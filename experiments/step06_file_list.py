"""步骤 02：获取企业微信微盘文件列表。"""

import json
from datetime import datetime

from requests import post

from config.settings import (
    PROJECT_ROOT,
    WEWORK_API_BASE_URL,
    WEDRIVE_SPACE_ID,
    WEDRIVE_FOLDER_ID,
)

from experiments.step01_auth import run as get_token
from utils.http_client import get


OUTPUT_FILE = PROJECT_ROOT / "output" / "step02_file_list.json"


def run() -> dict:
    """调用企业微信微盘文件列表接口。"""

    auth_result = get_token()

    token_result = auth_result["result"]

    if token_result.get("errcode") != 0:
        result = {
            "ok": False,
            "message": "获取access_token失败",
            "auth_result": token_result,
        }

    elif not WEDRIVE_SPACE_ID:
        result = {
            "ok": False,
            "message": (
                "缺少 WEDRIVE_SPACE_ID，请在 .env 中配置微盘空间ID"
            ),
        }

    else:

        params = {
            "access_token": token_result["access_token"],
        }

        body = {
            "spaceid": WEDRIVE_SPACE_ID,
            "fatherid": WEDRIVE_FOLDER_ID,
            "sort_type": 1,
            "start": 0,
            "limit": 50,
        }

        response = post(
            f"{WEWORK_API_BASE_URL}/wedrive/file_list",
            params=params,
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
        "experiment": "step02_file_list",
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