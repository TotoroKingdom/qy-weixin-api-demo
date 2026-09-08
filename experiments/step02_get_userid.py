"""步骤 02：通过手机号获取企业微信 userid。"""

import json
from datetime import datetime

from config.settings import (
    PROJECT_ROOT,
    WEWORK_API_BASE_URL,
    MOBILE
)

from experiments.step01_auth import run as get_token
from utils.http_client import post


OUTPUT_FILE = PROJECT_ROOT / "output" / "step02_get_userid.json"


def run() -> dict:
    """通过手机号获取企业微信 userid。"""

    # 1. 获取 access_token
    auth_result = get_token()

    token_result = auth_result["result"]


    MOBILE: str = "13415152421"

    if token_result.get("errcode") != 0:
        result = {
            "ok": False,
            "message": "获取 access_token 失败",
            "auth_result": token_result,
        }


    elif not MOBILE:
        result = {
            "ok": False,
            "message": "请在 .env 中配置 MOBILE",
        }

    else:
        access_token = token_result["access_token"]

        # 2. 调用手机号获取 userid 接口
        response = post(
            f"{WEWORK_API_BASE_URL}/user/getuserid",
            params={
                "access_token": access_token
            },
            json={
                "mobile": MOBILE
            },
        )

        try:
            result = response.json()

        except ValueError:
            result = {
                "http_status": response.status_code,
                "response_text": response.text,
            }


    payload = {
        "experiment": "step02_get_userid",
        "created_at": datetime.now().astimezone().isoformat(),
        "result": result,
    }


    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            run(),
            ensure_ascii=False,
            indent=2
        )
    )