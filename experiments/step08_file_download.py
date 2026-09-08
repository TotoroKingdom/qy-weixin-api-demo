"""
步骤08：企业微信微盘文件下载

流程：

1. 获取 access_token
2. 调用 file_download 获取下载地址
3. 携带 cookie 下载文件
4. 保存到 output/docs
"""

import json
from pathlib import Path

import requests

from config.settings import (
    CORP_ID,
    CORP_SECRET,
    PROJECT_ROOT,
    WEWORK_API_BASE_URL,
)

from utils.http_client import get, post


OUTPUT_DIR = Path(
    r"E:\qy-weixin-api-demo\output\docs"
)


def get_access_token():

    response = get(
        f"{WEWORK_API_BASE_URL}/gettoken",
        params={
            "corpid": CORP_ID,
            "corpsecret": CORP_SECRET,
        },
    )

    result = response.json()

    if result.get("errcode") != 0:
        raise RuntimeError(result)

    return result["access_token"]



def get_download_url(
        access_token: str,
        fileid: str
):

    """
    获取文件下载地址
    """

    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_download",
        params={
            "access_token": access_token,
        },
        json={
            "fileid": fileid,
        },
    )


    result = response.json()


    if result.get("errcode") != 0:
        raise RuntimeError(result)


    return result



def download_file(
        download_url: str,
        cookie_name: str,
        cookie_value: str,
        save_path: Path
):

    """
    下载实际文件
    """

    print(
        f"开始下载: {save_path.name}"
    )


    cookies = {
        cookie_name: cookie_value
    }


    response = requests.get(
        download_url,
        cookies=cookies,
        stream=True,
        timeout=120,
    )


    response.raise_for_status()


    save_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    total = 0


    with save_path.open(
        "wb"
    ) as file:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):

            if chunk:

                file.write(chunk)

                total += len(chunk)


                print(
                    f"已下载: "
                    f"{total / 1024 / 1024:.2f} MB"
                )


    print(
        "下载完成:",
        save_path
    )



def run(
        fileid: str,
        file_name: str
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 获取下载地址"
    )


    download_info = get_download_url(
        access_token,
        fileid
    )


    print(
        json.dumps(
            download_info,
            ensure_ascii=False,
            indent=2
        )
    )


    save_path = (
        OUTPUT_DIR /
        file_name
    )


    print(
        "3. 开始下载"
    )


    download_file(
        download_info["download_url"],
        download_info["cookie_name"],
        download_info["cookie_value"],
        save_path,
    )


    return {
        "fileid": fileid,
        "save_path": str(save_path),
    }



if __name__ == "__main__":


    # 替换成 step07 上传成功返回的 fileid

    FILE_ID = (
        "s.ww48d00dd0cf1b78b0.788838296QBO_f.7888670416Wi3"
    )


    FILE_NAME = (
        "history.md"
    )


    result = run(
        FILE_ID,
        FILE_NAME
    )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )