from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

class ProductController:
    def __init__(self, view, db_manager):
        self.view = view
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

    def load_dropdowns(self):
        try:
            categories = self.db.get_categories()
            self.view.combo_category.clear()
            for cat in categories:
                self.category_map[cat['CategoryName']] = cat['CategoryID']
                self.view.combo_category.addItem(cat['CategoryName'])

            suppliers = self.db.get_suppliers()
            self.view.combo_supplier.clear()
            for sup in suppliers:
                self.supplier_map[sup['Name']] = sup['SupplierID']
                self.view.combo_supplier.addItem(sup['Name'])
        except Exception as e:
            QMessageBox.critical(self.view, "Load Error", f"Failed to load dropdowns:\n{str(e)}")

    def load_table_data(self):
        try:
            self.current_products = self.db.view_product_list()
            self.view.table.setRowCount(0)
            
            for row_idx, product in enumerate(self.current_products):
                self.view.table.insertRow(row_idx)
                self.view.table.setItem(row_idx, 0, QTableWidgetItem(str(product['ProductID'])))
                self.view.table.setItem(row_idx, 1, QTableWidgetItem(product['ProductName']))
                self.view.table.setItem(row_idx, 2, QTableWidgetItem(str(product['CategoryName'])))
                self.view.table.setItem(row_idx, 3, QTableWidgetItem(str(product['SupplierName'])))
                self.view.table.setItem(row_idx, 4, QTableWidgetItem(f"{product['Price']:.2f}"))
                self.view.table.setItem(row_idx, 5, QTableWidgetItem(product['Status']))
                self.view.table.setItem(row_idx, 6, QTableWidgetItem(product['Availability']))
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error", f"Failed to load products:\n{str(e)}")

    def add_product(self):
        data = self.view.get_form_data()
        try:
            if not data['name'] or not data['price'] or not data['initial_qty']:
                raise ValueError("Name, Price, and Initial Qty are required fields.")

            cat_id = self.category_map.get(data['category'])
            sup_id = self.supplier_map.get(data['supplier'])

            self.db.add_product(
                supplier_id=sup_id,
                admin_id=1, 
                name=data['name'],
                category_id=cat_id,
                price=float(data['price']),
                status=data['status'],
                initial_qty=int(data['initial_qty']),
                reorder_level=int(data['reorder_level'] or 0)
            )
            QMessageBox.information(self.view, "Success", "Product added successfully.")
            self.view.clear_form()
            self.load_table_data()
        except ValueError as ve:
            QMessageBox.warning(self.view, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error", str(e))

    def update_product(self):
        data = self.view.get_form_data()
        try:
            if not data['product_id']:
                raise ValueError("No product selected.")

            cat_id = self.category_map.get(data['category'])
            sup_id = self.supplier_map.get(data['supplier'])

            self.db.update_product(
                product_id=int(data['product_id']),
                supplier_id=sup_id,
                admin_id=1,
                name=data['name'],
                category_id=cat_id,
                price=float(data['price']),
                status=data['status'],
                reorder_level=int(data['reorder_level'] or 0)
            )
            QMessageBox.information(self.view, "Success", "Product updated successfully.")
            self.view.clear_form()
            self.load_table_data()
        except ValueError as ve:
            QMessageBox.warning(self.view, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error", str(e))

    def delete_product(self):
        data = self.view.get_form_data()
        try:
            confirm = QMessageBox.question(self.view, "Confirm Disable", "Disable this product?", 
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.db.soft_delete_product(int(data['product_id']))
                QMessageBox.information(self.view, "Success", "Product status set to Inactive.")
                self.view.clear_form()
                self.load_table_data()
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error", str(e))

    def populate_form_from_selection(self):
        selected_rows = self.view.table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        product = self.current_products[row]
        
        self.view.input_id.setText(str(product['ProductID']))
        self.view.input_name.setText(product['ProductName'])
        self.view.input_price.setText(str(product['Price']))
        self.view.combo_status.setCurrentText(product['Status'])
        self.view.input_reorder_level.setText(str(product['ReorderLevel'] if product['ReorderLevel'] is not None else 0))
        
        if product['CategoryName']:
            self.view.combo_category.setCurrentText(product['CategoryName'])
        if product['SupplierName']:
            self.view.combo_supplier.setCurrentText(product['SupplierName'])
        
        self.view.input_initial_qty.clear()
        self.view.input_initial_qty.setEnabled(False)
        self.view.input_initial_qty.setPlaceholderText("Locked. Manage stock in Inventory Tab.")
        
        self.view.btn_add.setEnabled(False)
        self.view.btn_update.setEnabled(True)
        self.view.btn_delete.setEnabled(True)