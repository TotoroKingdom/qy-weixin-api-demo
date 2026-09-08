"""步骤 07：企业微信微盘分块上传（无需编译，使用 OpenSSL 原生 SHA1）。

运行：python experiments/step07_file_chunk_upload.py <文件路径> --workers 10
凭据和目标目录读取 config.settings / .env；未配置文件夹时上传到空间根目录。
自动查找 Python 自带或系统 OpenSSL；也可用 --openssl-lib 指定 libcrypto 绝对路径。
仅分块和获取 token 的瞬时失败自动重试；init/finish 不盲目重试，避免重复创建文件。
请勿在计算摘要或上传期间修改源文件。HTTP 超时沿用 utils.http_client。

协议：https://developer.work.weixin.qq.com/document/path/98004
状态格式参照：https://github.com/wecomopen/file_block_digest
"""

from __future__ import annotations

import argparse
import base64
import ctypes
import ctypes.util
import json
import os
from pathlib import Path
import random
import struct
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 同时支持直接执行脚本和 python -m experiments.step07_file_chunk_upload。
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from requests.exceptions import RequestException

from config import settings
from utils import http_client

BLOCK_SIZE = 2 * 1024 * 1024
MAX_FILE_SIZE = 20 * 1024**3
MAX_WORKERS = 10
OUTPUT_FILE = settings.PROJECT_ROOT / "output" / "step07_file_chunk_upload.json"
# PyCharm 直接点击运行时使用的默认文件路径：可在这里修改。
UPLOAD_FILE = Path(r"E:\qy-weixin-api-demo\docs\history.md")


class UploadError(RuntimeError):
    """可安全显示的上传错误，不包含令牌、上传凭证或响应正文。"""


class _SHAContext(ctypes.Structure):
    # OpenSSL include/openssl/sha.h: SHA_LONG = unsigned int (32 位)。
    _fields_ = [
        ("h", ctypes.c_uint32 * 5),
        ("Nl", ctypes.c_uint32),
        ("Nh", ctypes.c_uint32),
        ("data", ctypes.c_uint32 * 16),
        ("num", ctypes.c_uint),
    ]


def _crypto_candidates(explicit: str | None):
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_absolute() or not path.is_file():
            raise UploadError("--openssl-lib 必须是现有 libcrypto 动态库的绝对路径")
        yield str(path)
        return

    # 优先使用解释器安装目录中的库，不从工作目录搜寻 DLL。
    root = Path(sys.base_prefix)
    directories = [root / "DLLs", root / "Library" / "bin", root / "lib", root]
    try:
        import _ssl
        directories.insert(0, Path(_ssl.__file__).resolve().parent)
    except ImportError:
        pass
    for directory in dict.fromkeys(directories):
        for pattern in ("libcrypto*.dll", "libcrypto.so*", "libcrypto*.dylib"):
            yield from (str(p) for p in sorted(directory.glob(pattern)))
    name = ctypes.util.find_library("crypto")
    if name:
        yield name


class NativeSHA1:
    """ctypes 调用 C SHA1；没有 Python SHA1 压缩轮函数或逐字节循环。"""

    def __init__(self, library: str | None = None):
        if ctypes.sizeof(_SHAContext) != 96:
            raise UploadError("当前平台的 SHA_CTX 布局不受支持")
        for candidate in dict.fromkeys(_crypto_candidates(library)):
            try:
                lib = ctypes.CDLL(candidate)
                lib.SHA1_Init.argtypes = [ctypes.POINTER(_SHAContext)]
                lib.SHA1_Update.argtypes = [
                    ctypes.POINTER(_SHAContext), ctypes.c_void_p, ctypes.c_size_t
                ]
                lib.SHA1_Final.argtypes = [
                    ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(_SHAContext)
                ]
                for name in ("SHA1_Init", "SHA1_Update", "SHA1_Final"):
                    getattr(lib, name).restype = ctypes.c_int
                self.lib = lib
                self.context = _SHAContext()
                self._init()
                self.update(b"abc")
                if self.final() != "a9993e364706816aba3e25717850c26c9cd0d89d":
                    continue
                self._init()
                return
            except (OSError, AttributeError, UploadError):
                continue
        raise UploadError(
            "找不到兼容且导出 SHA1_Init/Update/Final 的 OpenSSL libcrypto。"
            "请安装与 Python 位数一致的 OpenSSL，或使用 --openssl-lib 指定动态库；"
            "不会回退到纯 Python SHA1。"
        )

    def _init(self):
        if self.lib.SHA1_Init(ctypes.byref(self.context)) != 1:
            raise UploadError("OpenSSL SHA1_Init 失败")

    def update(self, data: bytes):
        if self.lib.SHA1_Update(ctypes.byref(self.context), data, len(data)) != 1:
            raise UploadError("OpenSSL SHA1_Update 失败")

    def state(self) -> str:
        if self.context.num != 0:
            raise UploadError("非末块 SHA1 状态必须位于 64 字节边界")
        # 官方 C++ 示例取 h0..h4 的内存字节，而非按大端拼接五个整数。
        # 显式小端序复现官方 x86 样例；这里不能使用每块独立 digest()。
        return struct.pack("<5I", *self.context.h).hex()

    def final(self) -> str:
        digest = (ctypes.c_ubyte * 20)()
        if self.lib.SHA1_Final(digest, ctypes.byref(self.context)) != 1:
            raise UploadError("OpenSSL SHA1_Final 失败")
        return bytes(digest).hex()


def _signature(stat):
    # Windows 的 stat/fstat 对 ctime 的含义可能不同，不能用它跨句柄比较。
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)


def _check_file(stat, expected):
    if _signature(stat) != expected:
        raise UploadError("源文件已改变，已停止上传；请保持文件不变后重新运行")


def calculate_block_sha(file_path: Path, library: str | None = None) -> tuple[list[str], tuple]:
    """单次顺序读文件，内存 O(2MB)；末块即使恰好 2MB 也必须 final。"""
    sha = NativeSHA1(library)
    result = []
    with file_path.open("rb") as source:
        stat = os.fstat(source.fileno())
        expected = _signature(stat)
        if not 0 < stat.st_size <= MAX_FILE_SIZE:
            raise UploadError("分块上传仅支持非空、大小不超过 20 GiB 的文件")
        remaining = stat.st_size
        while remaining:
            block = source.read(min(BLOCK_SIZE, remaining))
            if len(block) != min(BLOCK_SIZE, remaining):
                raise UploadError("读取源文件不完整，已停止上传")
            remaining -= len(block)
            sha.update(block)
            result.append(sha.state() if remaining else sha.final())
        _check_file(os.fstat(source.fileno()), expected)
    _check_file(file_path.stat(), expected)
    return result, expected


def _request(method: str, endpoint: str, *, params: dict, body: dict | None = None,
             retries: int = 0, stop: threading.Event | None = None) -> dict:
    """重试瞬时网络/服务错误；永久业务错误立即停止。隐藏含凭据的 URL。"""
    for attempt in range(retries + 1):
        if stop is not None and stop.is_set():
            raise UploadError("上传已取消")
        retryable = False
        response = None
        try:
            url = f"{settings.WEWORK_API_BASE_URL.rstrip('/')}/{endpoint}"
            if method == "GET":
                response = http_client.get(url, params=params)
            else:
                response = http_client.post(url, params=params, json=body)
            status = response.status_code
            if not 200 <= status < 300:
                retryable = status in (408, 429) or 500 <= status < 600
                error = f"{endpoint}: HTTP {status}"
            else:
                try:
                    data = response.json()
                except ValueError:
                    data = None
                if not isinstance(data, dict) or "errcode" not in data:
                    retryable = True
                    error = f"{endpoint}: 响应不是有效的企业微信 JSON"
                elif data["errcode"] == 0:
                    return data
                else:
                    code = data["errcode"]
                    retryable = code in (-1, 45009, 45011)
                    # 不直接输出服务端正文，避免回显敏感内容。
                    error = f"{endpoint}: errcode={code}" if isinstance(code, int) else (
                        f"{endpoint}: errcode 格式错误"
                    )
        except RequestException as exc:
            retryable = True
            error = f"{endpoint}: 网络请求失败（{type(exc).__name__}）"
        finally:
            if response is not None:
                response.close()
        if not retryable or attempt == retries:
            if retryable and endpoint.endswith(("file_upload_init", "file_upload_finish")):
                error += "；服务端结果可能已生效，请先核对微盘，避免重复创建"
            raise UploadError(error)
        delay = min(2**attempt, 30) + random.uniform(0, 0.25)
        part = f" 分块 {body['index']}" if body and "index" in body else ""
        print(f"{endpoint}{part} 失败，{delay:.1f}s 后重试 {attempt + 1}/{retries}",
              file=sys.stderr, flush=True)
        if stop is None:
            time.sleep(delay)
        elif stop.wait(delay):
            raise UploadError("上传已取消")
    raise AssertionError("unreachable")


def _upload_parts(file_path: Path, expected: tuple, token: str, upload_key: str,
                  count: int, workers: int, retries: int):
    stop = threading.Event()
    size = expected[2]

    def upload(index: int) -> int:
        if stop.is_set():
            raise UploadError("上传已取消")
        # 每个线程独立文件句柄，避免并发 seek/read 互相覆盖。
        with file_path.open("rb") as source:
            _check_file(os.fstat(source.fileno()), expected)
            offset = (index - 1) * BLOCK_SIZE
            source.seek(offset)
            block = source.read(min(BLOCK_SIZE, size - offset))
            _check_file(os.fstat(source.fileno()), expected)
        if len(block) != min(BLOCK_SIZE, size - offset):
            raise UploadError(f"分块 {index} 读取不完整")
        _request("POST", "wedrive/file_upload_part", params={"access_token": token},
                 body={"upload_key": upload_key, "index": index,
                       "file_base64_content": base64.b64encode(block).decode("ascii")},
                 retries=retries, stop=stop)
        return len(block)

    pool = ThreadPoolExecutor(max_workers=min(workers, count))
    completed_bytes = completed_parts = 0
    started = time.perf_counter()
    print(f"上传进度：0/{count} 块，0.0%", file=sys.stderr, flush=True)
    try:
        futures = [pool.submit(upload, index) for index in range(1, count + 1)]
        for future in as_completed(futures):
            completed_bytes += future.result()
            completed_parts += 1
            elapsed = max(time.perf_counter() - started, 0.001)
            print(f"上传进度：{completed_parts}/{count} 块，"
                  f"{completed_bytes / size:.1%}，"
                  f"{completed_bytes / 1024**2:.2f}/{size / 1024**2:.2f} MiB，"
                  f"{completed_bytes / 1024**2 / elapsed:.2f} MiB/s",
                  file=sys.stderr, flush=True)
    finally:
        stop.set()
        pool.shutdown(wait=True, cancel_futures=True)
    _check_file(file_path.stat(), expected)


def run(file_path: str | Path, *, workers: int = MAX_WORKERS, retries: int = 3,
        openssl_lib: str | None = None) -> dict:
    """上传一个文件；仅全部块成功才 finish，保存不含凭据的结果。"""
    try:
        if not 1 <= workers <= MAX_WORKERS:
            raise UploadError("workers 必须在 1 到 10 之间")
        if not 0 <= retries <= 10:
            raise UploadError("retries 必须在 0 到 10 之间（不含首次请求）")
        if not settings.CORP_ID or not settings.CORP_SECRET:
            raise UploadError("请在 .env 中配置 CORP_ID 和 CORP_SECRET")
        if not settings.WEDRIVE_SPACE_ID:
            raise UploadError("请在 .env 中配置 WEDRIVE_SPACE_ID")
        path = Path(file_path).expanduser().resolve()
        if not path.is_file():
            raise UploadError(f"文件不存在或不是普通文件：{path}")
        print("计算 2 MiB 分块累积 SHA1（OpenSSL）…", file=sys.stderr, flush=True)
        started = time.perf_counter()
        hashes, expected = calculate_block_sha(path, openssl_lib)
        hash_seconds = time.perf_counter() - started
        print(f"摘要计算完成：{len(hashes)} 块，耗时 {hash_seconds:.3f}s",
              file=sys.stderr, flush=True)
        auth = _request("GET", "gettoken", retries=retries, params={
            "corpid": settings.CORP_ID, "corpsecret": settings.CORP_SECRET,
        })
        token = auth.get("access_token")
        if not isinstance(token, str) or not token:
            raise UploadError("获取 access_token 失败：响应缺少有效 token")
        _check_file(path.stat(), expected)
        started = time.perf_counter()
        init = _request("POST", "wedrive/file_upload_init", params={"access_token": token},
                        body={"spaceid": settings.WEDRIVE_SPACE_ID,
                              "fatherid": settings.WEDRIVE_FOLDER_ID or settings.WEDRIVE_SPACE_ID,
                              "file_name": path.name, "size": expected[2], "block_sha": hashes})
        hit_exist = init.get("hit_exist")
        if hit_exist is True:
            fileid = init.get("fileid")
            print("已命中秒传，无需上传分块。", file=sys.stderr, flush=True)
        elif hit_exist is False:
            upload_key = init.get("upload_key")
            if not isinstance(upload_key, str) or not upload_key:
                raise UploadError("初始化成功但缺少 upload_key，无法继续")
            _upload_parts(path, expected, token, upload_key, len(hashes), workers, retries)
            finish = _request("POST", "wedrive/file_upload_finish",
                              params={"access_token": token}, body={"upload_key": upload_key})
            fileid = finish.get("fileid")
        else:
            raise UploadError("初始化响应缺少有效 hit_exist，无法判断上传状态")
        if not isinstance(fileid, str) or not fileid:
            raise UploadError("完成响应缺少 fileid；请核对微盘中的文件状态")
        result = {"ok": True, "fileid": fileid, "hit_exist": hit_exist,
                  "size": expected[2], "blocks": len(hashes),
                  "hash_seconds": round(hash_seconds, 3),
                  "upload_seconds": round(time.perf_counter() - started, 3)}
    except (UploadError, OSError, ValueError) as exc:
        result = {"ok": False, "message": str(exc)}
    payload = {"experiment": "step07_file_chunk_upload",
               "created_at": datetime.now().astimezone().isoformat(), "result": result}
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "file", nargs="?", type=Path, default=UPLOAD_FILE,
        help=f"待上传文件的路径（默认：{UPLOAD_FILE}）",
    )
    parser.add_argument("--workers", type=int, choices=range(1, MAX_WORKERS + 1), default=MAX_WORKERS,
                        help="并发线程数，默认 10，最多 10")
    parser.add_argument("--retries", type=int, choices=range(0, 11), default=3,
                        help="分块瞬时失败的额外重试次数，默认 3")
    parser.add_argument("--openssl-lib", help="OpenSSL libcrypto 动态库的绝对路径（可选）")
    args = parser.parse_args()
    try:
        print(f"待上传文件：{Path(args.file).resolve()}", file=sys.stderr, flush=True)
        payload = run(args.file, workers=args.workers, retries=args.retries, openssl_lib=args.openssl_lib)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["result"]["ok"] else 1
    except KeyboardInterrupt:
        print("已取消；未完成的上传不会被标记为成功。", file=sys.stderr)
        return 130
    except OSError as exc:
        print(f"无法保存结果：{type(exc).__name__}；请核对微盘中的文件状态。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


