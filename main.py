# main.py

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel)

from styles import APP_STYLE
from database.db_manager import DatabaseManager
from views.product_view import ProductView
from controllers.product_controller import ProductController
from views.references_view import ReferencesView
from controllers.references_controller import ReferencesController
from views.inventory_view import InventoryView
from controllers.inventory_controller import InventoryController
from views.pos_view import POSView
from controllers.pos_controller import POSController
from views.reports_view import ReportsView
from controllers.reports_controller import ReportsController
from views.users_view import UsersView
from controllers.users_controller import UsersController

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supermarket POS & Inventory System")
        self.resize(1280, 800)
        self.setStyleSheet(APP_STYLE)

        self.db = DatabaseManager(user="root", password="")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(0)

        title = QLabel(" Retail Admin\n Dashboard")
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(30)

        self.btn_nav_pos = self.create_nav_button("Point of Sale")
        self.btn_nav_products = self.create_nav_button("Product Management")
        self.btn_nav_inventory = self.create_nav_button("Inventory Management")
        self.btn_nav_refs = self.create_nav_button("Categories and Suppliers")
        self.btn_nav_reports = self.create_nav_button("Sales Reports")
        self.btn_nav_users = self.create_nav_button("User Management")
        
        sidebar_layout.addWidget(self.btn_nav_pos)
        sidebar_layout.addWidget(self.btn_nav_products)
        sidebar_layout.addWidget(self.btn_nav_inventory)
        sidebar_layout.addWidget(self.btn_nav_refs)
        sidebar_layout.addWidget(self.btn_nav_reports)
        sidebar_layout.addWidget(self.btn_nav_users)
        sidebar_layout.addStretch()

        # --- Main View Area ---
        self.stacked_widget = QStackedWidget()

        self.pos_view = POSView()
        self.pos_controller = POSController(self.pos_view, self.db)
        
        self.product_view = ProductView()
        self.product_controller = ProductController(self.product_view, self.db)

        self.refs_view = ReferencesView()
        self.refs_controller = ReferencesController(self.refs_view, self.db)
        
        self.inv_view = InventoryView()
        self.inv_controller = InventoryController(self.inv_view, self.db)
        
        self.rep_view = ReportsView()
        self.rep_controller = ReportsController(self.rep_view, self.db)

        self.usr_view = UsersView()
        self.usr_controller = UsersController(self.usr_view, self.db)

        # Order must match switch_tab index
        self.stacked_widget.addWidget(self.pos_view)   # Index 0
        self.stacked_widget.addWidget(self.product_view)      # Index 1
        self.stacked_widget.addWidget(self.inv_view)          # Index 2
        self.stacked_widget.addWidget(self.refs_view)         # Index 3
        self.stacked_widget.addWidget(self.rep_view)       # 4
        self.stacked_widget.addWidget(self.usr_view)       # 5

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

        # --- Connections ---
        self.btn_nav_pos.clicked.connect(lambda: self.switch_tab(0, self.btn_nav_pos))
        self.btn_nav_products.clicked.connect(lambda: self.switch_tab(1, self.btn_nav_products))
        self.btn_nav_inventory.clicked.connect(lambda: self.switch_tab(2, self.btn_nav_inventory))
        self.btn_nav_refs.clicked.connect(lambda: self.switch_tab(3, self.btn_nav_refs))
        self.btn_nav_reports.clicked.connect(lambda: self.switch_tab(4, self.btn_nav_reports))
        self.btn_nav_users.clicked.connect(lambda: self.switch_tab(5, self.btn_nav_users))

        # Refresh dependent data when tabs are clicked
        self.btn_nav_products.clicked.connect(self.product_controller.load_dropdowns)
        self.btn_nav_products.clicked.connect(self.product_controller.load_table_data)
        self.btn_nav_inventory.clicked.connect(self.inv_controller.load_data)
        self.btn_nav_refs.clicked.connect(self.refs_controller.load_data)
        self.btn_nav_reports.clicked.connect(self.rep_controller.load_data)
        self.btn_nav_users.clicked.connect(self.usr_controller.load_data)

        self.switch_tab(1, self.btn_nav_products)

    def create_nav_button(self, text):
        btn = QPushButton(text)
        btn.setCheckable(True)
        return btn

    def switch_tab(self, index, active_btn):
        self.stacked_widget.setCurrentIndex(index)
        for btn in [self.btn_nav_pos, self.btn_nav_products, self.btn_nav_inventory, 
                    self.btn_nav_refs, self.btn_nav_reports, self.btn_nav_users]:
            btn.setChecked(False)
        active_btn.setChecked(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())