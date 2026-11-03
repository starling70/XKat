# database.py
from pathlib import Path
import sqlite3


class FileRecord:
    def __init__(self, idfile, curpath, oldnextpath, statusfile, comm):
        self.idfile = idfile
        self.curpath = curpath
        self.oldnextpath = oldnextpath
        self.statusfile = statusfile
        self.comm = comm

    def __repr__(self):
        return f"FileRecord(idfile={self.idfile}, curpath='{self.curpath}')"


class XKatDatabase:

    def __init__(self, db_path="/home/os/XKat/BASE/xfiles.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None

    def connect(self):
        """Підключення до існуючої бази даних SQLite"""
        if not self.db_path.exists():
            print(f"Увага: Файл бази даних не знайдено за шляхом {self.db_path}")
            return False

        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Помилка підключення до бази: {e}")
            return False

    def load_all_records(self):
        """Зчитування всіх записів із таблиці xfiles та перетворення на об'єкти"""
        if not self.conn:
            return []
        
        try:
            self.cursor.execute(
                "SELECT idfile, curpath, oldnextpath, statusfile, comm FROM xfiles"
            )
            rows = self.cursor.fetchall()
            # Формуємо список об'єктів FileRecord
            records = [
                FileRecord(row[0], row[1], row[2], row[3], row[4])
                for row in rows
            ]
            return records
        except Exception as e:
            print(f"Помилка виконання запиту: {e}")
            return []

    def close(self):
        """Закриття з'єднання з базою"""
        if self.conn:
            self.conn.close()