"""
步骤08：企业微信微盘新建文件夹/文档

接口：
wedrive/file_create

file_type:
1: 文件夹
3: 文档
4: 表格
"""

import json
from datetime import datetime

from config.settings import (
    CORP_ID,
    CORP_SECRET,
    PROJECT_ROOT,
    WEDRIVE_SPACE_ID,
    WEDRIVE_FOLDER_ID,
    WEWORK_API_BASE_URL,
)

from utils.http_client import get, post


OUTPUT_FILE = (
    PROJECT_ROOT /
    "output" /
    "step08_file_create.json"
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



def create_file(
        access_token: str,
        file_name: str,
        file_type: int,
        space_id: str = None,
        father_id: str = None,
):

    """
    新建微盘文件/文件夹。

    file_type:
        1 文件夹
        3 文档
        4 表格
    """

    space_id = (
        space_id
        or
        WEDRIVE_SPACE_ID
    )


    father_id = (
        father_id
        or
        WEDRIVE_FOLDER_ID
        or
        space_id
    )


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_create",
        params={
            "access_token": access_token,
        },
        json={
            "spaceid": space_id,
            "fatherid": father_id,
            "file_type": file_type,
            "file_name": file_name,
        },
    )


    result = response.json()


    if result.get("errcode") != 0:
        raise RuntimeError(result)


    return result



def run(
        file_name: str,
        file_type: int
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 创建文件"
    )


    result = create_file(
        access_token,
        file_name,
        file_type,
    )


    payload = {
        "experiment":
            "step08_file_create",

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


    # 创建文件夹
    result = run(
        file_name="测试目录",
        file_type=1,
    )


    # 创建文档示例：
    #
    # result = run(
    #     file_name="测试文档",
    #     file_type=3,
    # )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )