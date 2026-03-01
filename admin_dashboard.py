# d:\PythonProjects\GroceryStoreInventoryPOS\admin_dashboard.py
import sys
from pathlib import Path

from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QFrame,
    QLabel,
    QMessageBox,
)

from styles import APP_STYLE
from database.db_manager import DatabaseManager
from auth.operator_context import AdminContext

from views.product_view import ProductView
from controllers.product_controller import ProductController

from views.references_view import ReferencesView
from controllers.references_controller import ReferencesController

from views.inventory_view import InventoryView
from controllers.inventory_controller import InventoryController

from views.reports_view import ReportsView
from controllers.reports_controller import ReportsController

from views.users_view import UsersView
from controllers.users_controller import UsersController

from views.registers_view import RegistersView
from controllers.registers_controller import RegistersController


class Dashboard(QMainWindow):
    def __init__(self, db: DatabaseManager, operator: AdminContext):
        super().__init__()
        self.setWindowTitle("Retail Admin Dashboard")
        self.resize(1280, 800)
        self.setStyleSheet(APP_STYLE)

        self.db = db
        self.operator = operator

        if not self.db.is_admin_active(self.operator.admin_account_id):
            raise SystemExit(
                f"Admin account {self.operator.admin_account_id} is inactive. Cannot start admin dashboard."
            )

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 12)
        sidebar_layout.setSpacing(0)

        title = QLabel(" Retail Admin\n Dashboard")
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(20)

        self.btn_nav_products = self.create_nav_button("Product Management")
        self.btn_nav_inventory = self.create_nav_button("Inventory Management")
        self.btn_nav_refs = self.create_nav_button("Categories and Suppliers")
        self.btn_nav_reports = self.create_nav_button("Sales Reports")
        self.btn_nav_users = self.create_nav_button("User Management")
        self.btn_nav_registers = self.create_nav_button("Register Management")

        sidebar_layout.addWidget(self.btn_nav_products)
        sidebar_layout.addWidget(self.btn_nav_inventory)
        sidebar_layout.addWidget(self.btn_nav_refs)
        sidebar_layout.addWidget(self.btn_nav_reports)
        sidebar_layout.addWidget(self.btn_nav_users)
        sidebar_layout.addWidget(self.btn_nav_registers)

        sidebar_layout.addSpacing(18)
        sidebar_layout.addWidget(QLabel(" Tools"))
        sidebar_layout.addSpacing(8)

        self.btn_launch_pos = self.create_nav_button("Open Cashier POS")
        self.btn_launch_pos.setCheckable(False)
        sidebar_layout.addWidget(self.btn_launch_pos)

        sidebar_layout.addStretch()

        self.stacked_widget = QStackedWidget()

        self.product_view = ProductView()
        self.product_controller = ProductController(self.product_view, self.db, self.operator)

        self.inv_view = InventoryView()
        self.inv_controller = InventoryController(self.inv_view, self.db, self.operator)

        self.refs_view = ReferencesView()
        self.refs_controller = ReferencesController(self.refs_view, self.db, self.operator)

        self.rep_view = ReportsView()
        self.rep_controller = ReportsController(self.rep_view, self.db, self.operator)

        self.usr_view = UsersView()
        self.usr_controller = UsersController(self.usr_view, self.db, self.operator)

        self.reg_view = RegistersView()
        self.reg_controller = RegistersController(self.reg_view, self.db, self.operator)

        self.stacked_widget.addWidget(self.product_view)  # 0
        self.stacked_widget.addWidget(self.inv_view)      # 1
        self.stacked_widget.addWidget(self.refs_view)     # 2
        self.stacked_widget.addWidget(self.rep_view)      # 3
        self.stacked_widget.addWidget(self.usr_view)      # 4
        self.stacked_widget.addWidget(self.reg_view)      # 5

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

        self.btn_nav_products.clicked.connect(lambda: self.switch_tab(0, self.btn_nav_products))
        self.btn_nav_inventory.clicked.connect(lambda: self.switch_tab(1, self.btn_nav_inventory))
        self.btn_nav_refs.clicked.connect(lambda: self.switch_tab(2, self.btn_nav_refs))
        self.btn_nav_reports.clicked.connect(lambda: self.switch_tab(3, self.btn_nav_reports))
        self.btn_nav_users.clicked.connect(lambda: self.switch_tab(4, self.btn_nav_users))
        self.btn_nav_registers.clicked.connect(lambda: self.switch_tab(5, self.btn_nav_registers))

        self.btn_nav_products.clicked.connect(self.product_controller.load_dropdowns)
        self.btn_nav_products.clicked.connect(self.product_controller.load_table_data)
        self.btn_nav_inventory.clicked.connect(self.inv_controller.load_data)
        self.btn_nav_refs.clicked.connect(self.refs_controller.load_data)
        self.btn_nav_reports.clicked.connect(self.rep_controller.load_data)
        self.btn_nav_users.clicked.connect(self.usr_controller.load_data)
        self.btn_nav_registers.clicked.connect(self.reg_controller.load_data)

        self.btn_launch_pos.clicked.connect(self.launch_cashier_pos)

        self.switch_tab(0, self.btn_nav_products)

    def create_nav_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        return btn

    def switch_tab(self, index: int, active_btn: QPushButton) -> None:
        self.stacked_widget.setCurrentIndex(index)
        for btn in [
            self.btn_nav_products,
            self.btn_nav_inventory,
            self.btn_nav_refs,
            self.btn_nav_reports,
            self.btn_nav_users,
            self.btn_nav_registers,
        ]:
            btn.setChecked(False)
        active_btn.setChecked(True)

    def launch_cashier_pos(self) -> None:
        script_path = Path(__file__).resolve().parent / "cashier_main.py"
        if not script_path.exists():
            QMessageBox.critical(self, "Launch Error", f"cashier_main.py was not found at:\n{script_path}")
            return

        started = QProcess.startDetached(sys.executable, [str(script_path)])
        if not started:
            QMessageBox.critical(
                self,
                "Launch Error",
                "Cashier POS did not start.\n\n"
                f"Python: {sys.executable}\nScript: {script_path}"
            )