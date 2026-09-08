"""
步骤17：企业微信微盘修改文件安全设置

接口:
wedrive/file_secure_setting

说明:
仅支持在线文档类型。
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
    "step17_file_secure_setting.json"
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



def set_file_secure_setting(
        access_token: str,
        fileid: str,
        watermark: dict,
):

    """
    修改文件安全设置。

    watermark:

    {
        "text": "水印文字",
        "margin_type": 1,
        "show_visitor_name": True,
        "show_text": True
    }


    参数说明:

    text:
        水印文字

    margin_type:
        1 低密度水印
        2 高密度水印

    show_visitor_name:
        是否显示访问人名称

    show_text:
        是否展示水印文本
    """


    response = post(
        f"{WEWORK_API_BASE_URL}/wedrive/file_secure_setting",
        params={
            "access_token": access_token,
        },
        json={
            "fileid": fileid,
            "watermark": watermark,
        },
    )


    result = response.json()


    if result.get("errcode") != 0:
        raise RuntimeError(result)


    return result



def run(
        fileid: str,
        watermark: dict,
):

    print(
        "1. 获取access_token"
    )


    access_token = get_access_token()


    print(
        "2. 修改文件安全设置"
    )


    result = set_file_secure_setting(
        access_token,
        fileid,
        watermark,
    )


    payload = {
        "experiment":
            "step17_file_secure_setting",

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


    FILE_ID = (
        "s.ww48d00dd0cf1b78b0.788838296QBO_f.7888548578K4W"
    )


    WATERMARK = {

        # 水印文字
        "text": "企业内部资料",


        # 1低密度 2高密度
        "margin_type": 2,


        # 是否显示访问人名称
        "show_visitor_name": True,


        # 是否展示水印文本
        "show_text": True,

    }


    result = run(
        FILE_ID,
        WATERMARK,
    )


    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )