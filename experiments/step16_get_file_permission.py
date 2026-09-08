"""
步骤16：企业微信微盘获取文件权限信息

接口:
wedrive/get_file_permission

功能:
获取指定文件的权限配置
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
    "step16_get_file_permission.json"
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



def get_file_permission(
        access_token: str,
        fileid: str,
):

    """
    获取文件权限信息。

    返回:
    - share_range
    - secure_setting
    - inherit_father_auth
    - file_member_list
    - watermark
    """


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/get_file_permission",
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
        "2. 获取文件权限信息"
    )


    result = get_file_permission(
        access_token,
        fileid,
    )


    payload = {
        "experiment":
            "step16_get_file_permission",

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


    # 文件fileid
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