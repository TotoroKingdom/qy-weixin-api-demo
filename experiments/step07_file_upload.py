"""步骤 07：上传文件到企业微信微盘。"""

import base64
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


OUTPUT_FILE = PROJECT_ROOT / "output" / "step07_file_upload.json"


UPLOAD_FILE = (
    PROJECT_ROOT / "test.md"
)


def encode_file(file_path):
    """
    文件转Base64
    """

    with open(
        file_path,
        "rb"
    ) as f:

        return base64.b64encode(
            f.read()
        ).decode("utf-8")



def run() -> dict:
    """
    调用企业微信微盘上传文件接口。
    """

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
                "缺少 WEDRIVE_SPACE_ID，请在 .env 配置"
            ),
        }


    elif not UPLOAD_FILE.exists():

        result = {
            "ok": False,
            "message": (
                f"上传文件不存在: {UPLOAD_FILE}"
            ),
        }


    else:

        file_size = UPLOAD_FILE.stat().st_size


        if file_size > 10 * 1024 * 1024:

            result = {
                "ok": False,
                "message": (
                    "文件超过10MB，请使用分块上传"
                ),
            }


        else:

            params = {
                "access_token":
                    token_result["access_token"],
            }


            body = {

                "spaceid":
                    WEDRIVE_SPACE_ID,

                "fatherid":
                    WEDRIVE_FOLDER_ID,

                "file_name":
                    UPLOAD_FILE.name,

                "file_base64_content":
                    encode_file(
                        UPLOAD_FILE
                    ),
            }


            response = post(

                f"{WEWORK_API_BASE_URL}/wedrive/file_upload",

                params=params,

                json=body,

            )


            try:

                result = response.json()


            except ValueError:

                result = {

                    "http_status":
                        response.status_code,

                    "response_text":
                        response.text,

                }



    payload = {

        "experiment":
            "step07_file_upload",

        "created_at":
            datetime.now()
            .astimezone()
            .isoformat(),

        "result":
            result,

    }



    OUTPUT_FILE.parent.mkdir(
        exist_ok=True
    )


    OUTPUT_FILE.write_text(

        json.dumps(

            payload,

            ensure_ascii=False,

            indent=2,

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