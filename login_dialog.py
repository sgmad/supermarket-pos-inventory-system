# d:\PythonProjects\GroceryStoreInventoryPOS\views\login_dialog.py
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self, title: str = "Login", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        root.addWidget(QLabel("<b>Please sign in</b>"))

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Username:", self.input_username)
        form.addRow("Password:", self.input_password)

        root.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_login = QPushButton("Login")
        self.btn_cancel = QPushButton("Cancel")

        btn_row.addWidget(self.btn_login)
        btn_row.addWidget(self.btn_cancel)

        root.addLayout(btn_row)

        self.btn_login.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        self.input_username.setFocus()

    def username(self) -> str:
        return (self.input_username.text() or "").strip()

    def password(self) -> str:
        return self.input_password.text() or ""