import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "users.db"


class UserStore:

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def user_exists(self, user_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone() is not None

    def create_user(self, user_id: int, password: str, email: str = "") -> bool:
        if self.user_exists(user_id):
            return False
        cursor = self.conn.cursor()
        password_hash = self._hash_password(password)
        cursor.execute(
            "INSERT INTO users (user_id, password_hash, email, created_at) VALUES (?, ?, ?, ?)",
            (user_id, password_hash, email.strip(), datetime.utcnow().isoformat())
        )
        self.conn.commit()
        return True

    def verify_user(self, user_id: int, password: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        return row["password_hash"] == self._hash_password(password)

    def log_interaction(self, user_id: int, action: str, details: str = ""):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO interactions (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
            (user_id, action, details[:255], datetime.utcnow().isoformat())
        )
        self.conn.commit()


USER_STORE = UserStore()
