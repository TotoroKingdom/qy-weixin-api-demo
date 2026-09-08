from pathlib import Path

from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

CORP_ID = os.getenv("CORP_ID", "")
CORP_SECRET = os.getenv("CORP_SECRET", "")

WEDRIVE_SPACE_ID = os.getenv(
    "WEDRIVE_SPACE_ID",
    ""
)

WEDRIVE_FOLDER_ID = os.getenv(
    "WEDRIVE_FOLDER_ID",
    ""
)

MOBILE = os.getenv(
    "MOBILE",
    ""
)
USER_ID = os.getenv(
    "USER_ID",
    ""
)

WEWORK_API_BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"
