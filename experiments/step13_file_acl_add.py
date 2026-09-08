"""
步骤13：企业微信微盘新增成员权限

接口:
wedrive/file_acl_add

功能:
给指定文件添加成员访问权限
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
    "step13_file_acl_add.json"
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



def add_acl(
        access_token: str,
        fileid: str,
        auth_info: list,
):

    """
    给文件新增成员权限。

    auth_info:

    个人:
    {
        "type":1,
        "userid":"USERID",
        "auth":1
    }


    部门:
    {
        "type":2,
        "departmentid":1,
        "auth":1
    }
    """


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_acl_add",
        params={
            "access_token": access_token,
        },
        json={
            "fileid": fileid,
            "auth_info": auth_info,
        },
    )


    result = response.json()


    if result.get("errcode") != 0:
        raise RuntimeError(result)


    return result



def run(
        fileid: str,
        auth_info: list,
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 新增成员权限"
    )


    result = add_acl(
        access_token,
        fileid,
        auth_info,
    )


    payload = {
        "experiment":
            "step13_file_acl_add",

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


    # 添加权限示例

    AUTH_INFO = [

        # 添加个人成员
        {
            "type": 1,
            "userid": "13415152421",
            "auth": 1,
        },


    ]


    result = run(
        FILE_ID,
        AUTH_INFO,
    )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )