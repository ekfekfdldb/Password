# app/utils.py
import os, sys, json
from pathlib import Path

APP_NAME = "MyVault"

def get_appdata_dir() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home() / ".config")
    p = Path(base) / APP_NAME
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_db_path() -> Path:
    return get_appdata_dir() / "vault.db"

def json_prompt_defaults() -> dict:
    return {"username": "", "password": "", "url": "", "notes": ""}

def resource_path(rel_path: str) -> str:
    # PyInstaller 대응
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return str(Path(base) / rel_path)
    return rel_path

AUTO_LOCK_MIN = 5           # 자동 잠금 분 (원하면 UI에서 바꾸게 확장 가능)
CLIPBOARD_CLEAR_SEC = 20    # 복사 후 자동 삭제 초

def try_icon(root):
    # Windows .ico가 있으면 창 아이콘 지정
    ico = resource_path("icon.ico")
    if Path(ico).exists():
        try:
            root.iconbitmap(ico)
        except Exception:
            pass