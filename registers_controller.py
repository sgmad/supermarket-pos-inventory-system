# d:\PythonProjects\GroceryStoreInventoryPOS\controllers\registers_controller.py
from PyQt6.QtWidgets import QTableWidgetItem

from controllers.base_controller import BaseController


class RegistersController(BaseController):
    def __init__(self, view, db_manager, operator):
        super().__init__(view)
        self.db = db_manager
        self.operator = operator
        self._require_admin_context()

        self.view.table.itemSelectionChanged.connect(self.select_register)
        self.view.btn_add.clicked.connect(self.add_register)
        self.view.btn_update.clicked.connect(self.update_register)
        self.view.btn_clear.clicked.connect(self.clear_form)
        self.view.btn_refresh.clicked.connect(self.load_data)

        self.load_data()

    def _require_admin_context(self) -> None:
        if not hasattr(self.operator, "admin_account_id"):
            raise TypeError("RegistersController requires an AdminContext with admin_account_id.")

    def _require_active_admin(self) -> None:
        if not self.db.is_admin_active(int(self.operator.admin_account_id)):
            raise ValueError(f"Admin account {self.operator.admin_account_id} is inactive. Action blocked.")

    def load_data(self) -> None:
        try:
            self._require_active_admin()

            regs = self.db.get_registers()
            self.view.table.setRowCount(0)

            for row_idx, r in enumerate(regs):
                self.view.table.insertRow(row_idx)
                self.view.table.setItem(row_idx, 0, QTableWidgetItem(str(r.get("RegisterID") or "")))
                self.view.table.setItem(row_idx, 1, QTableWidgetItem(str(r.get("Location") or "")))
                self.view.table.setItem(row_idx, 2, QTableWidgetItem(str(r.get("Status") or "")))

            self.clear_form()

        except Exception as e:
            self._error("Registers", f"Failed to load registers.\n\n{e}")

    def clear_form(self) -> None:
        self.view.table.clearSelection()
        self.view.input_register_id.clear()
        self.view.input_location.clear()
        self.view.combo_status.setCurrentText("Online")
        self.view.btn_update.setEnabled(False)
        self.view.btn_add.setEnabled(True)

    def select_register(self) -> None:
        items = self.view.table.selectedItems()
        if not items:
            return

        row = items[0].row()
        self.view.input_register_id.setText(self.view.table.item(row, 0).text().strip())
        self.view.input_location.setText(self.view.table.item(row, 1).text())
        self.view.combo_status.setCurrentText(self.view.table.item(row, 2).text())

        self.view.btn_update.setEnabled(True)
        self.view.btn_add.setEnabled(False)

    def add_register(self) -> None:
        try:
            self._require_active_admin()

            location = (self.view.input_location.text() or "").strip()
            status = (self.view.combo_status.currentText() or "").strip()

            if not location:
                raise ValueError("Location is required.")

            new_id = self.db.add_register(location=location, status=status)

            self._info("Registers", f"Register created (ID {new_id}).")
            self.load_data()

        except ValueError as ve:
            self._warn("Registers", str(ve))
        except Exception as e:
            self._error("Registers", f"Failed to add register.\n\n{e}")

    def update_register(self) -> None:
        try:
            self._require_active_admin()

            reg_id = self._parse_int("Selected Register ID", self.view.input_register_id.text())
            location = (self.view.input_location.text() or "").strip()
            status = (self.view.combo_status.currentText() or "").strip()

            if not location:
                raise ValueError("Location is required.")

            self.db.update_register(register_id=reg_id, location=location, status=status)

            self._info("Registers", "Register updated.")
            self.load_data()

        except ValueError as ve:
            self._warn("Registers", str(ve))
        except Exception as e:
            self._error("Registers", f"Failed to update register.\n\n{e}")