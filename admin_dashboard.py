from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QFrame, QLabel
)
from PyQt6.QtCore import Qt

from styles import APP_STYLE
from database.db_manager import DatabaseManager
from auth.context import AdminContext

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
        self.setWindowTitle("Retail POS - Admin Dashboard")
        self.resize(1366, 768)
        self.setStyleSheet(APP_STYLE)

        self.db = db
        self.operator = operator

        if not self.db.is_admin_active(self.operator.admin_account_id):
            raise SystemExit(f"Admin ID {self.operator.admin_account_id} is inactive. Access Denied.")

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --------------------
        # Dark, Industrial Sidebar
        # --------------------
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)

        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 20, 0, 0)
        sb_layout.setSpacing(0)

        # Branding / User Info block
        brand_box = QVBoxLayout()
        brand_box.setContentsMargins(20, 0, 20, 20)
        brand_box.setSpacing(4)
        
        lbl_brand = QLabel("ADMIN DASHBOARD")
        lbl_brand.setObjectName("SidebarTitle")
        
        lbl_user = QLabel(f"OP ID: {self.operator.admin_account_id}")
        lbl_user.setObjectName("SidebarMeta")

        brand_box.addWidget(lbl_brand)
        brand_box.addWidget(lbl_user)
        sb_layout.addLayout(brand_box)

        # Navigation
        self.btn_nav_products = self.create_nav_button("CATALOG")
        self.btn_nav_inventory = self.create_nav_button("INVENTORY")
        self.btn_nav_refs = self.create_nav_button("REFERENCES")
        self.btn_nav_registers = self.create_nav_button("REGISTERS")
        self.btn_nav_users = self.create_nav_button("USERS")
        self.btn_nav_reports = self.create_nav_button("REPORTS")

        self._nav_buttons = [
            self.btn_nav_products,
            self.btn_nav_inventory,
            self.btn_nav_refs,
            self.btn_nav_registers,
            self.btn_nav_users,
            self.btn_nav_reports,
        ]

        for b in self._nav_buttons:
            sb_layout.addWidget(b)

        sb_layout.addStretch()

        # --------------------
        # Main Content Area
        # --------------------
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        self.lbl_page_title = QLabel("")
        self.lbl_page_title.setObjectName("Header")
        content_layout.addWidget(self.lbl_page_title)

        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # --------------------
        # Pages + Controllers
        # --------------------
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

        root.addWidget(sidebar)
        root.addWidget(content)

        # --------------------
        # Navigation Wiring
        # --------------------
        self.btn_nav_products.clicked.connect(lambda: self.switch_tab(0, self.btn_nav_products, "PRODUCT CATALOG"))
        self.btn_nav_inventory.clicked.connect(lambda: self.switch_tab(1, self.btn_nav_inventory, "INVENTORY MANAGEMENT"))
        self.btn_nav_refs.clicked.connect(lambda: self.switch_tab(2, self.btn_nav_refs, "CATEGORIES & SUPPLIERS"))
        self.btn_nav_registers.clicked.connect(lambda: self.switch_tab(5, self.btn_nav_registers, "REGISTER TERMINALS"))
        self.btn_nav_users.clicked.connect(lambda: self.switch_tab(4, self.btn_nav_users, "USER MANAGEMENT"))
        self.btn_nav_reports.clicked.connect(lambda: self.switch_tab(3, self.btn_nav_reports, "FINANCIAL REPORTS"))

        self.btn_nav_products.clicked.connect(self.product_controller.load_dropdowns)
        self.btn_nav_products.clicked.connect(self.product_controller.load_table_data)
        self.btn_nav_inventory.clicked.connect(self.inv_controller.load_data)
        self.btn_nav_refs.clicked.connect(self.refs_controller.load_data)
        self.btn_nav_registers.clicked.connect(self.reg_controller.load_data)
        self.btn_nav_users.clicked.connect(self.usr_controller.load_data)
        self.btn_nav_reports.clicked.connect(self.rep_controller.load_data)

        # Initialize to first tab
        self.switch_tab(0, self.btn_nav_products, "PRODUCT CATALOG")
        self.btn_nav_products.setFocus()

    def create_nav_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return btn

    def switch_tab(self, index: int, active_btn: QPushButton, title: str) -> None:
        self.stacked_widget.setCurrentIndex(index)
        self.lbl_page_title.setText(title)

        for btn in self._nav_buttons:
            btn.setChecked(False)
        active_btn.setChecked(True)

    def keyPressEvent(self, event) -> None:
        key = event.key()
        fw = self.focusWidget()

        if fw in self._nav_buttons:
            idx = self._nav_buttons.index(fw)

            if key == Qt.Key.Key_Down:
                self._nav_buttons[(idx + 1) % len(self._nav_buttons)].setFocus()
                event.accept()
                return

            if key == Qt.Key.Key_Up:
                self._nav_buttons[(idx - 1) % len(self._nav_buttons)].setFocus()
                event.accept()
                return

            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                fw.click()
                event.accept()
                return

        super().keyPressEvent(event)