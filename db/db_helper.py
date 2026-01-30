import sqlite3
from collections import Generator
from contextlib import contextmanager
from pathlib import Path


class DBHelper:
    def __init__(self, db_path: str):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def init_db(self):
        """创建表（如果不存在）"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS `character` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    avatars TEXT,
                    nicknames TEXT,
                    arena_skill TEXT,
                    story_skill TEXT,
                    awakening_passive TEXT,
                    talent_tree TEXT,
                    background TEXT,
                    club TEXT,
                    element TEXT,
                    year TEXT,
                    bonds TEXT,
                    extra TEXT,
                    skins TEXT,
                    hobbies TEXT,
                    type INTEGER, -- 角色类型；1=通常，2=女神,
                    tags TEXT,
                    created_at TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    translated
                )
            """)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        提供线程安全的连接上下文管理器。
        每次调用都会创建新连接，使用后自动关闭。
        """
        conn = sqlite3.connect(self._db_path)
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            conn.close()
