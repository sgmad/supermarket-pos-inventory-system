# d:\PythonProjects\GroceryStoreInventoryPOS\controllers\reports_controller.py
from PyQt6.QtWidgets import QTableWidgetItem

from controllers.base_controller import BaseController


class ReportsController(BaseController):
    def __init__(self, view, db_manager, operator):
        super().__init__(view)
        self.db = db_manager
        self.operator = operator
        self._require_admin_context()
        self.load_data()

    def _require_admin_context(self) -> None:
        if not hasattr(self.operator, "admin_account_id"):
            raise TypeError("ReportsController requires an AdminContext with admin_account_id.")

    def _require_active_admin(self) -> None:
        if not self.db.is_admin_active(int(self.operator.admin_account_id)):
            raise ValueError(f"Admin account {self.operator.admin_account_id} is inactive. Action blocked.")

    def _money(self, value) -> str:
        try:
            return f"{float(value or 0):.2f}"
        except (TypeError, ValueError):
            return "0.00"

    def load_data(self) -> None:
        try:
            self._require_active_admin()

            daily_data = self.db.view_daily_sales_report()
            self.view.table_daily.setRowCount(0)
            for row, record in enumerate(daily_data):
                self.view.table_daily.insertRow(row)
                self.view.table_daily.setItem(row, 0, QTableWidgetItem(str(record.get("SaleDate", ""))))
                self.view.table_daily.setItem(row, 1, QTableWidgetItem(str(record.get("TotalTransactions", 0))))
                self.view.table_daily.setItem(row, 2, QTableWidgetItem(self._money(record.get("TotalRevenue"))))
                self.view.table_daily.setItem(row, 3, QTableWidgetItem(self._money(record.get("TotalTax"))))

            history_data = self.db.view_sales_history()
            self.view.table_history.setRowCount(0)
            for row, record in enumerate(history_data):
                self.view.table_history.insertRow(row)
                self.view.table_history.setItem(row, 0, QTableWidgetItem(str(record.get("ReceiptID", ""))))
                self.view.table_history.setItem(row, 1, QTableWidgetItem(str(record.get("ReceiptDate", ""))))
                self.view.table_history.setItem(row, 2, QTableWidgetItem(str(record.get("CashierAccountID", ""))))
                self.view.table_history.setItem(row, 3, QTableWidgetItem(self._money(record.get("GrandTotal"))))
                self.view.table_history.setItem(row, 4, QTableWidgetItem(self._money(record.get("PaymentAmount"))))
                self.view.table_history.setItem(row, 5, QTableWidgetItem(str(record.get("SaleStatus", ""))))

        except Exception as e:
            self._error("Reports", f"Failed to load reports.\n\n{e}")