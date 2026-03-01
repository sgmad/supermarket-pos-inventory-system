# d:\PythonProjects\GroceryStoreInventoryPOS\controllers\pos_controller.py
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QDialog

from controllers.base_controller import BaseController
from views.login_dialog import LoginDialog
from auth.operator_context import AdminContext
from admin_dashboard import Dashboard


class POSController(BaseController):
    def __init__(self, view, db_manager, operator):
        super().__init__(view)
        self.operator = operator
        self._require_cashier_context()
        self.db = db_manager
        self.current_receipt_id = None
        self.current_grand_total = 0.0
        self._admin_windows: list[Dashboard] = []

        self._load_customers_for_pos()

        self.view.btn_add_item.clicked.connect(self.process_item)
        self.view.input_barcode.returnPressed.connect(self.process_item)

        self.view.btn_pay.clicked.connect(self.finalize_transaction)
        self.view.input_payment.returnPressed.connect(self.finalize_transaction)

        self.view.btn_cancel.clicked.connect(self.cancel_transaction)

        self.view.btn_manager.clicked.connect(self.open_manager_tools)
        self.view.btn_logout.clicked.connect(self.logout_or_lock)

    def _require_cashier_context(self) -> None:
        if not hasattr(self.operator, "cashier_account_id") or not hasattr(self.operator, "register_id"):
            raise TypeError("POSController requires a CashierContext with cashier_account_id and register_id.")

    def _ensure_cashier_and_register_ok(self) -> None:
        if not self.db.is_cashier_active(int(self.operator.cashier_account_id)):
            raise ValueError(f"Cashier account {self.operator.cashier_account_id} is inactive. Sales are blocked.")
        if not self.db.is_register_online(int(self.operator.register_id)):
            raise ValueError(f"Register {self.operator.register_id} is offline. Sales are blocked.")

    def _load_customers_for_pos(self) -> None:
        self.view.combo_customer.clear()
        self.view.combo_customer.addItem("Walk-in Customer", None)

        try:
            customers = self.db.get_customers_active_lite()
            for c in customers:
                cid = c.get("CustomerID")
                name = (c.get("DisplayName") or "").strip() or f"Customer {cid}"
                self.view.combo_customer.addItem(name, cid)
        except Exception:
            self.view.combo_customer.clear()
            self.view.combo_customer.addItem("Walk-in Customer", None)

    def _reset_sale_state(self) -> None:
        self.current_receipt_id = None
        self.current_grand_total = 0.0
        self.view.reset_ui()

    def _cancel_receipt_safely(self, receipt_id: int) -> None:
        try:
            self.db.cancel_sale(receipt_id)
        except Exception:
            pass

    def process_item(self) -> None:
        created_receipt_id = None

        try:
            self._ensure_cashier_and_register_ok()

            prod_id = self._parse_int("Product ID", self.view.input_barcode.text())
            qty = self._parse_int("Quantity", self.view.input_qty.text())
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero.")

            if self.current_receipt_id is None:
                customer_id = self.view.selected_customer_id()
                created_receipt_id = self.db.create_sale(
                    int(self.operator.cashier_account_id),
                    int(self.operator.register_id),
                    customer_id,
                )
                self.current_receipt_id = created_receipt_id

            summary = self.db.get_receipt_summary(self.current_receipt_id)
            if summary is None:
                raise RuntimeError("Receipt session is invalid. Sale creation failed.")

            self.db.add_sale_item(self.current_receipt_id, prod_id, qty)
            self.refresh_cart()

            self.view.input_barcode.clear()
            self.view.input_qty.setText("1")
            self.view.input_barcode.setFocus()

        except ValueError as ve:
            if created_receipt_id is not None:
                self._cancel_receipt_safely(created_receipt_id)
                self.current_receipt_id = None
            self._warn("POS", str(ve))

        except Exception as e:
            if created_receipt_id is not None:
                self._cancel_receipt_safely(created_receipt_id)
                self.current_receipt_id = None
            self._error("POS", f"Failed to add item.\n\n{e}")

    def refresh_cart(self) -> None:
        if not self.current_receipt_id:
            return

        try:
            items = self.db.get_receipt_items(self.current_receipt_id)
            self.view.table_cart.setRowCount(0)

            for row_idx, item in enumerate(items):
                self.view.table_cart.insertRow(row_idx)
                self.view.table_cart.setItem(row_idx, 0, QTableWidgetItem(str(item.get("ProductID") or "")))
                self.view.table_cart.setItem(row_idx, 1, QTableWidgetItem(str(item.get("ProductName") or "")))
                self.view.table_cart.setItem(row_idx, 2, QTableWidgetItem(str(item.get("Qty") or "")))
                self.view.table_cart.setItem(row_idx, 3, QTableWidgetItem(f"{float(item.get('UnitPrice') or 0):.2f}"))
                self.view.table_cart.setItem(row_idx, 4, QTableWidgetItem(f"{float(item.get('Subtotal') or 0):.2f}"))

            summary = self.db.get_receipt_summary(self.current_receipt_id)
            if summary:
                self.view.lbl_subtotal.setText(f"{float(summary.get('TotalAmount') or 0):.2f}")
                self.view.lbl_tax.setText(f"{float(summary.get('TaxAmount') or 0):.2f}")
                self.current_grand_total = float(summary.get("GrandTotal") or 0)
                self.view.lbl_grand_total.setText(f"{self.current_grand_total:.2f}")

        except Exception as e:
            self._error("POS", f"Failed to refresh cart.\n\n{e}")

    def finalize_transaction(self) -> None:
        if not self.current_receipt_id:
            self._warn("POS", "Cart is empty.")
            return

        try:
            self._ensure_cashier_and_register_ok()

            payment = self._parse_money("Payment amount", self.view.input_payment.text())

            summary = self.db.get_receipt_summary(self.current_receipt_id)
            if summary is None:
                raise RuntimeError("Receipt session is invalid. Cannot finalize sale.")

            self.current_grand_total = float(summary.get("GrandTotal") or 0)
            self.view.lbl_subtotal.setText(f"{float(summary.get('TotalAmount') or 0):.2f}")
            self.view.lbl_tax.setText(f"{float(summary.get('TaxAmount') or 0):.2f}")
            self.view.lbl_grand_total.setText(f"{self.current_grand_total:.2f}")

            if payment < self.current_grand_total:
                raise ValueError("Payment is less than Grand Total.")

            self.db.finalize_sale(self.current_receipt_id, payment)

            change = payment - self.current_grand_total
            self._info(
                "Transaction Complete",
                f"Sale Finalized.\n\nAmount Paid: ₱{payment:.2f}\nChange: ₱{change:.2f}",
            )

            self._reset_sale_state()

        except ValueError as ve:
            self._warn("POS", str(ve))
        except Exception as e:
            self._error("POS", f"Failed to finalize transaction.\n\n{e}")

    def cancel_transaction(self) -> None:
        if not self.current_receipt_id:
            return

        if not self._confirm("Cancel Transaction", "Void this transaction?"):
            return

        try:
            self.db.cancel_sale(self.current_receipt_id)
            self._reset_sale_state()
        except Exception as e:
            self._error("POS", f"Failed to cancel sale.\n\n{e}")

    def open_manager_tools(self) -> None:
        dlg = LoginDialog("Manager Login")
        result = dlg.exec()
        if result != QDialog.DialogCode.Accepted:
            return

        try:
            admin_id = self.db.authenticate_admin(dlg.username(), dlg.password())
        except Exception as e:
            self._warn("Manager Login Failed", str(e))
            return

        admin_ctx = AdminContext(admin_account_id=admin_id)
        win = Dashboard(self.db, admin_ctx)
        win.show()
        self._admin_windows.append(win)

    def logout_or_lock(self) -> None:
        if self.current_receipt_id is not None:
            ok = self._confirm(
                "Logout / Lock",
                "A transaction is currently open.\n\nLogging out will void the open transaction.\n\nContinue?",
            )
            if not ok:
                return

            try:
                self.db.cancel_sale(self.current_receipt_id)
            except Exception:
                pass

            self._reset_sale_state()

        self.view.close()