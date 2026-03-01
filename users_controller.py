# d:\PythonProjects\GroceryStoreInventoryPOS\controllers\users_controller.py
from PyQt6.QtWidgets import QTableWidgetItem

from controllers.base_controller import BaseController


class UsersController(BaseController):
    def __init__(self, view, db_manager, operator):
        super().__init__(view)
        self.db = db_manager
        self.operator = operator
        self._require_admin_context()

        self.view.table_staff.itemSelectionChanged.connect(self.select_staff)
        self.view.btn_update_role.clicked.connect(self.toggle_staff_role)
        self.view.btn_set_staff_status.clicked.connect(self.set_staff_status)

        self.view.table_cust.itemSelectionChanged.connect(self.select_cust)
        self.view.btn_add_cust.clicked.connect(self.add_customer)
        self.view.btn_set_cust_status.clicked.connect(self.set_customer_status)
        self.view.btn_clear_cust.clicked.connect(self.clear_cust)

        self.load_data()

    def _require_admin_context(self) -> None:
        if not hasattr(self.operator, "admin_account_id"):
            raise TypeError("UsersController requires an AdminContext with admin_account_id.")

    def _require_active_admin(self) -> None:
        if not self.db.is_admin_active(int(self.operator.admin_account_id)):
            raise ValueError(f"Admin account {self.operator.admin_account_id} is inactive. Action blocked.")

    def load_data(self) -> None:
        try:
            self._require_active_admin()

            staff = self.db.get_staff_list()
            self.view.table_staff.setRowCount(0)
            for row, user in enumerate(staff):
                self.view.table_staff.insertRow(row)
                self.view.table_staff.setItem(row, 0, QTableWidgetItem(str(user.get("ID") or "")))
                self.view.table_staff.setItem(row, 1, QTableWidgetItem(str(user.get("Name") or "")))
                self.view.table_staff.setItem(row, 2, QTableWidgetItem(str(user.get("Role") or "")))
                self.view.table_staff.setItem(row, 3, QTableWidgetItem(str(user.get("Status") or "")))

            custs = self.db.get_customer_list()
            self.view.table_cust.setRowCount(0)
            for row, c in enumerate(custs):
                self.view.table_cust.insertRow(row)
                self.view.table_cust.setItem(row, 0, QTableWidgetItem(str(c.get("CustomerID") or "")))
                self.view.table_cust.setItem(row, 1, QTableWidgetItem(str(c.get("FirstName") or "")))
                self.view.table_cust.setItem(row, 2, QTableWidgetItem(str(c.get("LastName") or "")))
                self.view.table_cust.setItem(row, 3, QTableWidgetItem(str(c.get("ContactNumber") or "")))
                self.view.table_cust.setItem(row, 4, QTableWidgetItem(str(c.get("Email") or "")))
                self.view.table_cust.setItem(row, 5, QTableWidgetItem(str(c.get("Status") or "")))

            self._clear_staff_form()
            self.clear_cust()

        except Exception as e:
            self._error("Users", f"Failed to load users.\n\n{e}")

    # ---------------- Staff ----------------

    def _clear_staff_form(self) -> None:
        self.view.table_staff.clearSelection()
        self.view.input_staff_id.clear()
        self.view.input_staff_role.clear()

        self.view.combo_staff_status.setCurrentText("Active")
        self.view.combo_staff_status.setEnabled(False)

        self.view.btn_update_role.setEnabled(False)
        self.view.btn_set_staff_status.setEnabled(False)
        self.view.btn_update_role.setText("Change Role")

    def select_staff(self) -> None:
        items = self.view.table_staff.selectedItems()
        if not items:
            return

        r = items[0].row()
        account_id = self.view.table_staff.item(r, 0).text().strip()
        role = self.view.table_staff.item(r, 2).text().strip()
        status = self.view.table_staff.item(r, 3).text().strip()

        self.view.input_staff_id.setText(account_id)
        self.view.input_staff_role.setText(role)

        self.view.combo_staff_status.setEnabled(True)
        self.view.combo_staff_status.setCurrentText(status)
        self.view.btn_set_staff_status.setEnabled(True)

        self.view.btn_update_role.setEnabled(True)
        if role == "Admin":
            self.view.btn_update_role.setText("Change Role to Cashier")
        elif role == "Cashier":
            self.view.btn_update_role.setText("Change Role to Admin")
        else:
            self.view.btn_update_role.setText("Change Role")

    def toggle_staff_role(self) -> None:
        try:
            self._require_active_admin()

            account_id = self._parse_int("Selected Account ID", self.view.input_staff_id.text())
            current_role = (self.view.input_staff_role.text() or "").strip()

            if current_role == "Admin":
                new_role = "Cashier"
            elif current_role == "Cashier":
                new_role = "Admin"
            else:
                raise ValueError("Selected staff role is invalid.")

            if not self._confirm("Change Role", f"Change role of Account {account_id} to {new_role}?"):
                return

            self.db.update_user_role(account_id, new_role)
            self._info("Users", f"Role updated to {new_role}.")
            self.load_data()

        except ValueError as ve:
            self._warn("Users", str(ve))
        except Exception as e:
            self._error("Users", f"Failed to update role.\n\n{e}")

    def set_staff_status(self) -> None:
        try:
            self._require_active_admin()

            account_id = self._parse_int("Selected Account ID", self.view.input_staff_id.text())
            new_status = (self.view.combo_staff_status.currentText() or "").strip()

            if not self._confirm("Set Staff Status", f"Set Account {account_id} status to {new_status}?"):
                return

            self.db.set_user_status(account_id, new_status)
            self._info("Users", "Staff status updated.")
            self.load_data()

        except ValueError as ve:
            self._warn("Users", str(ve))
        except Exception as e:
            self._error("Users", f"Failed to update staff status.\n\n{e}")

    # ---------------- Customers ----------------

    def clear_cust(self) -> None:
        self.view.table_cust.clearSelection()
        self.view.input_cust_id.clear()
        self.view.input_cust_id.setPlaceholderText("New")
        self.view.input_fname.clear()
        self.view.input_lname.clear()
        self.view.input_contact.clear()
        self.view.input_email.clear()

        self.view.combo_cust_status.setCurrentText("Active")
        self.view.combo_cust_status.setEnabled(False)
        self.view.btn_set_cust_status.setEnabled(False)

        self.view.btn_add_cust.setEnabled(True)

    def select_cust(self) -> None:
        items = self.view.table_cust.selectedItems()
        if not items:
            return

        r = items[0].row()
        cust_id = self.view.table_cust.item(r, 0).text()
        fname = self.view.table_cust.item(r, 1).text()
        lname = self.view.table_cust.item(r, 2).text()
        contact = self.view.table_cust.item(r, 3).text()
        email = self.view.table_cust.item(r, 4).text()
        status = self.view.table_cust.item(r, 5).text()

        self.view.input_cust_id.setText(cust_id)
        self.view.input_fname.setText(fname)
        self.view.input_lname.setText(lname)
        self.view.input_contact.setText(contact)
        self.view.input_email.setText(email)
        self.view.combo_cust_status.setCurrentText(status)

        self.view.btn_add_cust.setEnabled(False)
        self.view.combo_cust_status.setEnabled(True)
        self.view.btn_set_cust_status.setEnabled(True)

    def add_customer(self) -> None:
        try:
            self._require_active_admin()

            fname = (self.view.input_fname.text() or "").strip()
            lname = (self.view.input_lname.text() or "").strip()
            contact = (self.view.input_contact.text() or "").strip() or None
            email = (self.view.input_email.text() or "").strip() or None

            if not fname or not lname:
                raise ValueError("First Name and Last Name are required.")

            self.db.add_customer(fname, lname, contact, email)
            self._info("Users", "Customer added.")
            self.load_data()

        except ValueError as ve:
            self._warn("Users", str(ve))
        except Exception as e:
            self._error("Users", f"Failed to add customer.\n\n{e}")

    def set_customer_status(self) -> None:
        try:
            self._require_active_admin()

            customer_id = self._parse_int("Selected Customer ID", self.view.input_cust_id.text())
            new_status = (self.view.combo_cust_status.currentText() or "").strip()

            if not self._confirm("Set Customer Status", f"Set Customer {customer_id} status to {new_status}?"):
                return

            self.db.set_customer_status(customer_id, new_status)
            self._info("Users", "Customer status updated.")
            self.load_data()

        except ValueError as ve:
            self._warn("Users", str(ve))
        except Exception as e:
            self._error("Users", f"Failed to update customer status.\n\n{e}")