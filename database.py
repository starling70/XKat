from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass
class FileRecord:
    idfile: int | None
    curpath: str | None
    oldnextpath: str | None
    statusfile: int | None
    comm: str | None

    def __repr__(self) -> str:
        return f"FileRecord(idfile={self.idfile}, curpath={self.curpath!r})"


class XKatDatabase:
    _BASE_SELECT = (
        "SELECT idfile, curpath, oldnextpath, statusfile, comm "
        "FROM xfiles "
        "WHERE (statusfile IS NULL OR statusfile != 8)"
    )

    def __init__(self, db_path: str | Path = "/home/os/XKat/BASE/xfiles.db"):
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def __enter__(self) -> "XKatDatabase":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def connect(self) -> bool:
        """Підключення до існуючої бази даних SQLite."""
        if not self.db_path.exists():
            print(f"Увага: Файл бази даних не знайдено за шляхом {self.db_path}")
            return False

        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Помилка підключення до бази: {e}")
            self.conn = None
            self.cursor = None
            return False

    def _fetch_records(self, query: str, params: tuple = ()) -> list[FileRecord]:
        if not self.conn or not self.cursor:
            return []
        try:
            self.cursor.execute(query, params)
            return [FileRecord(*row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Помилка виконання запиту: {e}")
            return []

    def _execute_write(self, query: str, params: tuple, error_prefix: str) -> bool:
        if not self.conn or not self.cursor:
            return False
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            try:
                self.conn.rollback()
            except sqlite3.Error:
                pass
            print(f"{error_prefix}: {e}")
            return False

    def load_all_records(self) -> list[FileRecord]:
        """Зчитування всіх активних записів, крім тих, де statusfile = 8."""
        return self._fetch_records(self._BASE_SELECT)

    def update_record_target(self, idfile: int, oldnextpath: str | None, statusfile: int | None) -> bool:
        """Оновлення oldnextpath та statusfile для конкретного файлу."""
        return self._execute_write(
            "UPDATE xfiles SET oldnextpath = ?, statusfile = ? WHERE idfile = ?",
            (oldnextpath, statusfile, idfile),
            "Помилка оновлення бази даних",
        )

    def update_status(self, idfile: int, statusfile: int | None) -> bool:
        """Оновлення лише statusfile для конкретного файлу."""
        return self._execute_write(
            "UPDATE xfiles SET statusfile = ? WHERE idfile = ?",
            (statusfile, idfile),
            "Помилка оновлення статусу в базі",
        )

    def insert_record(
        self,
        curpath: str,
        oldnextpath: str | None,
        statusfile: int | None,
        comm: str | None,
    ) -> bool:
        """Вставка нового запису в таблицю xfiles."""
        return self._execute_write(
            "INSERT INTO xfiles (curpath, oldnextpath, statusfile, comm) VALUES (?, ?, ?, ?)",
            (curpath, oldnextpath, statusfile, comm),
            "Помилка вставки нового запису в базу",
        )

    def update_comm(self, idfile: int, comm: str | None) -> bool:
        """Оновлення лише поля comm для конкретного файлу."""
        return self._execute_write(
            "UPDATE xfiles SET comm = ? WHERE idfile = ?",
            (comm, idfile),
            "Помилка оновлення коментаря в базі",
        )

    def search_records(self, search_term: str) -> list[FileRecord]:
        """Регістронезалежний пошук за полями curpath або comm."""
        term = f"%{search_term.lower()}%"
        query = (
            f"{self._BASE_SELECT} "
            "AND (LOWER(curpath) LIKE ? OR LOWER(comm) LIKE ?)"
        )
        return self._fetch_records(query, (term, term))

    def get_records_by_directory(self, dir_path: str | Path) -> list[FileRecord]:
        """Вибірка всіх активних записів, чий curpath належить вказаному каталогу."""
        raw_dir = str(dir_path)
        prefix = raw_dir.rstrip("/") + "/"
        query = (
            f"{self._BASE_SELECT} "
            "AND (curpath LIKE ? OR curpath = ?)"
        )
        return self._fetch_records(query, (prefix + "%", raw_dir))

    def close(self) -> None:
        """Закриття з'єднання з базою."""
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                print(f"Помилка закриття з'єднання з базою: {e}")
            finally:
                self.conn = None
                self.cursor = None
                