"""
步骤14：企业微信微盘删除成员权限

接口:
wedrive/file_acl_del

功能:
删除指定文件的成员访问权限
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
    "step14_file_acl_del.json"
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



def delete_acl(
        access_token: str,
        fileid: str,
        auth_info: list,
):

    """
    删除文件成员权限。

    auth_info:

    删除个人:
    {
        "type": 1,
        "userid": "USERID1"
    }


    删除部门:
    {
        "type": 2,
        "departmentid": 1
    }
    """


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_acl_del",
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
        "2. 删除成员权限"
    )


    result = delete_acl(
        access_token,
        fileid,
        auth_info,
    )


    payload = {
        "experiment":
            "step14_file_acl_del",

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


    # 删除成员示例

    AUTH_INFO = [

        # 删除个人成员
        {
            "type": 1,
            "userid": "13415152421",
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