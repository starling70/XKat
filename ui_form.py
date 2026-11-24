from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
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

        central_widget = QWidget(window)
        window.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # --- Ліва колонка: шляхи, коментар, вкладки дій, таблиця ---
        left_layout = QVBoxLayout()
        left_layout.setSpacing(6)

        window.tCurPath = QLineEdit()
        window.tCurPath.setReadOnly(True)

        window.lDestPath = QLabel("Dest Path Label")

        window.tNextPath = QLineEdit()
        window.tNextPath.setAlignment(Qt.AlignmentFlag.AlignLeft)

        window.tComm = QTextEdit()
        window.tComm.setMaximumHeight(80)

        for widget in (window.tCurPath, window.lDestPath, window.tNextPath, window.tComm):
            left_layout.addWidget(widget)

        window.tabPanel = QTabWidget()

        play_tab = QWidget()
        play_layout = QHBoxLayout(play_tab)
        play_layout.setContentsMargins(6, 6, 6, 6)
        play_layout.setSpacing(4)

        play_buttons = (
            ("bPlay", "Play"),
            ("bNext", "Next"),
            ("bStay", "St"),
            ("bReName", "ReName"),
            ("bConvert", "Convert"),
            ("bToEdit", "ToEdit"),
            ("bRemove", "Remove"),
        )
        for attr_name, text in play_buttons:
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            setattr(window, attr_name, btn)
            play_layout.addWidget(btn)

        window.tabPanel.addTab(play_tab, "Просмотр")
        for tab_title in ("Удаление", "Пережато", "Редактирование"):
            window.tabPanel.addTab(QWidget(), tab_title)

        left_layout.addWidget(window.tabPanel)

        window.tTable = QTableWidget(4, 4)
        window.tTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        window.tTable.setAlternatingRowColors(True)
        window.tTable.horizontalHeader().setStretchLastSection(True)
        window.tTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        left_layout.addWidget(window.tTable)

        main_layout.addLayout(left_layout, stretch=3)

        # --- Центральна панель керування ---
        center_layout = QVBoxLayout()
        center_layout.setSpacing(6)

        window.bThere = QPushButton("Сюда")
        window.bOut = QPushButton("Отсюда")
        window.tSearch = QLineEdit()
        window.tSearch.setPlaceholderText("Поиск...")
        window.bSearch = QPushButton("Search")
        window.cbStay = QCheckBox("Stay")

        for widget in (window.bThere, window.bOut, window.tSearch, window.bSearch, window.cbStay):
            widget.setMinimumWidth(110)
            center_layout.addWidget(widget)

        center_layout.addStretch()
        main_layout.addLayout(center_layout, stretch=1)

        # --- Права колонка: дерево файлової системи ---
        window.treeFS = QTreeWidget()
        window.treeFS.setHeaderLabel("X")
        window.treeFS.setAlternatingRowColors(True)
        main_layout.addWidget(window.treeFS, stretch=2)
        