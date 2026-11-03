# main.py
from pathlib import Path
import random
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

        # Ініціалізація дерева та зв'язування подій
        self.populate_tree()
        self.treeFS.itemClicked.connect(self.on_tree_item_clicked)

    def init_database_and_playlist(self):
        """Підключення до бази, завантаження, перемішування і виведення першого елемента"""
        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            # Завантажуємо всі записи у вигляді об'єктів
            self.playlist = db.load_all_records()
            db.close()

            if self.playlist:
                # Перемішуємо плейлист для випадкового перегляду
                random.shuffle(self.playlist)
                self.current_index = 0

                # Беремо перший об'єкт і вписуємо його curpath у tCurPath
                first_record = self.playlist[self.current_index]
                self.tCurPath.setText(first_record.curpath)
            else:
                self.tCurPath.setText("База даних порожня або таблиця xfiles не знайдена")

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