from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

class POSController:
    def __init__(self, view, db_manager):
        self.view = view
        self.db = db_manager
        self.current_receipt_id = None
        self.current_grand_total = 0.0

        self.view.btn_add_item.clicked.connect(self.process_item)
        self.view.input_barcode.returnPressed.connect(self.process_item)
        self.view.btn_pay.clicked.connect(self.finalize_transaction)
        self.view.btn_cancel.clicked.connect(self.cancel_transaction)

    def process_item(self):
        prod_id_str = self.view.input_barcode.text().strip()
        qty_str = self.view.input_qty.text().strip()

        try:
            if not prod_id_str.isdigit() or not qty_str.isdigit():
                raise ValueError("Product ID and Quantity must be valid numbers.")
            
            prod_id = int(prod_id_str)
            qty = int(qty_str)

            if qty <= 0:
                raise ValueError("Quantity must be greater than zero.")

            # Create receipt session if one does not exist
            if self.current_receipt_id is None:
                # Hardcoded CashierID=1, RegisterID=1, CustomerID=None
                self.current_receipt_id = self.db.create_sale(1, 1, None)

            self.db.add_sale_item(self.current_receipt_id, prod_id, qty)
            self.refresh_cart()
            
            self.view.input_barcode.clear()
            self.view.input_qty.setText("1")
            self.view.input_barcode.setFocus()

        except ValueError as ve:
            QMessageBox.warning(self.view, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error", str(e))

    def refresh_cart(self):
        if not self.current_receipt_id:
            return

        try:
            items = self.db.get_receipt_items(self.current_receipt_id)
            self.view.table_cart.setRowCount(0)
            
            for row_idx, item in enumerate(items):
                self.view.table_cart.insertRow(row_idx)
                self.view.table_cart.setItem(row_idx, 0, QTableWidgetItem(str(item['ProductID'])))
                self.view.table_cart.setItem(row_idx, 1, QTableWidgetItem(item['ProductName']))
                self.view.table_cart.setItem(row_idx, 2, QTableWidgetItem(str(item['Qty'])))
                self.view.table_cart.setItem(row_idx, 3, QTableWidgetItem(f"{item['UnitPrice']:.2f}"))
                self.view.table_cart.setItem(row_idx, 4, QTableWidgetItem(f"{item['Subtotal']:.2f}"))

            summary = self.db.get_receipt_summary(self.current_receipt_id)
            if summary:
                self.view.lbl_subtotal.setText(f"{summary['TotalAmount']:.2f}")
                self.view.lbl_tax.setText(f"{summary['TaxAmount']:.2f}")
                self.current_grand_total = float(summary['GrandTotal'])
                self.view.lbl_grand_total.setText(f"{self.current_grand_total:.2f}")

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to refresh cart: {str(e)}")

    def finalize_transaction(self):
        if not self.current_receipt_id:
            return QMessageBox.warning(self.view, "Warning", "Cart is empty.")

        payment_str = self.view.input_payment.text().strip()
        
        try:
            if not payment_str:
                raise ValueError("Enter payment amount.")
            
            payment = float(payment_str)
            if payment < self.current_grand_total:
                raise ValueError("Payment is less than Grand Total.")

            self.db.finalize_sale(self.current_receipt_id, payment)
            
            change = payment - self.current_grand_total
            QMessageBox.information(self.view, "Transaction Complete", 
                                    f"Sale Finalized.\n\nAmount Paid: ₱{payment:.2f}\nChange: ₱{change:.2f}")
            
            self.current_receipt_id = None
            self.current_grand_total = 0.0
            self.view.reset_ui()

        except ValueError as ve:
            QMessageBox.warning(self.view, "Payment Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error", str(e))

    def cancel_transaction(self):
        if not self.current_receipt_id:
            return

        confirm = QMessageBox.question(self.view, "Cancel Transaction", 
                                       "Are you sure you want to void this transaction?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.db.cancel_sale(self.current_receipt_id)
                self.current_receipt_id = None
                self.current_grand_total = 0.0
                self.view.reset_ui()
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to cancel sale: {str(e)}")