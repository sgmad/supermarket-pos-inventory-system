# controllers/inventory_controller.py

from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

class InventoryController:
    def __init__(self, view, db_manager):
        self.view = view
        self.db = db_manager
        
        self.view.table_stock.itemSelectionChanged.connect(self.select_product)
        self.view.btn_stock_in.clicked.connect(self.stock_in)
        self.view.btn_stock_out.clicked.connect(self.stock_out)

        self.load_data()

    def load_data(self):
        self.load_stock()
        self.load_logs()

    def load_stock(self):
        try:
            stock_data = self.db.view_available_stock()
            self.view.table_stock.setRowCount(0)
            
            for row_idx, item in enumerate(stock_data):
                self.view.table_stock.insertRow(row_idx)
                # Note: db query returns i.InventoryID, but we need p.ProductID for adjustments. 
                # Assuming view_available_stock includes p.ProductID from the JOIN in db_manager
                self.view.table_stock.setItem(row_idx, 0, QTableWidgetItem(str(item.get('ProductID', item['InventoryID']))))
                self.view.table_stock.setItem(row_idx, 1, QTableWidgetItem(item['ProductName']))
                self.view.table_stock.setItem(row_idx, 2, QTableWidgetItem(str(item['QtyAvailable'])))
                self.view.table_stock.setItem(row_idx, 3, QTableWidgetItem(str(item['LastUpdated'])))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load stock:\n{str(e)}")

    def load_logs(self):
        try:
            logs = self.db.view_inventory_movement_logs()
            self.view.table_logs.setRowCount(0)
            
            for row_idx, log in enumerate(logs):
                self.view.table_logs.insertRow(row_idx)
                self.view.table_logs.setItem(row_idx, 0, QTableWidgetItem(str(log['AuditDateTime'])))
                self.view.table_logs.setItem(row_idx, 1, QTableWidgetItem(str(log['ProductName'])))
                
                # Format change amount with + or - sign
                change = log['ChangeAmount']
                change_str = f"+{change}" if change > 0 else str(change)
                
                self.view.table_logs.setItem(row_idx, 2, QTableWidgetItem(change_str))
                self.view.table_logs.setItem(row_idx, 3, QTableWidgetItem(log['Reason']))
                self.view.table_logs.setItem(row_idx, 4, QTableWidgetItem(str(log['PreviousQty'])))
                self.view.table_logs.setItem(row_idx, 5, QTableWidgetItem(str(log['NewQty'])))
        except Exception as e:
            pass # Fails silently if table is empty on fresh start

    def select_product(self):
        rows = self.view.table_stock.selectedItems()
        if rows:
            row = rows[0].row()
            self.view.input_prod_id.setText(self.view.table_stock.item(row, 0).text())
            self.view.input_prod_name.setText(self.view.table_stock.item(row, 1).text())
            
            self.view.btn_stock_in.setEnabled(True)
            self.view.btn_stock_out.setEnabled(True)
            self.view.input_qty.clear()

    def stock_in(self):
        self._execute_adjustment('sp_stock_in')

    def stock_out(self):
        self._execute_adjustment('sp_stock_out')

    def _execute_adjustment(self, procedure_name):
        p_id = self.view.input_prod_id.text()
        qty_str = self.view.input_qty.text()

        try:
            if not p_id:
                raise ValueError("No product selected.")
            if not qty_str.isdigit() or int(qty_str) <= 0:
                raise ValueError("Quantity must be a positive number.")

            qty = int(qty_str)
            # Admin ID hardcoded to 1 pending auth implementation
            if procedure_name == 'sp_stock_in':
                self.db.record_stock_in(int(p_id), 1, qty)
            else:
                # Add method to db_manager if not exists, or direct call
                with self.db._get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.callproc('sp_stock_out', (int(p_id), 1, qty))
                        conn.commit()

            QMessageBox.information(self.view, "Success", "Stock adjusted successfully.")
            self.view.input_qty.clear()
            self.load_data() # Refresh both tables
            
        except ValueError as ve:
            QMessageBox.warning(self.view, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error", str(e))