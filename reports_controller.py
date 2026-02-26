from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

class ReportsController:
    def __init__(self, view, db_manager):
        self.view = view
        self.db = db_manager
        self.load_data()

    def load_data(self):
        try:
            # Load Daily Aggregation
            daily_data = self.db.view_daily_sales_report()
            self.view.table_daily.setRowCount(0)
            for row, record in enumerate(daily_data):
                self.view.table_daily.insertRow(row)
                self.view.table_daily.setItem(row, 0, QTableWidgetItem(str(record['SaleDate'])))
                self.view.table_daily.setItem(row, 1, QTableWidgetItem(str(record['TotalTransactions'])))
                self.view.table_daily.setItem(row, 2, QTableWidgetItem(f"{record['TotalRevenue']:.2f}"))
                self.view.table_daily.setItem(row, 3, QTableWidgetItem(f"{record['TotalTax']:.2f}"))

            # Load Raw History
            history_data = self.db.view_sales_history()
            self.view.table_history.setRowCount(0)
            for row, record in enumerate(history_data):
                self.view.table_history.insertRow(row)
                self.view.table_history.setItem(row, 0, QTableWidgetItem(str(record['ReceiptID'])))
                self.view.table_history.setItem(row, 1, QTableWidgetItem(str(record['ReceiptDate'])))
                self.view.table_history.setItem(row, 2, QTableWidgetItem(str(record['CashierID'])))
                self.view.table_history.setItem(row, 3, QTableWidgetItem(f"{record['GrandTotal']:.2f}"))
                self.view.table_history.setItem(row, 4, QTableWidgetItem(f"{record['PaymentAmount']:.2f}"))
                self.view.table_history.setItem(row, 5, QTableWidgetItem(record['SaleStatus']))
                
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load reports:\n{str(e)}")