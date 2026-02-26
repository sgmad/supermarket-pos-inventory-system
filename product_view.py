from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                             QComboBox, QGridLayout, QHeaderView, QGroupBox, QAbstractItemView)
from PyQt6.QtCore import Qt

class ProductView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Supplier", "Price (₱)", "Status", "Availability"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)
        main_layout.addWidget(self.table)

        form_group = QGroupBox("Product Management")
        form_layout = QGridLayout()
        form_layout.setContentsMargins(15, 20, 15, 15)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)

        self.input_id = QLineEdit()
        self.input_id.setReadOnly(True)
        self.input_id.setPlaceholderText("System Assigned")
        self.input_name = QLineEdit()
        self.combo_category = QComboBox()
        self.combo_supplier = QComboBox()
        
        form_layout.addWidget(QLabel("Product ID:"), 0, 0)
        form_layout.addWidget(self.input_id, 0, 1)
        form_layout.addWidget(QLabel("Product Name:"), 1, 0)
        form_layout.addWidget(self.input_name, 1, 1)
        form_layout.addWidget(QLabel("Category:"), 2, 0)
        form_layout.addWidget(self.combo_category, 2, 1)
        form_layout.addWidget(QLabel("Supplier:"), 3, 0)
        form_layout.addWidget(self.combo_supplier, 3, 1)

        self.input_price = QLineEdit()
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Active", "Inactive"])
        
        self.input_initial_qty = QLineEdit()
        self.input_initial_qty.setPlaceholderText("Required for new products")
        
        self.input_reorder_level = QLineEdit()
        self.input_reorder_level.setPlaceholderText("Threshold for low stock warning")

        form_layout.addWidget(QLabel("Price (₱):"), 0, 2)
        form_layout.addWidget(self.input_price, 0, 3)
        form_layout.addWidget(QLabel("System Status:"), 1, 2)
        form_layout.addWidget(self.combo_status, 1, 3)
        form_layout.addWidget(QLabel("Initial Quantity:"), 2, 2)
        form_layout.addWidget(self.input_initial_qty, 2, 3)
        form_layout.addWidget(QLabel("Reorder Level:"), 3, 2)
        form_layout.addWidget(self.input_reorder_level, 3, 3)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add New Product")
        self.btn_update = QPushButton("Update Selected")
        self.btn_update.setEnabled(False)
        self.btn_delete = QPushButton("Disable Selected")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.setEnabled(False)
        self.btn_clear = QPushButton("Clear Form")
        self.btn_clear.setObjectName("btn_clear")

        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_update)
        button_layout.addWidget(self.btn_delete)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_clear)
        
        main_layout.addLayout(button_layout)

    def get_form_data(self):
        return {
            "product_id": self.input_id.text(),
            "name": self.input_name.text(),
            "category": self.combo_category.currentText(),
            "supplier": self.combo_supplier.currentText(),
            "price": self.input_price.text(),
            "status": self.combo_status.currentText(),
            "initial_qty": self.input_initial_qty.text(),
            "reorder_level": self.input_reorder_level.text()
        }

    def clear_form(self):
        self.input_id.clear()
        self.input_name.clear()
        self.combo_category.setCurrentIndex(0)
        self.combo_supplier.setCurrentIndex(0)
        self.input_price.clear()
        self.combo_status.setCurrentIndex(0)
        
        self.input_initial_qty.clear()
        self.input_initial_qty.setEnabled(True)
        self.input_initial_qty.setPlaceholderText("Required for new products")
        
        self.input_reorder_level.clear()
        self.btn_add.setEnabled(True)
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.table.clearSelection()