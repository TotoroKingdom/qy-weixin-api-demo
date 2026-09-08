"""步骤 02：创建企业微信微盘空间。"""

import json
from datetime import datetime

from config.settings import (
    PROJECT_ROOT,
    WEWORK_API_BASE_URL,
)

from experiments.step01_auth import run as get_token
from utils.http_client import post


OUTPUT_FILE = PROJECT_ROOT / "output" / "step02_create_space.json"


def run() -> dict:
    """调用企业微信微盘接口创建空间。"""

    # 1. 获取 access_token
    auth_result = get_token()

    token_result = auth_result["result"]

    if token_result.get("errcode") != 0:
        result = {
            "ok": False,
            "message": "获取 access_token 失败",
            "auth_result": token_result,
        }

    else:
        access_token = token_result["access_token"]

        # 2. 创建空间请求参数
        payload = {
            "space_name": "API测试空间",
            "space_sub_type": 0
        }

        # 3. 调用微盘创建空间接口
        response = post(
            f"{WEWORK_API_BASE_URL}/wedrive/space_create",
            params={
                "access_token": access_token
            },
            json=payload,
        )

        try:
            result = response.json()

        except ValueError:
            result = {
                "http_status": response.status_code,
                "response_text": response.text,
            }


    output = {
        "experiment": "step02_create_space",
        "created_at": datetime.now().astimezone().isoformat(),
        "result": result,
    }


    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    return output


if __name__ == "__main__":
    print(
        json.dumps(
            run(),
            ensure_ascii=False,
            indent=2
        )
    )