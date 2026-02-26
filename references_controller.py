# controllers/references_controller.py

from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

class ReferencesController:
    def __init__(self, view, db_manager):
        self.view = view
        self.db = db_manager
        
        self.view.btn_add_cat.clicked.connect(self.add_category)
        self.view.btn_upd_cat.clicked.connect(self.update_category)
        self.view.btn_clear_cat.clicked.connect(self.clear_cat)
        self.view.cat_table.itemSelectionChanged.connect(self.select_cat)

        self.view.btn_add_sup.clicked.connect(self.add_supplier)
        self.view.btn_upd_sup.clicked.connect(self.update_supplier)
        self.view.btn_clear_sup.clicked.connect(self.clear_sup)
        self.view.sup_table.itemSelectionChanged.connect(self.select_sup)

        self.load_data()

    def load_data(self):
        try:
            # Load Categories
            cats = self.db.get_categories() # Assuming your DB manager fetches all categories
            self.view.cat_table.setRowCount(0)
            for row, cat in enumerate(cats):
                self.view.cat_table.insertRow(row)
                self.view.cat_table.setItem(row, 0, QTableWidgetItem(str(cat['CategoryID'])))
                self.view.cat_table.setItem(row, 1, QTableWidgetItem(cat['CategoryName']))
                self.view.cat_table.setItem(row, 2, QTableWidgetItem(cat.get('Status', 'Active')))

            # Load Suppliers
            sups = self.db.get_suppliers()
            self.view.sup_table.setRowCount(0)
            for row, sup in enumerate(sups):
                self.view.sup_table.insertRow(row)
                self.view.sup_table.setItem(row, 0, QTableWidgetItem(str(sup['SupplierID'])))
                self.view.sup_table.setItem(row, 1, QTableWidgetItem(sup['Name']))
                self.view.sup_table.setItem(row, 2, QTableWidgetItem(sup.get('ContactNumber', '')))
                self.view.sup_table.setItem(row, 3, QTableWidgetItem(sup.get('Address', '')))
        except Exception as e:
            pass # Silent fail on init if tables are empty

    # --- Category Logic ---
    def add_category(self):
        name = self.view.cat_name.text()
        if not name:
            return QMessageBox.warning(self.view, "Error", "Category name required.")
        self.db.add_category(name, self.view.cat_status.currentText())
        self.clear_cat()
        self.load_data()

    def update_category(self):
        c_id = self.view.cat_id.text()
        if not c_id: return
        self.db.update_category(int(c_id), self.view.cat_name.text(), self.view.cat_status.currentText())
        self.clear_cat()
        self.load_data()

    def select_cat(self):
        rows = self.view.cat_table.selectedItems()
        if rows:
            r = rows[0].row()
            self.view.cat_id.setText(self.view.cat_table.item(r, 0).text())
            self.view.cat_name.setText(self.view.cat_table.item(r, 1).text())
            self.view.cat_status.setCurrentText(self.view.cat_table.item(r, 2).text())

    def clear_cat(self):
        self.view.cat_id.clear()
        self.view.cat_name.clear()
        self.view.cat_status.setCurrentIndex(0)

    # --- Supplier Logic ---
    def add_supplier(self):
        name = self.view.sup_name.text()
        if not name: return QMessageBox.warning(self.view, "Error", "Supplier name required.")
        self.db.add_supplier(1, name, self.view.sup_contact.text(), self.view.sup_address.text())
        self.clear_sup()
        self.load_data()

    def update_supplier(self):
        s_id = self.view.sup_id.text()
        if not s_id: return
        self.db.update_supplier(int(s_id), self.view.sup_name.text(), self.view.sup_contact.text(), self.view.sup_address.text())
        self.clear_sup()
        self.load_data()

    def select_sup(self):
        rows = self.view.sup_table.selectedItems()
        if rows:
            r = rows[0].row()
            self.view.sup_id.setText(self.view.sup_table.item(r, 0).text())
            self.view.sup_name.setText(self.view.sup_table.item(r, 1).text())
            self.view.sup_contact.setText(self.view.sup_table.item(r, 2).text() if self.view.sup_table.item(r, 2) else "")
            self.view.sup_address.setText(self.view.sup_table.item(r, 3).text() if self.view.sup_table.item(r, 3) else "")

    def clear_sup(self):
        self.view.sup_id.clear()
        self.view.sup_name.clear()
        self.view.sup_contact.clear()
        self.view.sup_address.clear()