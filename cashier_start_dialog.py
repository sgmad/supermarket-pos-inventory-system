from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox

class CashierStartDialog(QDialog):
    def __init__(self, cashiers, registers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start POS Session")

        self.combo_cashier = QComboBox()
        for c in cashiers:
            self.combo_cashier.addItem(f"{c['CashierName']} (ID {c['CashierID']})", c["CashierID"])

        self.combo_register = QComboBox()
        for r in registers:
            self.combo_register.addItem(
                f"{r['Location']} (ID {r['RegisterID']}) - {r['Status']}",
                r["RegisterID"]
            )

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select Cashier:"))
        layout.addWidget(self.combo_cashier)
        layout.addWidget(QLabel("Select Register:"))
        layout.addWidget(self.combo_register)

        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_cancel = QPushButton("Cancel")
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

        self.btn_start.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def selected_cashier_id(self) -> int:
        return int(self.combo_cashier.currentData())

    def selected_register_id(self) -> int:
        return int(self.combo_register.currentData())