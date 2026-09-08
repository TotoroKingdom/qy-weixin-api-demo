"""
步骤10：企业微信微盘文件移动

接口:
wedrive/file_move

功能:
将文件/文件夹移动到指定目录
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
    "step10_file_move.json"
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



def move_file(
        access_token: str,
        fatherid: str,
        fileids: list,
        replace: bool = False,
):

    """
    移动文件到指定目录。

    参数:
        fatherid:
            目标目录fileid

        fileids:
            要移动的文件fileid列表

        replace:
            是否覆盖同名文件
    """


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_move",
        params={
            "access_token": access_token,
        },
        json={
            "fatherid": fatherid,
            "replace": replace,
            "fileid": fileids,
        },
    )


    result = response.json()


    if result.get("errcode") != 0:
        raise RuntimeError(result)


    return result



def run(
        fatherid: str,
        fileids: list,
        replace: bool = False,
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 移动文件"
    )


    result = move_file(
        access_token,
        fatherid,
        fileids,
        replace,
    )


    payload = {
        "experiment":
            "step10_file_move",

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


    # 目标目录fileid
    TARGET_FOLDER_ID = (
        "s.ww48d00dd0cf1b78b0.788838296QBO_d.788868055JRHv"
    )


    # 待移动文件列表
    FILE_IDS = [
        "s.ww48d00dd0cf1b78b0.788838296QBO_f.7888548578K4W",
        "s.ww48d00dd0cf1b78b0.788838296QBO_f.7888670416Wi3",
    ]


    result = run(
        fatherid=TARGET_FOLDER_ID,
        fileids=FILE_IDS,
        replace=False,
    )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )