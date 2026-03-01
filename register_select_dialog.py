# d:\PythonProjects\GroceryStoreInventoryPOS\views\register_select_dialog.py
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PyQt6.QtCore import Qt


class RegisterSelectDialog(QDialog):
    def __init__(self, registers: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Register")
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        root.addWidget(QLabel("<b>Select an online register</b>"))

        self.combo_register = QComboBox()
        for r in registers:
            reg_id = r.get("RegisterID")
            loc = r.get("Location") or ""
            status = r.get("Status") or ""
            self.combo_register.addItem(f"{loc} (ID {reg_id}) - {status}", reg_id)

        root.addWidget(self.combo_register)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_ok = QPushButton("Continue")
        self.btn_cancel = QPushButton("Cancel")

        btn_row.addWidget(self.btn_ok)
        btn_row.addWidget(self.btn_cancel)

        root.addLayout(btn_row)

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        self.combo_register.setFocus()

    def selected_register_id(self) -> int:
        return int(self.combo_register.currentData())