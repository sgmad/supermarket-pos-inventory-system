# d:\PythonProjects\GroceryStoreInventoryPOS\controllers\inventory_controller.py
from PyQt6.QtWidgets import QTableWidgetItem

from controllers.base_controller import BaseController


class InventoryController(BaseController):
    def __init__(self, view, db_manager, operator):
        super().__init__(view)
        self.operator = operator
        self._require_admin_context()
        self.db = db_manager

        self.view.table_stock.itemSelectionChanged.connect(self.select_product)
        self.view.btn_stock_in.clicked.connect(self.stock_in)
        self.view.btn_stock_out.clicked.connect(self.stock_out)

        self.load_data()

    def _require_admin_context(self) -> None:
        if not hasattr(self.operator, "admin_account_id"):
            raise TypeError("InventoryController requires an AdminContext with admin_account_id.")

    def _require_active_admin(self) -> None:
        if not self.db.is_admin_active(int(self.operator.admin_account_id)):
            raise ValueError(f"Admin account {self.operator.admin_account_id} is inactive. Action blocked.")

    def load_data(self) -> None:
        try:
            self._require_active_admin()
            self.load_stock()
            self.load_logs()
        except Exception as e:
            self._error("Inventory", f"Failed to load inventory view.\n\n{e}")

    def load_stock(self) -> None:
        stock_data = self.db.view_available_stock()
        self.view.table_stock.setRowCount(0)

        for row_idx, item in enumerate(stock_data):
            self.view.table_stock.insertRow(row_idx)

            product_id = item.get("ProductID", "")
            name = item.get("ProductName", "")
            qty = item.get("QtyAvailable", "")
            reorder = item.get("ReorderLevel", 0)
            low_flag = "YES" if int(item.get("IsLowStock") or 0) == 1 else ""
            updated = item.get("LastUpdated", "")

            self.view.table_stock.setItem(row_idx, 0, QTableWidgetItem(str(product_id)))
            self.view.table_stock.setItem(row_idx, 1, QTableWidgetItem(str(name)))
            self.view.table_stock.setItem(row_idx, 2, QTableWidgetItem(str(qty)))
            self.view.table_stock.setItem(row_idx, 3, QTableWidgetItem(str(reorder)))
            self.view.table_stock.setItem(row_idx, 4, QTableWidgetItem(low_flag))
            self.view.table_stock.setItem(row_idx, 5, QTableWidgetItem(str(updated)))

    def load_logs(self) -> None:
        logs = self.db.view_inventory_movement_logs()
        self.view.table_logs.setRowCount(0)

        for row_idx, log in enumerate(logs):
            self.view.table_logs.insertRow(row_idx)
            self.view.table_logs.setItem(row_idx, 0, QTableWidgetItem(str(log.get("AuditDateTime", ""))))
            self.view.table_logs.setItem(row_idx, 1, QTableWidgetItem(str(log.get("ProductName", ""))))

            change = int(log.get("ChangeAmount") or 0)
            change_str = f"+{change}" if change > 0 else str(change)

            self.view.table_logs.setItem(row_idx, 2, QTableWidgetItem(change_str))
            self.view.table_logs.setItem(row_idx, 3, QTableWidgetItem(str(log.get("Reason", ""))))
            self.view.table_logs.setItem(row_idx, 4, QTableWidgetItem(str(log.get("PreviousQty", ""))))
            self.view.table_logs.setItem(row_idx, 5, QTableWidgetItem(str(log.get("NewQty", ""))))

    def select_product(self) -> None:
        items = self.view.table_stock.selectedItems()
        if not items:
            return

        row = items[0].row()
        self.view.input_prod_id.setText(self.view.table_stock.item(row, 0).text())
        self.view.input_prod_name.setText(self.view.table_stock.item(row, 1).text())

        self.view.btn_stock_in.setEnabled(True)
        self.view.btn_stock_out.setEnabled(True)
        self.view.input_qty.clear()

    def stock_in(self) -> None:
        self._execute_adjustment(is_stock_in=True)

    def stock_out(self) -> None:
        self._execute_adjustment(is_stock_in=False)

    def _execute_adjustment(self, is_stock_in: bool) -> None:
        try:
            self._require_active_admin()

            product_id = self._parse_int("Selected Product ID", self.view.input_prod_id.text())
            qty = self._parse_int("Quantity", self.view.input_qty.text())
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero.")

            if is_stock_in:
                self.db.stock_in(product_id, int(self.operator.admin_account_id), qty)
            else:
                self.db.stock_out(product_id, int(self.operator.admin_account_id), qty)

            self._info("Inventory", "Stock adjusted successfully.")
            self.view.input_qty.clear()
            self.load_data()

        except ValueError as ve:
            self._warn("Inventory", str(ve))
        except Exception as e:
            self._error("Inventory", f"Failed to adjust stock.\n\n{e}")