"""步骤 04：给微盘空间添加成员权限。"""

import json
from datetime import datetime

from config.settings import (
    PROJECT_ROOT,
    WEWORK_API_BASE_URL,
    WEDRIVE_SPACE_ID,
    USER_ID,
)

from experiments.step01_auth import run as get_token
from utils.http_client import post


OUTPUT_FILE = PROJECT_ROOT / "output" / "step04_add_space_member.json"


def run() -> dict:
    """调用企业微信微盘接口添加空间成员。"""

    # 1. 获取 access_token
    auth_result = get_token()

    token_result = auth_result["result"]

    if token_result.get("errcode") != 0:
        result = {
            "ok": False,
            "message": "获取 access_token 失败",
            "auth_result": token_result,
        }

    elif not WEDRIVE_SPACE_ID:
        result = {
            "ok": False,
            "message": "请配置 WEDRIVE_SPACE_ID",
        }

    elif not USER_ID:
        result = {
            "ok": False,
            "message": "请配置 USER_ID",
        }

    else:

        access_token = token_result["access_token"]

        # 2. 添加空间成员
        body = {
            "spaceid": WEDRIVE_SPACE_ID,
            "auth_info": [
                {
                    "type": 1,
                    "userid": USER_ID,
                    "auth": 7
                }
            ]
        }

        response = post(
            f"{WEWORK_API_BASE_URL}/wedrive/space_acl_add",
            params={
                "access_token": access_token
            },
            json=body,
        )

        try:
            result = response.json()

        except ValueError:
            result = {
                "http_status": response.status_code,
                "response_text": response.text,
            }


    payload = {
        "experiment": "step04_add_space_member",
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