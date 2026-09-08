"""
步骤19：企业微信微盘文件变更事件回调

事件:
wedrive_file_change

变更类型:
create_file
rename_file
update_file
delete_file
move_file
"""

import json
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from flask import Flask, request


app = Flask(__name__)


OUTPUT_FILE = Path(
    "./output/step19_wedrive_file_change.json"
)



def parse_xml(xml_data: str):

    root = ET.fromstring(xml_data)


    result = {}


    for child in root:

        result[child.tag] = child.text


    return result



def save_event(event):

    OUTPUT_FILE.parent.mkdir(
        exist_ok=True
    )


    OUTPUT_FILE.write_text(
        json.dumps(
            {
                "created_at":
                    datetime.now()
                    .astimezone()
                    .isoformat(),

                "event":
                    event,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )



@app.route(
    "/wechat/callback",
    methods=["POST"]
)
def callback():


    xml_data = (
        request.data
        .decode("utf-8")
    )


    print(
        "收到微盘文件变更事件:"
    )

    print(xml_data)


    event = parse_xml(
        xml_data
    )


    if (
        event.get("Event")
        ==
        "wedrive_file_change"
    ):

        change_type = (
            event.get(
                "ChangeType"
            )
        )


        file_ids = []


        # FileId可能多个
        for item in event:

            if item == "FileId":

                file_ids.append(
                    event[item]
                )


        result = {

            "event":
                "wedrive_file_change",

            "change_type":
                change_type,

            "file_ids":
                file_ids,
        }


    else:

        result = {
            "event":
                "unknown",

            "raw":
                event,
        }



    save_event(
        result
    )


    return "success"



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
    )