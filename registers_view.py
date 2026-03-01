from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox,
    QHeaderView, QGroupBox, QGridLayout, QAbstractItemView
)


class RegistersView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(12)

        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("<b>Register Management</b>"))
        header_row.addStretch()

        self.btn_refresh = QPushButton("Refresh")
        header_row.addWidget(self.btn_refresh)

        main.addLayout(header_row)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Register ID", "Location", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        main.addWidget(self.table)

        form = QGroupBox("Create / Update Register")
        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(10)

        self.input_register_id = QLineEdit()
        self.input_register_id.setReadOnly(True)
        self.input_register_id.setPlaceholderText("New (auto)")

        self.input_location = QLineEdit()
        self.input_location.setPlaceholderText("Example: Counter A / Branch 2 / Kiosk 3")

        self.combo_status = QComboBox()
        self.combo_status.addItems(["Online", "Offline"])

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Add Register")
        self.btn_update = QPushButton("Update Selected")
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setObjectName("btn_clear")

        self.btn_update.setEnabled(False)

        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_update)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_clear)

        grid.addWidget(QLabel("Register ID:"), 0, 0)
        grid.addWidget(self.input_register_id, 0, 1)
        grid.addWidget(QLabel("Status:"), 0, 2)
        grid.addWidget(self.combo_status, 0, 3)

        grid.addWidget(QLabel("Location:"), 1, 0)
        grid.addWidget(self.input_location, 1, 1, 1, 3)

        grid.addLayout(btn_row, 2, 0, 1, 4)

        form.setLayout(grid)
        main.addWidget(form)