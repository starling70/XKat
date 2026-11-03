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
        """Зчитування всіх записів, КРІМ тих, де statusfile = 8"""
        if not self.conn:
            return []
        
        try:
            self.cursor.execute(
                "SELECT idfile, curpath, oldnextpath, statusfile, comm FROM xfiles WHERE statusfile IS NULL OR statusfile != 8"
            )
            rows = self.cursor.fetchall()
            records = [
                FileRecord(row[0], row[1], row[2], row[3], row[4])
                for row in rows
            ]
            return records
        except Exception as e:
            print(f"Помилка виконання запиту: {e}")
            return []

    def update_record_target(self, idfile, oldnextpath, statusfile):
        """Оновлення oldnextpath та statusfile для конкретного файлу"""
        if not self.conn:
            return False
        try:
            self.cursor.execute(
                "UPDATE xfiles SET oldnextpath = ?, statusfile = ? WHERE idfile = ?",
                (oldnextpath, statusfile, idfile)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Помилка оновлення бази даних: {e}")
            return False

    def update_status(self, idfile, statusfile):
        """Оновлення лише statusfile для конкретного файлу (для видалення)"""
        if not self.conn:
            return False
        try:
            self.cursor.execute(
                "UPDATE xfiles SET statusfile = ? WHERE idfile = ?",
                (statusfile, idfile)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Помилка оновлення статусу в базі: {e}")
            return False

    def close(self):
        """Закриття з'єднання з базою"""
        if self.conn:
            self.conn.close()

    def insert_record(self, curpath, oldnextpath, statusfile, comm):
            """Вставка нового запису в таблицю xfiles (idгенерується автоматично)"""
            if not self.conn:
                return False
            try:
                self.cursor.execute(
                    "INSERT INTO xfiles (curpath, oldnextpath, statusfile, comm) VALUES (?, ?, ?, ?)",
                    (curpath, oldnextpath, statusfile, comm)
                )
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Помилка вставки нового запису в базу: {e}")
                return False

    def update_comm(self, idfile, comm):
            """Оновлення лише поля comm для конкретного файлу"""
            if not self.conn:
                return False
            try:
                self.cursor.execute(
                    "UPDATE xfiles SET comm = ? WHERE idfile = ?",
                    (comm, idfile)
                )
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Помилка оновлення коментаря в базі: {e}")
                return False