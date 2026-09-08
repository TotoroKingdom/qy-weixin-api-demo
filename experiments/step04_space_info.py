"""步骤 03：获取企业微信微盘空间信息。"""

import json
from datetime import datetime

from config.settings import (
    PROJECT_ROOT,
    WEWORK_API_BASE_URL,
    WEDRIVE_SPACE_ID,
)

from experiments.step01_auth import run as get_token
from utils.http_client import post


OUTPUT_FILE = PROJECT_ROOT / "output" / "step03_space_info.json"


def run() -> dict:
    """调用企业微信微盘接口获取空间信息。"""

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
            "message": "请在 .env 中配置 WEDRIVE_SPACE_ID",
        }

    else:
        access_token = token_result["access_token"]

        # 2. 调用获取空间信息接口
        response = post(
            f"{WEWORK_API_BASE_URL}/wedrive/space_info",
            params={
                "access_token": access_token
            },
            json={
                "spaceid": WEDRIVE_SPACE_ID
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
        "experiment": "step03_space_info",
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