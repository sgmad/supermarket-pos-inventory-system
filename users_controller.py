from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

class UsersController:
    def __init__(self, view, db_manager):
        self.view = view
        self.db = db_manager
        
        # Staff Connections
        self.view.table_staff.itemSelectionChanged.connect(self.select_staff)
        self.view.btn_update_role.clicked.connect(self.update_role)
        self.view.btn_disable_staff.clicked.connect(self.disable_staff)

        # Customer Connections
        self.view.table_cust.itemSelectionChanged.connect(self.select_cust)
        self.view.btn_add_cust.clicked.connect(self.add_customer)
        self.view.btn_disable_cust.clicked.connect(self.disable_customer)
        self.view.btn_clear_cust.clicked.connect(self.clear_cust)

        self.load_data()

    def load_data(self):
        try:
            # Load Staff
            staff = self.db.get_staff_list()
            self.view.table_staff.setRowCount(0)
            for row, user in enumerate(staff):
                self.view.table_staff.insertRow(row)
                self.view.table_staff.setItem(row, 0, QTableWidgetItem(str(user['ID'])))
                self.view.table_staff.setItem(row, 1, QTableWidgetItem(user['Name']))
                self.view.table_staff.setItem(row, 2, QTableWidgetItem(user['Role']))
                self.view.table_staff.setItem(row, 3, QTableWidgetItem(user['Status']))
                self.view.table_staff.setItem(row, 4, QTableWidgetItem(user['AccountType']))

            # Load Customers
            custs = self.db.get_customer_list()
            self.view.table_cust.setRowCount(0)
            for row, c in enumerate(custs):
                self.view.table_cust.insertRow(row)
                self.view.table_cust.setItem(row, 0, QTableWidgetItem(str(c['CustomerID'])))
                self.view.table_cust.setItem(row, 1, QTableWidgetItem(c['FirstName']))
                self.view.table_cust.setItem(row, 2, QTableWidgetItem(c['LastName']))
                self.view.table_cust.setItem(row, 3, QTableWidgetItem(c['ContactNumber'] if c['ContactNumber'] else ""))
                self.view.table_cust.setItem(row, 4, QTableWidgetItem(c['Email'] if c['Email'] else ""))
                self.view.table_cust.setItem(row, 5, QTableWidgetItem(c['Status']))
        except Exception:
            pass 

    # --- Staff Logic ---
    def select_staff(self):
        rows = self.view.table_staff.selectedItems()
        if rows:
            r = rows[0].row()
            self.view.input_staff_id.setText(self.view.table_staff.item(r, 0).text())
            u_type = self.view.table_staff.item(r, 4).text()
            self.view.input_staff_type.setText(u_type)
            
            # Roles can only be updated for Admins based on the schema
            self.view.combo_role.setEnabled(u_type == 'Admin')

    def update_role(self):
        s_id = self.view.input_staff_id.text()
        s_type = self.view.input_staff_type.text()
        
        if not s_id or s_type != 'Admin':
            return QMessageBox.warning(self.view, "Invalid", "Select an Admin to change roles.")
        try:
            self.db.update_user_role(int(s_id), self.view.combo_role.currentText())
            self.load_data()
            QMessageBox.information(self.view, "Success", "Role updated.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", str(e))

    def disable_staff(self):
        s_id = self.view.input_staff_id.text()
        s_type = self.view.input_staff_type.text()
        if not s_id: return
        
        confirm = QMessageBox.question(self.view, "Confirm Disable", f"Disable this {s_type}?")
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if s_type == 'Admin':
                    self.db.disable_admin(int(s_id))
                else:
                    self.db.disable_cashier(int(s_id))
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self.view, "Error", str(e))

    # --- Customer Logic ---
    def select_cust(self):
        rows = self.view.table_cust.selectedItems()
        if rows:
            r = rows[0].row()
            self.view.input_cust_id.setText(self.view.table_cust.item(r, 0).text())
            self.view.btn_add_cust.setEnabled(False)

    def add_customer(self):
        fname = self.view.input_fname.text()
        lname = self.view.input_lname.text()
        contact = self.view.input_contact.text() or None
        email = self.view.input_email.text() or None

        if not fname or not lname:
            return QMessageBox.warning(self.view, "Error", "First and Last Name required.")
        
        try:
            self.db.add_customer(fname, lname, contact, email)
            self.clear_cust()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error", str(e))

    def disable_customer(self):
        c_id = self.view.input_cust_id.text()
        if not c_id: return
        
        try:
            self.db.disable_customer(int(c_id))
            self.clear_cust()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", str(e))

    def clear_cust(self):
        self.view.input_cust_id.clear()
        self.view.input_fname.clear()
        self.view.input_lname.clear()
        self.view.input_contact.clear()
        self.view.input_email.clear()
        self.view.btn_add_cust.setEnabled(True)
        self.view.table_cust.clearSelection()