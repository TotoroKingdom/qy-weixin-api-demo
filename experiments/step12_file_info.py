"""
步骤12：企业微信微盘获取文件信息

接口:
wedrive/file_info

功能:
获取指定文件详细信息
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
    "step12_file_info.json"
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



def get_file_info(
        access_token: str,
        fileid: str,
):

    """
    获取文件信息。

    参数:
        fileid:
            微盘文件ID
    """


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_info",
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



def run(
        fileid: str,
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 获取文件信息"
    )


    result = get_file_info(
        access_token,
        fileid,
    )


    payload = {
        "experiment":
            "step12_file_info",

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


    # 替换为实际文件fileid

    FILE_ID = (
        "s.ww48d00dd0cf1b78b0.788838296QBO_f.7888548578K4W"
    )


    result = run(
        FILE_ID
    )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )