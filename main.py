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

        # Ініціалізація бази даних та завантаження в пам'ять (фільтрує статус 8)
        self.init_database_and_playlist()

        # Підключення кнопок до обробників
        self.bNext.clicked.connect(self.on_next_clicked)
        self.bPlay.clicked.connect(self.on_play_clicked)
        self.bThere.clicked.connect(self.on_there_clicked)
        self.bReName.clicked.connect(self.on_rename_clicked)
        self.bRemove.clicked.connect(self.on_remove_clicked)

        # Ініціалізація дерева та зв'язування подій
        self.populate_tree()
        self.treeFS.itemClicked.connect(self.on_tree_item_clicked)

    def init_database_and_playlist(self):
        """Підключення до бази, завантаження активних записів, перемішування і виведення першого елемента"""
        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            # Завантажуємо записи (статус 8 автоматично відсіюється в database.py)
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
        """Обробник натискання кнопки bPlay (повторний запуск поточного файлу)"""
        if not self.playlist:
            return
        record = self.playlist[self.current_index]
        self.play_file(record.curpath)

    def on_next_clicked(self):
        """Перехід до наступного випадкового запису, оновлення полів і запуск"""
        if not self.playlist:
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)
        record = self.playlist[self.current_index]
        self.update_ui_from_record(record)
        self.play_file(record.curpath)
        
        print(f"Індекс: {self.current_index}, idfile: {record.idfile}")

    def on_there_clicked(self):
        """Обробник кнопки bThere: оновлює oldnextpath та statusfile=6 у пам'яті та базі"""
        if not self.playlist:
            return

        record = self.playlist[self.current_index]
        new_next_path = self.tNextPath.text().strip()

        record.oldnextpath = new_next_path
        record.statusfile = 6

        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            success = db.update_record_target(record.idfile, new_next_path, 6)
            db.close()
            if success:
                print(f"Збережено (There): idfile={record.idfile} -> статус 6")

    def on_rename_clicked(self):
        """Обробник кнопки bReName: записує шлях з tNextPath у oldnextpath та встановлює статус 6"""
        if not self.playlist:
            return

        record = self.playlist[self.current_index]
        new_next_path = self.tNextPath.text().strip()

        record.oldnextpath = new_next_path
        record.statusfile = 6

        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            success = db.update_record_target(record.idfile, new_next_path, 6)
            db.close()
            if success:
                print(f"Зафіксовано перейменування: idfile={record.idfile} -> статус 6")

    def on_remove_clicked(self):
        """Обробник кнопки bRemove: ставимо статус 8 у базі, видаляємо з пам'яті та йдемо далі"""
        if not self.playlist:
            return

        record = self.playlist[self.current_index]
        record.statusfile = 8

        # Оновлюємо статус в базі даних на 8
        db = XKatDatabase("/home/os/XKat/BASE/xfiles.db")
        if db.connect():
            success = db.update_status(record.idfile, 8)
            db.close()
            if success:
                print(f"Файл позначено до видалення (статус 8): idfile={record.idfile}, шлях={record.curpath}")

        # Видаляємо поточний елемент зі списку в пам'яті
        self.playlist.pop(self.current_index)

        # Переходимо до наступного або виводимо повідомлення, якщо список скінчився
        if self.playlist:
            if self.current_index >= len(self.playlist):
                self.current_index = 0
            
            next_record = self.playlist[self.current_index]
            self.update_ui_from_record(next_record)
            self.play_file(next_record.curpath)
        else:
            self.tCurPath.setText("Плейлист порожній")
            self.tNextPath.clear()
            if hasattr(self.tComm, "setPlainText"):
                self.tComm.clear()
            else:
                self.tComm.setText("")

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

            if self.playlist and 0 <= self.current_index < len(self.playlist):
                current_record = self.playlist[self.current_index]
                if current_record.curpath:
                    file_name_ext = Path(current_record.curpath).name
                    new_full_path = str(Path(dir_path) / file_name_ext)
                    self.tNextPath.setText(new_full_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = XKFormPyQt()
    form.show()
    sys.exit(app.exec())