import sqlite3
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SQLViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XKat — Перевірка бази даних SQLite")
        self.resize(900, 600)

        # Головний віджет і макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. Поле для введення SQL-запиту (багаторядкове)
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText(
            "Введіть SQL-запит, наприклад: SELECT * FROM xfiles WHERE statusfile = 1 LIMIT 50"
        )
        self.query_input.setMaximumHeight(100)
        # Вставимо дефолтний запит для зручності
        self.query_input.setPlainText("SELECT * FROM xfiles LIMIT 50;")
        layout.addWidget(self.query_input)

        # 2. Кнопка виконання
        self.exec_button = QPushButton("Виконати запит")
        self.exec_button.clicked.connect(self.execute_query)
        layout.addWidget(self.exec_button)

        # 3. Таблиця для виводу результатів
        self.table = QTableWidget()
        layout.addWidget(self.table)

    def execute_query(self):
        query = self.query_input.toPlainText().strip()
        if not query:
            return

        try:
            # Підключаємося до нашої нової бази SQLite
            conn = sqlite3.connect("/home/os/XKat/BASE/xfiles.db")
            cursor = conn.cursor()

            cursor.execute(query)

            # Якщо це запит на вибірку (SELECT)
            if cursor.description:
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]

                # Заповнюємо таблицю
                self.table.setRowCount(len(rows))
                self.table.setColumnCount(len(column_names))
                self.table.setHorizontalHeaderLabels(column_names)

                for row_idx, row_data in enumerate(rows):
                    for col_idx, cell_data in enumerate(row_data):
                        val_str = str(cell_data) if cell_data is not None else "NULL"
                        item = QTableWidgetItem(val_str)
                        self.table.setItem(row_idx, col_idx, item)
            else:
                # Для UPDATE / DELETE / INSERT
                conn.commit()
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                QMessageBox.information(
                    self, "Успіх", "Запит успішно виконано (зміни збережено)."
                )

            conn.close()

        except Exception as e:
            QMessageBox.critical(
                self.Error if hasattr(self, "Error") else self, "Помилка SQL", str(e)
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SQLViewerApp()
    window.show()
    sys.exit(app.exec())
