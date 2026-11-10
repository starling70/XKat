# ui_form.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)


class UIForm:
    @staticmethod
    def setup_ui(window):
        window.setWindowTitle("Xkat (PyQt6 Modular)")
        window.resize(1100, 700)

        # Головний віджет та компонування
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- ЛІВА КОЛОНКА (Поля введення + Вкладки + Таблиця) ---
        left_layout = QVBoxLayout()

        window.tCurPath = QLineEdit()
        window.tCurPath.setReadOnly(True)
        window.lDestPath = QLabel("Dest Path Label")
        window.tNextPath = QLineEdit()
        window.tNextPath.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        window.tComm = QTextEdit()
        window.tComm.setMaximumHeight(80)

        left_layout.addWidget(window.tCurPath)
        left_layout.addWidget(window.lDestPath)
        left_layout.addWidget(window.tNextPath)
        left_layout.addWidget(window.tComm)

        # Панель вкладок дій (tabPanel)
        window.tabPanel = QTabWidget()

        # Вкладка "Просмотр"
        pPlay = QWidget()
        pPlay_layout = QHBoxLayout(pPlay)
        window.bPlay = QPushButton("Play")
        window.bNext = QPushButton("Next")
        window.bStay = QPushButton("St")
        window.bReName = QPushButton("ReName")
        window.bConvert = QPushButton("Convert")
        window.bToEdit = QPushButton("ToEdit")
        window.bRemove = QPushButton("Remove")
        for btn in [
            window.bPlay,
            window.bNext,
            window.bStay,
            window.bReName,
            window.bConvert,
            window.bToEdit,
            window.bRemove,
        ]:
            pPlay_layout.addWidget(btn)
        window.tabPanel.addTab(pPlay, "Просмотр")

        window.tabPanel.addTab(QWidget(), "Удаление")
        window.tabPanel.addTab(QWidget(), "Пережато")
        window.tabPanel.addTab(QWidget(), "Редактирование")

        left_layout.addWidget(window.tabPanel)

        # Таблиця (tTable)
        window.tTable = QTableWidget(4, 4)
        left_layout.addWidget(window.tTable)

        main_layout.addLayout(left_layout, stretch=3)

        # --- ЦЕНТРАЛЬНА ПАНЕЛЬ КНОПОК ---
        center_layout = QVBoxLayout()
        window.bThere = QPushButton("Сюда")
        window.bOut = QPushButton("Отсюда")
        window.tSearch = QLineEdit()
        window.bSearch = QPushButton("Search")
        window.cbStay = QCheckBox("Stay")

        center_layout.addWidget(window.bThere)
        center_layout.addWidget(window.bOut)
        center_layout.addWidget(window.tSearch)
        center_layout.addWidget(window.bSearch)
        center_layout.addWidget(window.cbStay)
        center_layout.addStretch()

        main_layout.addLayout(center_layout, stretch=1)

        # --- ПРАВА КОЛОНКА (Дерево файлів treeFS) ---
        window.treeFS = QTreeWidget()
        window.treeFS.setHeaderLabel("X")
        main_layout.addWidget(window.treeFS, stretch=2)
