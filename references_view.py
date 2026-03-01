from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit, QAbstractItemView,
                             QComboBox, QFormLayout, QHeaderView, QGroupBox, QSplitter)

class ReferencesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        splitter = QSplitter()

        # --- Categories Section ---
        cat_widget = QWidget()
        cat_layout = QVBoxLayout(cat_widget)
        
        self.cat_table = QTableWidget()
        self.cat_table.setColumnCount(3)
        self.cat_table.setHorizontalHeaderLabels(["ID", "Category Name", "Status"])
        self.cat_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cat_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        cat_layout.addWidget(QLabel("<b>Manage Categories</b>"))
        cat_layout.addWidget(self.cat_table)

        cat_form = QFormLayout()
        self.cat_id = QLineEdit()
        self.cat_id.setReadOnly(True)
        self.cat_name = QLineEdit()
        self.cat_status = QComboBox()
        self.cat_status.addItems(["Active", "Inactive"])
        
        cat_form.addRow("ID:", self.cat_id)
        cat_form.addRow("Name:", self.cat_name)
        cat_form.addRow("Status:", self.cat_status)
        cat_layout.addLayout(cat_form)

        cat_btns = QHBoxLayout()
        self.btn_add_cat = QPushButton("Add Category")
        self.btn_upd_cat = QPushButton("Update Category")
        self.btn_clear_cat = QPushButton("Clear")
        self.btn_clear_cat.setObjectName("btn_clear")
        cat_btns.addWidget(self.btn_add_cat)
        cat_btns.addWidget(self.btn_upd_cat)
        cat_btns.addWidget(self.btn_clear_cat)
        cat_layout.addLayout(cat_btns)

        # --- Suppliers Section ---
        sup_widget = QWidget()
        sup_layout = QVBoxLayout(sup_widget)
        
        self.sup_table = QTableWidget()
        self.sup_table.setColumnCount(4)
        self.sup_table.setHorizontalHeaderLabels(["ID", "Supplier Name", "Contact", "Address"])
        self.sup_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sup_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        sup_layout.addWidget(QLabel("<b>Manage Suppliers</b>"))
        sup_layout.addWidget(self.sup_table)

        sup_form = QFormLayout()
        self.sup_id = QLineEdit()
        self.sup_id.setReadOnly(True)
        self.sup_name = QLineEdit()
        self.sup_contact = QLineEdit()
        self.sup_address = QLineEdit()
        
        sup_form.addRow("ID:", self.sup_id)
        sup_form.addRow("Name:", self.sup_name)
        sup_form.addRow("Contact:", self.sup_contact)
        sup_form.addRow("Address:", self.sup_address)
        sup_layout.addLayout(sup_form)

        sup_btns = QHBoxLayout()
        self.btn_add_sup = QPushButton("Add Supplier")
        self.btn_upd_sup = QPushButton("Update Supplier")
        self.btn_clear_sup = QPushButton("Clear")
        self.btn_clear_sup.setObjectName("btn_clear")
        sup_btns.addWidget(self.btn_add_sup)
        sup_btns.addWidget(self.btn_upd_sup)
        sup_btns.addWidget(self.btn_clear_sup)
        sup_layout.addLayout(sup_btns)

        # Add to splitter
        splitter.addWidget(cat_widget)
        splitter.addWidget(sup_widget)
        main_layout.addWidget(splitter)