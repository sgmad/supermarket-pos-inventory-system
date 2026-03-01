# d:\PythonProjects\GroceryStoreInventoryPOS\controllers\references_controller.py
from PyQt6.QtWidgets import QTableWidgetItem

from controllers.base_controller import BaseController


class ReferencesController(BaseController):
    def __init__(self, view, db_manager, operator):
        super().__init__(view)
        self.operator = operator
        self._require_admin_context()
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

    def _require_admin_context(self) -> None:
        if not hasattr(self.operator, "admin_account_id"):
            raise TypeError("ReferencesController requires an AdminContext with admin_account_id.")

    def _require_active_admin(self) -> None:
        if not self.db.is_admin_active(int(self.operator.admin_account_id)):
            raise ValueError(f"Admin account {self.operator.admin_account_id} is inactive. Action blocked.")

    def load_data(self) -> None:
        try:
            self._require_active_admin()

            cats = self.db.get_categories_all()
            self.view.cat_table.setRowCount(0)
            for row, cat in enumerate(cats):
                self.view.cat_table.insertRow(row)
                self.view.cat_table.setItem(row, 0, QTableWidgetItem(str(cat.get("CategoryID") or "")))
                self.view.cat_table.setItem(row, 1, QTableWidgetItem(str(cat.get("CategoryName") or "")))
                self.view.cat_table.setItem(row, 2, QTableWidgetItem(str(cat.get("Status") or "Active")))

            sups = self.db.get_suppliers()
            self.view.sup_table.setRowCount(0)
            for row, sup in enumerate(sups):
                self.view.sup_table.insertRow(row)
                self.view.sup_table.setItem(row, 0, QTableWidgetItem(str(sup.get("SupplierID") or "")))
                self.view.sup_table.setItem(row, 1, QTableWidgetItem(str(sup.get("Name") or "")))
                self.view.sup_table.setItem(row, 2, QTableWidgetItem(str(sup.get("ContactNumber") or "")))
                self.view.sup_table.setItem(row, 3, QTableWidgetItem(str(sup.get("Address") or "")))

            self.clear_cat()
            self.clear_sup()

        except Exception as e:
            self._error("References", f"Failed to load reference data.\n\n{e}")

    # ---------------- Categories ----------------

    def add_category(self) -> None:
        try:
            self._require_active_admin()

            name = (self.view.cat_name.text() or "").strip()
            status = (self.view.cat_status.currentText() or "").strip()

            if not name:
                raise ValueError("Category name is required.")

            self.db.add_category(name, status)
            self._info("References", "Category added.")
            self.load_data()

        except ValueError as ve:
            self._warn("References", str(ve))
        except Exception as e:
            self._error("References", f"Failed to add category.\n\n{e}")

    def update_category(self) -> None:
        try:
            self._require_active_admin()

            category_id = self._parse_int("Selected Category ID", self.view.cat_id.text())
            name = (self.view.cat_name.text() or "").strip()
            status = (self.view.cat_status.currentText() or "").strip()

            if not name:
                raise ValueError("Category name is required.")

            self.db.update_category(category_id, name, status)
            self._info("References", "Category updated.")
            self.load_data()

        except ValueError as ve:
            self._warn("References", str(ve))
        except Exception as e:
            self._error("References", f"Failed to update category.\n\n{e}")

    def select_cat(self) -> None:
        items = self.view.cat_table.selectedItems()
        if not items:
            return
        r = items[0].row()
        self.view.cat_id.setText(self.view.cat_table.item(r, 0).text())
        self.view.cat_name.setText(self.view.cat_table.item(r, 1).text())
        self.view.cat_status.setCurrentText(self.view.cat_table.item(r, 2).text())

    def clear_cat(self) -> None:
        self.view.cat_table.clearSelection()
        self.view.cat_id.clear()
        self.view.cat_name.clear()
        self.view.cat_status.setCurrentIndex(0)

    # ---------------- Suppliers ----------------

    def add_supplier(self) -> None:
        try:
            self._require_active_admin()

            name = (self.view.sup_name.text() or "").strip()
            contact = (self.view.sup_contact.text() or "").strip() or None
            address = (self.view.sup_address.text() or "").strip() or None

            if not name:
                raise ValueError("Supplier name is required.")

            self.db.add_supplier(name, contact, address)
            self._info("References", "Supplier added.")
            self.load_data()

        except ValueError as ve:
            self._warn("References", str(ve))
        except Exception as e:
            self._error("References", f"Failed to add supplier.\n\n{e}")

    def update_supplier(self) -> None:
        try:
            self._require_active_admin()

            supplier_id = self._parse_int("Selected Supplier ID", self.view.sup_id.text())
            name = (self.view.sup_name.text() or "").strip()
            contact = (self.view.sup_contact.text() or "").strip() or None
            address = (self.view.sup_address.text() or "").strip() or None

            if not name:
                raise ValueError("Supplier name is required.")

            self.db.update_supplier(supplier_id, name, contact, address)
            self._info("References", "Supplier updated.")
            self.load_data()

        except ValueError as ve:
            self._warn("References", str(ve))
        except Exception as e:
            self._error("References", f"Failed to update supplier.\n\n{e}")

    def select_sup(self) -> None:
        items = self.view.sup_table.selectedItems()
        if not items:
            return
        r = items[0].row()
        self.view.sup_id.setText(self.view.sup_table.item(r, 0).text())
        self.view.sup_name.setText(self.view.sup_table.item(r, 1).text())
        self.view.sup_contact.setText(self.view.sup_table.item(r, 2).text() if self.view.sup_table.item(r, 2) else "")
        self.view.sup_address.setText(self.view.sup_table.item(r, 3).text() if self.view.sup_table.item(r, 3) else "")

    def clear_sup(self) -> None:
        self.view.sup_table.clearSelection()
        self.view.sup_id.clear()
        self.view.sup_name.clear()
        self.view.sup_contact.clear()
        self.view.sup_address.clear()