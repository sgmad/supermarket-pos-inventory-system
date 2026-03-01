# d:\PythonProjects\GroceryStoreInventoryPOS\views\users_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QPushButton, QLabel, QLineEdit,
    QComboBox, QGridLayout, QHeaderView, QGroupBox, QSplitter, QAbstractItemView
)


class UsersView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        splitter = QSplitter()

        # --- Left: Staff Management ---
        staff_widget = QWidget()
        staff_layout = QVBoxLayout(staff_widget)

        staff_layout.addWidget(QLabel("<b>Staff Directory</b>"))
        self.table_staff = QTableWidget()
        self.table_staff.setColumnCount(4)
        self.table_staff.setHorizontalHeaderLabels(["Account ID", "Name", "Role", "Status"])
        self.table_staff.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_staff.verticalHeader().setVisible(False)
        self.table_staff.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_staff.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_staff.setAlternatingRowColors(True)
        staff_layout.addWidget(self.table_staff)

        staff_form = QGroupBox("Manage Staff")
        s_form_layout = QGridLayout()

        self.input_staff_id = QLineEdit()
        self.input_staff_id.setReadOnly(True)

        self.input_staff_role = QLineEdit()
        self.input_staff_role.setReadOnly(True)

        self.combo_staff_status = QComboBox()
        self.combo_staff_status.addItems(["Active", "Inactive", "Suspended"])

        self.btn_update_role = QPushButton("Change Role")
        self.btn_set_staff_status = QPushButton("Set Status")

        self.btn_update_role.setEnabled(False)
        self.btn_set_staff_status.setEnabled(False)
        self.combo_staff_status.setEnabled(False)

        s_form_layout.addWidget(QLabel("Account ID:"), 0, 0)
        s_form_layout.addWidget(self.input_staff_id, 0, 1)
        s_form_layout.addWidget(QLabel("Current Role:"), 0, 2)
        s_form_layout.addWidget(self.input_staff_role, 0, 3)

        s_form_layout.addWidget(QLabel("Status:"), 1, 0)
        s_form_layout.addWidget(self.combo_staff_status, 1, 1)
        s_form_layout.addWidget(self.btn_set_staff_status, 1, 2)

        s_form_layout.addWidget(QLabel("Role Change:"), 2, 0)
        s_form_layout.addWidget(self.btn_update_role, 2, 2)

        staff_form.setLayout(s_form_layout)
        staff_layout.addWidget(staff_form)

        # --- Right: Customer Management ---
        cust_widget = QWidget()
        cust_layout = QVBoxLayout(cust_widget)

        cust_layout.addWidget(QLabel("<b>Customer Database</b>"))
        self.table_cust = QTableWidget()
        self.table_cust.setColumnCount(6)
        self.table_cust.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Contact", "Email", "Status"])
        self.table_cust.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_cust.verticalHeader().setVisible(False)
        self.table_cust.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_cust.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_cust.setAlternatingRowColors(True)
        cust_layout.addWidget(self.table_cust)

        cust_form = QGroupBox("Add / Manage Customer")
        c_form_layout = QGridLayout()

        self.input_cust_id = QLineEdit()
        self.input_cust_id.setReadOnly(True)
        self.input_cust_id.setPlaceholderText("New")

        self.input_fname = QLineEdit()
        self.input_lname = QLineEdit()
        self.input_contact = QLineEdit()
        self.input_email = QLineEdit()

        self.combo_cust_status = QComboBox()
        self.combo_cust_status.addItems(["Active", "Inactive"])
        self.combo_cust_status.setEnabled(False)

        self.btn_add_cust = QPushButton("Add Customer")
        self.btn_set_cust_status = QPushButton("Set Status")
        self.btn_clear_cust = QPushButton("Clear Form")
        self.btn_clear_cust.setObjectName("btn_clear")

        self.btn_set_cust_status.setEnabled(False)

        c_form_layout.addWidget(QLabel("Customer ID:"), 0, 0)
        c_form_layout.addWidget(self.input_cust_id, 0, 1)
        c_form_layout.addWidget(QLabel("Status:"), 0, 2)
        c_form_layout.addWidget(self.combo_cust_status, 0, 3)

        c_form_layout.addWidget(QLabel("First Name:"), 1, 0)
        c_form_layout.addWidget(self.input_fname, 1, 1)
        c_form_layout.addWidget(QLabel("Last Name:"), 1, 2)
        c_form_layout.addWidget(self.input_lname, 1, 3)

        c_form_layout.addWidget(QLabel("Contact:"), 2, 0)
        c_form_layout.addWidget(self.input_contact, 2, 1)
        c_form_layout.addWidget(QLabel("Email:"), 2, 2)
        c_form_layout.addWidget(self.input_email, 2, 3)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_add_cust)
        btns.addWidget(self.btn_set_cust_status)
        btns.addStretch()
        btns.addWidget(self.btn_clear_cust)
        c_form_layout.addLayout(btns, 3, 0, 1, 4)

        cust_form.setLayout(c_form_layout)
        cust_layout.addWidget(cust_form)

        splitter.addWidget(staff_widget)
        splitter.addWidget(cust_widget)
        main_layout.addWidget(splitter)