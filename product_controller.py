# d:\PythonProjects\GroceryStoreInventoryPOS\controllers\product_controller.py
from PyQt6.QtWidgets import QTableWidgetItem

from controllers.base_controller import BaseController


class ProductController(BaseController):
    def __init__(self, view, db_manager, operator):
        super().__init__(view)
        self.operator = operator
        self._require_admin_context()
        self.db = db_manager
        self.current_products = []

        self.category_map = {}
        self.supplier_map = {}

        self.view.btn_add.clicked.connect(self.add_product)
        self.view.btn_update.clicked.connect(self.update_product)
        self.view.btn_delete.clicked.connect(self.delete_product)
        self.view.btn_clear.clicked.connect(self.view.clear_form)
        self.view.table.itemSelectionChanged.connect(self.populate_form_from_selection)

        self.load_dropdowns()
        self.load_table_data()

    def _require_admin_context(self) -> None:
        if not hasattr(self.operator, "admin_account_id"):
            raise TypeError("ProductController requires an AdminContext with admin_account_id.")

    def _require_active_admin(self) -> None:
        if not self.db.is_admin_active(int(self.operator.admin_account_id)):
            raise ValueError(f"Admin account {self.operator.admin_account_id} is inactive. Action blocked.")

    def load_dropdowns(self) -> None:
        try:
            self._require_active_admin()

            categories = self.db.get_categories_active()
            self.view.combo_category.clear()
            self.category_map.clear()
            for cat in categories:
                self.category_map[cat["CategoryName"]] = int(cat["CategoryID"])
                self.view.combo_category.addItem(cat["CategoryName"])

            suppliers = self.db.get_suppliers()
            self.view.combo_supplier.clear()
            self.supplier_map.clear()

            self.view.combo_supplier.addItem("(None)")
            self.supplier_map["(None)"] = None

            for sup in suppliers:
                name = sup["Name"]
                self.supplier_map[name] = int(sup["SupplierID"])
                self.view.combo_supplier.addItem(name)

        except Exception as e:
            self._error("Products", f"Failed to load dropdowns.\n\n{e}")

    def load_table_data(self) -> None:
        try:
            self._require_active_admin()

            self.current_products = self.db.view_product_list()
            self.view.table.setRowCount(0)

            for row_idx, product in enumerate(self.current_products):
                self.view.table.insertRow(row_idx)
                self.view.table.setItem(row_idx, 0, QTableWidgetItem(str(product.get("ProductID") or "")))
                self.view.table.setItem(row_idx, 1, QTableWidgetItem(str(product.get("ProductName") or "")))
                self.view.table.setItem(row_idx, 2, QTableWidgetItem(str(product.get("CategoryName") or "")))
                self.view.table.setItem(row_idx, 3, QTableWidgetItem(str(product.get("SupplierName") or "")))
                self.view.table.setItem(row_idx, 4, QTableWidgetItem(f"{float(product.get('Price') or 0):.2f}"))
                self.view.table.setItem(row_idx, 5, QTableWidgetItem(str(product.get("Status") or "")))
                self.view.table.setItem(row_idx, 6, QTableWidgetItem(str(product.get("Availability") or "")))

        except Exception as e:
            self._error("Products", f"Failed to load products.\n\n{e}")

    def add_product(self) -> None:
        data = self.view.get_form_data()
        try:
            self._require_active_admin()

            name = (data.get("name") or "").strip()
            if not name:
                raise ValueError("Product Name is required.")

            price = self._parse_money("Price", data.get("price") or "")
            initial_qty = self._parse_int("Initial Quantity", data.get("initial_qty") or "")
            if initial_qty < 0:
                raise ValueError("Initial Quantity cannot be negative.")

            reorder_level = 0
            reorder_raw = (data.get("reorder_level") or "").strip()
            if reorder_raw:
                reorder_level = self._parse_int("Reorder Level", reorder_raw)
                if reorder_level < 0:
                    raise ValueError("Reorder Level cannot be negative.")

            cat_id = self.category_map.get(data.get("category") or "")
            if cat_id is None:
                raise ValueError("Category selection is invalid.")

            sup_id = self.supplier_map.get(data.get("supplier") or "(None)")

            self.db.add_product(
                supplier_id=sup_id,
                admin_account_id=int(self.operator.admin_account_id),
                name=name,
                category_id=int(cat_id),
                price=price,
                status=str(data.get("status") or "Active"),
                initial_qty=initial_qty,
                reorder_level=reorder_level,
            )

            self._info("Products", "Product added successfully.")
            self.view.clear_form()
            self.load_table_data()

        except ValueError as ve:
            self._warn("Products", str(ve))
        except Exception as e:
            self._error("Products", f"Failed to add product.\n\n{e}")

    def update_product(self) -> None:
        data = self.view.get_form_data()
        try:
            self._require_active_admin()

            product_id = self._parse_int("Selected Product ID", data.get("product_id") or "")

            name = (data.get("name") or "").strip()
            if not name:
                raise ValueError("Product Name is required.")

            price = self._parse_money("Price", data.get("price") or "")

            reorder_level = 0
            reorder_raw = (data.get("reorder_level") or "").strip()
            if reorder_raw:
                reorder_level = self._parse_int("Reorder Level", reorder_raw)
                if reorder_level < 0:
                    raise ValueError("Reorder Level cannot be negative.")

            cat_id = self.category_map.get(data.get("category") or "")
            if cat_id is None:
                raise ValueError("Category selection is invalid.")

            sup_id = self.supplier_map.get(data.get("supplier") or "(None)")

            self.db.update_product(
                product_id=product_id,
                supplier_id=sup_id,
                admin_account_id=int(self.operator.admin_account_id),
                name=name,
                category_id=int(cat_id),
                price=price,
                status=str(data.get("status") or "Active"),
                reorder_level=reorder_level,
            )

            self._info("Products", "Product updated successfully.")
            self.view.clear_form()
            self.load_table_data()

        except ValueError as ve:
            self._warn("Products", str(ve))
        except Exception as e:
            self._error("Products", f"Failed to update product.\n\n{e}")

    def delete_product(self) -> None:
        data = self.view.get_form_data()
        try:
            self._require_active_admin()

            product_id = self._parse_int("Selected Product ID", data.get("product_id") or "")

            if not self._confirm("Disable Product", "Disable this product?"):
                return

            self.db.soft_delete_product(product_id)
            self._info("Products", "Product was set to Inactive.")
            self.view.clear_form()
            self.load_table_data()

        except ValueError as ve:
            self._warn("Products", str(ve))
        except Exception as e:
            self._error("Products", f"Failed to disable product.\n\n{e}")

    def populate_form_from_selection(self) -> None:
        selected_items = self.view.table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        if row < 0 or row >= len(self.current_products):
            return

        product = self.current_products[row]

        self.view.input_id.setText(str(product.get("ProductID") or ""))
        self.view.input_name.setText(str(product.get("ProductName") or ""))
        self.view.input_price.setText(str(product.get("Price") or ""))

        self.view.combo_status.setCurrentText(str(product.get("Status") or "Active"))
        self.view.input_reorder_level.setText(str(product.get("ReorderLevel") or 0))

        if product.get("CategoryName"):
            self.view.combo_category.setCurrentText(str(product["CategoryName"]))

        supplier_name = product.get("SupplierName")
        self.view.combo_supplier.setCurrentText(str(supplier_name) if supplier_name else "(None)")

        self.view.input_initial_qty.clear()
        self.view.input_initial_qty.setEnabled(False)
        self.view.input_initial_qty.setPlaceholderText("Locked. Use Inventory Management to adjust stock.")

        self.view.btn_add.setEnabled(False)
        self.view.btn_update.setEnabled(True)
        self.view.btn_delete.setEnabled(True)