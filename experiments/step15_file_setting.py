"""
步骤15：企业微信微盘分享设置

接口:
wedrive/file_setting

功能:
设置文件分享范围和访问权限
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
    "step15_file_setting.json"
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



def set_file_setting(
        access_token: str,
        fileid: str,
        auth_scope: int,
        auth: int = None,
):

    """
    设置文件分享权限。

    auth_scope:
        1 指定人
        2 企业内
        3 企业外
        4 企业内需管理员审批
        5 企业外需管理员审批


    auth:
        1 仅浏览（可下载）
        4 仅预览
    """


    data = {
        "fileid": fileid,
        "auth_scope": auth_scope,
    }


    if auth is not None:
        data["auth"] = auth


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_setting",
        params={
            "access_token": access_token,
        },
        json=data,
    )


    result = response.json()


    if result.get("errcode") != 0:
        raise RuntimeError(result)


    return result



def run(
        fileid: str,
        auth_scope: int,
        auth: int = None,
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 设置分享权限"
    )


    result = set_file_setting(
        access_token,
        fileid,
        auth_scope,
        auth,
    )


    payload = {
        "experiment":
            "step15_file_setting",

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


    # 示例1：
    # 企业内可访问，仅浏览下载

    result = run(
        fileid=FILE_ID,
        auth_scope=2,
        auth=1,
    )


    # 示例2：
    # 企业外访问，仅预览
    #
    # result = run(
    #     fileid=FILE_ID,
    #     auth_scope=3,
    #     auth=4,
    # )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )