"""
步骤11：企业微信微盘删除文件

接口:
wedrive/file_delete

功能:
删除指定文件/文件夹
"""

import json
from datetime import datetime

from config.settings import (
    CORP_ID,
    CORP_SECRET,
    PROJECT_ROOT,
    WEWORK_API_BASE_URL,
)

from utils.http_client import get, post


OUTPUT_FILE = (
    PROJECT_ROOT /
    "output" /
    "step11_file_delete.json"
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



def delete_file(
        access_token: str,
        fileids: list,
):

    """
    删除微盘文件。

    参数:
        fileids:
            文件fileid列表
    """


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_delete",
        params={
            "access_token": access_token,
        },
        json={
            "fileid": fileids,
        },
    )


    result = response.json()


    if result.get("errcode") != 0:
        raise RuntimeError(result)


    return result



def run(
        fileids: list,
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 删除文件"
    )


    result = delete_file(
        access_token,
        fileids,
    )


    payload = {
        "experiment":
            "step11_file_delete",

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
        encoding="utf-8",
    )


    return payload



if __name__ == "__main__":


    # 要删除的文件ID列表
    FILE_IDS = [
        "s.ww48d00dd0cf1b78b0.788838296QBO_d.788868420lq8V"
    ]


    result = run(
        FILE_IDS
    )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )