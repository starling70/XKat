# main.py
from pathlib import Path
import random
import subprocess
import sys

from database import XKatDatabase
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QTableWidgetItem
from ui_form import UIForm


class XKFormPyQt(QMainWindow):

    def __init__(self, mode=0):
        super().__init__()

        # Змінні стану та плейлист
        self.current_selected_dir = None
        self.root_path = Path("/home/alls3/X")
        self.incoming_path = Path("/home/B400/mule/Incoming/")
        self.playlist = []
        self.current_index = 0
        self.pending_first_play = False  # Прапорець для відкладеного старту плейлиста

        # Будуємо інтерфейс з ui_form.py
        UIForm.setup_ui(self)

        # Скануємо папку Incoming та заповнюємо tTable новими файлами
        self.populate_incoming_table()

        # Ініціалізація бази даних та завантаження активного плейлиста в пам'ять
        self.init_database_and_playlist()

        # Підключення кнопок до обробників
        self.bNext.clicked.connect(self.on_next_clicked)
        self.bPlay.clicked.connect(self.on_play_clicked)
        self.bThere.clicked.connect(self.on_there_clicked)
        self.bReName.clicked.connect(self.on_rename_clicked)
        self.bRemove.clicked.connect(self.on_remove_clicked)
        self.bStay.clicked.connect(self.on_stay_clicked)

        # Ініціалізація дерева та зв'язування подій
        self.populate_tree()
        self.treeFS.itemClicked.connect(self.on_tree_item_clicked)
        
        # Зв'язування кліків по таблиці Incoming
        self.tTable.itemClicked.connect(self.on_table_item_clicked)

    def populate_incoming_table(self):
        """Сканує папку Incoming та виводить знайдені файли у tTable"""
        self.tTable.clearContents()
        
        if not self.incoming_path.exists() or not self.incoming_path.is_dir():
            self.tTable.setRowCount(1)
            self.tTable.setItem(0, 0, QTableWidgetItem(f"Папка не знайдена: {self.incoming_path}"))
            return

        files = sorted([p for p in self.incoming_path.rglob('*') if p.is_file()])

        self.tTable.setRowCount(len(files))
        self.tTable.setColumnCount(1)
        
        for row, file_path in enumerate(files):
            item = QTableWidgetItem(str(file_path))
            self.tTable.setItem(row, 0, item)

    def init_database_and_playlist(self):
        """Підключення до бази, завантаження активних записів, перемішування"""
        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            self.playlist = db.load_all_records()
            db.close()

            if self.playlist:
                random.shuffle(self.playlist)
                self.current_index = 0

                # Виводимо дані першого запису на форму (у поля)
                record = self.playlist[self.current_index]
                self.update_ui_from_record(record)

                # Перевіряємо, чи є файли у папці Incoming
                incoming_files = [p for p in self.incoming_path.rglob('*') if p.is_file()] if self.incoming_path.exists() else []

                if incoming_files:
                    # Якщо папка не порожня — НЕ запускаємо відео автоматично, чекаємо дій
                    self.pending_first_play = True
                    print(f"Знайдено нові файли в Incoming ({len(incoming_files)} шт.). Автозапуск скасовано, очікуємо вибору.")
                else:
                    # Якщо папка порожня — запускаємо перший файл одразу, як і раніше
                    self.play_file(record.curpath)
            else:
                self.tCurPath.setText("База даних не містить активних записів")

    def update_ui_from_record(self, record):
        """Допоміжний метод для оновлення полів форми з об'єкта FileRecord"""
        self.tCurPath.setText(record.curpath if record.curpath else "")
        
        if record.oldnextpath and record.oldnextpath.strip():
            self.tNextPath.setText(record.oldnextpath)
        else:
            self.tNextPath.setText(record.curpath if record.curpath else "")
        
        comm_text = record.comm if record.comm else ""
        if hasattr(self.tComm, "setPlainText"):
            self.tComm.setPlainText(comm_text)
        else:
            self.tComm.setText(comm_text)

    def play_file(self, file_path):
        """Асинхронний запуск файлу системним обробником (VLC)"""
        if not file_path:
            return

        path_obj = Path(file_path)
        if not path_obj.exists():
            print(f"Попередження: Файл не знайдено на диску: {file_path}")
            return

        try:
            subprocess.Popen(["xdg-open", str(path_obj)])
            print(f"Запущено на перегляд: {file_path}")
        except Exception as e:
            print(f"Помилка запуску зовнішнього плеєра: {e}")

    def on_play_clicked(self):
        """Обробник натискання кнопки bPlay"""
        if not self.playlist:
            return
        record = self.playlist[self.current_index]
        self.play_file(record.curpath)

    def on_next_clicked(self):
        """Перехід до наступного випадкового запису"""
        if not self.playlist:
            return

        if self.pending_first_play:
            # Якщо автозапуск при старті був заблокований через Incoming,
            # то перший клік b`Next` відтворює поточний (0-й) елемент без зсуву індексу
            self.pending_first_play = False
            record = self.playlist[self.current_index]
            self.update_ui_from_record(record)
            self.play_file(record.curpath)
        else:
            # Звичайний перехід до наступного елемента
            self.current_index = (self.current_index + 1) % len(self.playlist)
            record = self.playlist[self.current_index]
            self.update_ui_from_record(record)
            self.play_file(record.curpath)
        
        print(f"Індекс: {self.current_index}, idfile: {record.idfile}")

    def on_there_clicked(self):
        """Обробник кнопки bThere"""
        if not self.playlist:
            return

        record = self.playlist[self.current_index]
        new_next_path = self.tNextPath.text().strip()

        record.oldnextpath = new_next_path
        record.statusfile = 6

        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            db.update_record_target(record.idfile, new_next_path, 6)
            db.close()

    def on_rename_clicked(self):
        """Обробник кнопки bReName"""
        if not self.playlist:
            return

        record = self.playlist[self.current_index]
        new_next_path = self.tNextPath.text().strip()

        record.oldnextpath = new_next_path
        record.statusfile = 6

        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            db.update_record_target(record.idfile, new_next_path, 6)
            db.close()

    def on_remove_clicked(self):
        """Обробник кнопки bRemove (статус 8)"""
        if not self.playlist:
            return

        record = self.playlist[self.current_index]
        record.statusfile = 8

        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            db.update_status(record.idfile, 8)
            db.close()

        self.playlist.pop(self.current_index)

        if self.playlist:
            if self.current_index >= len(self.playlist):
                self.current_index = 0
            next_record = self.playlist[self.current_index]
            self.update_ui_from_record(next_record)
            self.play_file(next_record.curpath)
        else:
            self.tCurPath.setText("Плейлист порожній")
            self.tNextPath.clear()

    def on_stay_clicked(self):
        """Обробник кнопки bStay: створює новий запис у базі зі статусом 6"""
        cur_path = self.tCurPath.text().strip()
        next_path = self.tNextPath.text().strip()
        comm = self.tComm.toPlainText() if hasattr(self.tComm, "setPlainText") else self.tComm.text()

        if not cur_path:
            print("Попередження: Поле curpath порожнє, нічого додавати.")
            return

        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            success = db.insert_record(cur_path, next_path, 6, comm)
            db.close()
            if success:
                print(f"Успішно додано новий файл у базу зі статусом 6: {cur_path}")

    def populate_tree(self):
        self.treeFS.clear()

        if not self.root_path.exists() or not self.root_path.is_dir():
            QTreeWidgetItem(
                self.treeFS, [f"Шлях не знайдено: {self.root_path}"]
            )
            return

        root_item = QTreeWidgetItem(self.treeFS, [self.root_path.name])
        root_item.setData(0, 32, str(self.root_path))

        self.add_subdirectories(self.root_path, root_item)
        root_item.setExpanded(True)

    def add_subdirectories(self, current_path: Path, parent_item: QTreeWidgetItem):
        try:
            for sub_path in sorted(current_path.iterdir()):
                if sub_path.is_dir():
                    sub_item = QTreeWidgetItem(parent_item, [sub_path.name])
                    sub_item.setData(0, 32, str(sub_path))
                    self.add_subdirectories(sub_path, sub_item)
        except PermissionError:
            pass

    def on_tree_item_clicked(self, item, column):
        """Обробник кліку по папці в дереві treeFS"""
        dir_path = item.data(0, 32)
        if dir_path:
            self.current_selected_dir = dir_path
            self.treeFS.setHeaderLabel(dir_path)

            current_cur_path = self.tCurPath.text().strip()
            if current_cur_path:
                file_name_ext = Path(current_cur_path).name
                new_full_path = str(Path(dir_path) / file_name_ext)
                self.tNextPath.setText(new_full_path)

    def on_table_item_clicked(self, item):
        """Обробник кліку по рядку у таблиці tTable (нові файли з Incoming)"""
        file_path = item.text()
        if file_path and Path(file_path).exists():
            self.tCurPath.setText(file_path)
            self.tNextPath.setText(file_path)
            self.play_file(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = XKFormPyQt()
    form.show()
    sys.exit(app.exec())