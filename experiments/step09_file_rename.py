"""
步骤09：企业微信微盘文件重命名

接口:
wedrive/file_rename
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
    "step09_file_rename.json"
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



def rename_file(
        access_token: str,
        fileid: str,
        new_name: str,
):

    """
    重命名微盘文件。
    """


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_rename",
        params={
            "access_token": access_token,
        },
        json={
            "fileid": fileid,
            "new_name": new_name,
        },
    )


    result = response.json()


    if result.get("errcode") != 0:
        raise RuntimeError(result)


    return result



def run(
        fileid: str,
        new_name: str,
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 重命名文件"
    )


    result = rename_file(
        access_token,
        fileid,
        new_name,
    )


    payload = {
        "experiment":
            "step09_file_rename",

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


    # 修改为实际文件fileid

    FILE_ID = (
        "s.ww48d00dd0cf1b78b0.788838296QBO_d.788868055JRHv"
    )


    NEW_NAME = (
        "测试文件-改名测试"
    )


    result = run(
        FILE_ID,
        NEW_NAME,
    )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )