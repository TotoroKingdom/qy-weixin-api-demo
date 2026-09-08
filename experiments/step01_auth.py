"""步骤 01：获取企业微信 access_token。"""

import json
from datetime import datetime

from config.settings import CORP_ID, CORP_SECRET, PROJECT_ROOT, WEWORK_API_BASE_URL
from utils.http_client import get

OUTPUT_FILE = PROJECT_ROOT / "output" / "step01_auth.json"


def run() -> dict:
    """请求 access_token，并将结果保存到 output/step01_auth.json。"""
    if not CORP_ID or not CORP_SECRET:
        result = {
            "ok": False,
            "message": "请复制 .env.example 为 .env，并填写 CORP_ID 和 CORP_SECRET。",
        }
    else:
        response = get(
            f"{WEWORK_API_BASE_URL}/gettoken",
            params={"corpid": CORP_ID, "corpsecret": CORP_SECRET},
        )
        try:
            result = response.json()
        except ValueError:
            result = {"http_status": response.status_code, "response_text": response.text}

    payload = {
        "experiment": "step01_auth",
        "created_at": datetime.now().astimezone().isoformat(),
        "result": result,
    }
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
