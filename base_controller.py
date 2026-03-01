# d:\PythonProjects\GroceryStoreInventoryPOS\controllers\base_controller.py
from __future__ import annotations

import traceback
from typing import Optional

from PyQt6.QtWidgets import QMessageBox, QWidget


class BaseController:
    """
    Centralizes:
    - Consistent dialogs (info/warn/error/confirm)
    - Common parsing helpers (int, money)
    - Consistent exception-to-details formatting for fatal/rare paths
    """

    def __init__(self, view: QWidget):
        self.view = view

    # ---------------- Dialog helpers ----------------

    def _info(self, title: str, message: str) -> None:
        QMessageBox.information(self.view, title, message)

    def _warn(self, title: str, message: str) -> None:
        QMessageBox.warning(self.view, title, message)

    def _error(self, title: str, message: str) -> None:
        QMessageBox.critical(self.view, title, message)

    def _confirm(self, title: str, message: str) -> bool:
        result = QMessageBox.question(
            self.view,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes

    def _exception_details(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    def _error_with_details(self, title: str, exc: Exception, user_message: Optional[str] = None) -> None:
        details = self._exception_details(exc)
        if user_message:
            QMessageBox.critical(self.view, title, f"{user_message}\n\n{type(exc).__name__}: {exc}\n\n{details}")
        else:
            QMessageBox.critical(self.view, title, f"{type(exc).__name__}: {exc}\n\n{details}")

    # ---------------- Parse helpers ----------------

    def _parse_int(self, label: str, raw: str) -> int:
        text = (raw or "").strip()
        if not text:
            raise ValueError(f"{label} is required.")
        try:
            return int(text)
        except ValueError:
            raise ValueError(f"{label} must be a whole number.")

    def _parse_money(self, label: str, raw: str) -> float:
        text = (raw or "").replace(",", "").strip()
        if not text:
            raise ValueError(f"{label} is required.")
        try:
            return float(text)
        except ValueError:
            raise ValueError(f"{label} must be a valid amount.")