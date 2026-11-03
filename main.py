# main.py
from pathlib import Path
import random
import subprocess
import sys

from database import XKatDatabase
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem
from ui_form import UIForm


class XKFormPyQt(QMainWindow):

    def __init__(self, mode=0):
        super().__init__()

        # Змінні стану та плейлист
        self.current_selected_dir = None
        self.root_path = Path("/home/alls3/X")
        self.playlist = []
        self.current_index = 0

        # Будуємо інтерфейс з ui_form.py
        UIForm.setup_ui(self)

        # Ініціалізація бази даних та завантаження в пам'ять
        self.init_database_and_playlist()

        # Підключення кнопок до обробників
        self.bNext.clicked.connect(self.on_next_clicked)
        self.bPlay.clicked.connect(self.on_play_clicked)

        # Ініціалізація дерева та зв'язування подій
        self.populate_tree()
        self.treeFS.itemClicked.connect(self.on_tree_item_clicked)

    def init_database_and_playlist(self):
        """Підключення до бази, завантаження, перемішування і виведення першого елемента"""
        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            # Завантажуємо всі записи у вигляді об'єктів FileRecord
            self.playlist = db.load_all_records()
            db.close()

            if self.playlist:
                # Перемішуємо плейлист для випадкового перегляду
                random.shuffle(self.playlist)
                self.current_index = 0

                # Виводимо дані першого запису на форму та запускаємо на перегляд
                record = self.playlist[self.current_index]
                self.update_ui_from_record(record)
                self.play_file(record.curpath)
            else:
                self.tCurPath.setText("База даних порожня або таблиця xfiles не знайдена")

    def update_ui_from_record(self, record):
        """Допоміжний метод для оновлення полів форми з об'єкта FileRecord"""
        self.tCurPath.setText(record.curpath if record.curpath else "")
        self.tNextPath.setText(record.oldnextpath if record.oldnextpath else "")
        
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
            # xdg-open запускає програму за замовчуванням (VLC) у фоновому режимі
            subprocess.Popen(["xdg-open", str(path_obj)])
            print(f"Запущено на перегляд: {file_path}")
        except Exception as e:
            print(f"Помилка запуску зовнішнього плеєра: {e}")

    def on_play_clicked(self):
        """Обробник натискання кнопки bPlay (повторний запуск поточного файлу)"""
        if not self.playlist:
            return
        record = self.playlist[self.current_index]
        self.play_file(record.curpath)

    def on_next_clicked(self):
        """Перехід до наступного випадкового запису, оновлення полів і запуск"""
        if not self.playlist:
            return

        # Збільшуємо індекс із циклічним переходом
        self.current_index = (self.current_index + 1) % len(self.playlist)

        # Беремо об'єкт, оновлюємо поля і запускаємо на перегляд
        record = self.playlist[self.current_index]
        self.update_ui_from_record(record)
        self.play_file(record.curpath)
        
        print(f"Індекс: {self.current_index}, idfile: {record.idfile}")

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
        dir_path = item.data(0, 32)
        if dir_path:
            self.current_selected_dir = dir_path
            self.treeFS.setHeaderLabel(dir_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = XKFormPyQt()
    form.show()
    sys.exit(app.exec())