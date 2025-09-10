# app/store.py
import json, sqlite3, time
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from app.crypto import gen_salt, derive_key, make_verifier, check_verifier, encrypt, decrypt

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS header (
  id INTEGER PRIMARY KEY CHECK (id=1),
  kdf_iter INTEGER NOT NULL,
  salt BLOB NOT NULL,
  verifier BLOB NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  display TEXT NOT NULL,    -- 목록 표시용(평문, 노출 감수)
  data   BLOB NOT NULL,     -- username/password/url/notes를 JSON으로 묶어 통암호화
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entries_display ON entries(display);
"""

class Vault:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.key: Optional[bytes] = None
        
    def lock(self):
        """메모리 내 키 제거"""
        self.key = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path, detect_types=0, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def init_db_if_needed(self):
        assert self.conn, "connect() 먼저 호출"
        cur = self.conn.cursor()
        cur.executescript(SCHEMA)
        self.conn.commit()

    def is_initialized(self) -> bool:
        assert self.conn
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='header';")
        if not cur.fetchone():
            return False
        cur.execute("SELECT COUNT(*) AS c FROM header WHERE id=1;")
        return cur.fetchone()["c"] == 1

    def create_master(self, master_password: str, kdf_iter: int = 200_000):
        assert self.conn
        if self.is_initialized():
            raise RuntimeError("이미 초기화됨")
        salt = gen_salt()
        key = derive_key(master_password, salt, kdf_iter)
        verifier = make_verifier(key)
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO header(id, kdf_iter, salt, verifier, created_at) VALUES(1, ?, ?, ?, ?)",
            (kdf_iter, salt, verifier, now),
        )
        self.conn.commit()
        self.key = key

    def unlock(self, master_password: str) -> bool:
        """헤더 읽고 파라미터로 키 파생 → verifier 검증"""
        assert self.conn
        cur = self.conn.cursor()
        cur.execute("SELECT kdf_iter, salt, verifier FROM header WHERE id=1;")
        row = cur.fetchone()
        if not row:
            raise RuntimeError("헤더가 없습니다. 최초 실행에서 마스터를 생성하세요.")
        kdf_iter, salt, verifier = row["kdf_iter"], row["salt"], row["verifier"]
        key = derive_key(master_password, salt, kdf_iter)
        ok = check_verifier(key, verifier)
        if ok:
            self.key = key
        return ok

    # ---- CRUD ----
    def list_entries(self) -> List[Dict[str, Any]]:
        assert self.conn
        cur = self.conn.cursor()
        cur.execute("SELECT id, display, updated_at FROM entries ORDER BY updated_at DESC;")
        return [dict(row) for row in cur.fetchall()]

    def add_entry(self, display: str, fields: Dict[str, Any]) -> int:
        """fields: {'username':..., 'password':..., 'url':..., 'notes':...}"""
        assert self.conn and self.key
        plaintext = json.dumps(fields, ensure_ascii=False).encode("utf-8")
        blob = encrypt(self.key, plaintext, aad=display.encode("utf-8"))
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO entries(display, data, created_at, updated_at) VALUES(?,?,?,?)",
            (display, blob, now, now),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_entry(self, entry_id: int) -> Tuple[str, Dict[str, Any]]:
        assert self.conn and self.key
        cur = self.conn.cursor()
        cur.execute("SELECT display, data FROM entries WHERE id=?;", (entry_id,))
        row = cur.fetchone()
        if not row:
            raise KeyError(f"id={entry_id} 없음")
        display = row["display"]
        data = decrypt(self.key, row["data"], aad=display.encode("utf-8"))
        return display, json.loads(data.decode("utf-8"))

    def update_entry(self, entry_id: int, new_display: str, fields: Dict[str, Any]):
        assert self.conn and self.key
        plaintext = json.dumps(fields, ensure_ascii=False).encode("utf-8")
        blob = encrypt(self.key, plaintext, aad=new_display.encode("utf-8"))
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE entries SET display=?, data=?, updated_at=? WHERE id=?",
            (new_display, blob, now, entry_id),
        )
        self.conn.commit()

    def delete_entry(self, entry_id: int):
        assert self.conn
        cur = self.conn.cursor()
        cur.execute("DELETE FROM entries WHERE id=?;", (entry_id,))
        self.conn.commit()

    def search_entries(self, keyword: str):
        """display 컬럼 LIKE 검색 (대소문자 구분 X는 SQLite collation 설정 필요하므로 우선 단순 LIKE)"""
        assert self.conn
        kw = f"%{keyword}%"
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, display, updated_at FROM entries WHERE display LIKE ? ORDER BY updated_at DESC;",
            (kw,),
        )
        return [dict(row) for row in cur.fetchall()]