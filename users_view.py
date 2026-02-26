from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                             QComboBox, QGridLayout, QHeaderView, QGroupBox, QSplitter, QAbstractItemView)

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
        
        staff_layout.addWidget(QLabel("<b>Staff Directory (Admins & Cashiers)</b>"))
        self.table_staff = QTableWidget()
        self.table_staff.setColumnCount(5)
        self.table_staff.setHorizontalHeaderLabels(["ID", "Name", "Role", "Status", "Type"])
        self.table_staff.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_staff.verticalHeader().setVisible(False)
        self.table_staff.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_staff.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        staff_layout.addWidget(self.table_staff)

        staff_form = QGroupBox("Update Staff Role")
        s_form_layout = QGridLayout()
        self.input_staff_id = QLineEdit()
        self.input_staff_id.setReadOnly(True)
        self.input_staff_type = QLineEdit()
        self.input_staff_type.setReadOnly(True)
        self.combo_role = QComboBox()
        self.combo_role.addItems(["Admin", "Editor"]) # Cashier roles are fixed by table structure
        
        s_form_layout.addWidget(QLabel("Selected ID:"), 0, 0)
        s_form_layout.addWidget(self.input_staff_id, 0, 1)
        s_form_layout.addWidget(QLabel("Type:"), 0, 2)
        s_form_layout.addWidget(self.input_staff_type, 0, 3)
        s_form_layout.addWidget(QLabel("New Role:"), 1, 0)
        s_form_layout.addWidget(self.combo_role, 1, 1)

        self.btn_update_role = QPushButton("Update Role")
        self.btn_disable_staff = QPushButton("Disable User")
        self.btn_disable_staff.setObjectName("btn_delete")
        s_form_layout.addWidget(self.btn_update_role, 1, 2)
        s_form_layout.addWidget(self.btn_disable_staff, 1, 3)
        
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
        
        c_form_layout.addWidget(QLabel("First Name:"), 0, 0)
        c_form_layout.addWidget(self.input_fname, 0, 1)
        c_form_layout.addWidget(QLabel("Last Name:"), 0, 2)
        c_form_layout.addWidget(self.input_lname, 0, 3)
        c_form_layout.addWidget(QLabel("Contact:"), 1, 0)
        c_form_layout.addWidget(self.input_contact, 1, 1)
        c_form_layout.addWidget(QLabel("Email:"), 1, 2)
        c_form_layout.addWidget(self.input_email, 1, 3)

        c_btns = QHBoxLayout()
        self.btn_add_cust = QPushButton("Add Customer")
        self.btn_disable_cust = QPushButton("Disable Selected")
        self.btn_disable_cust.setObjectName("btn_delete")
        self.btn_clear_cust = QPushButton("Clear Form")
        self.btn_clear_cust.setObjectName("btn_clear")
        
        c_btns.addWidget(self.btn_add_cust)
        c_btns.addWidget(self.btn_disable_cust)
        c_btns.addWidget(self.btn_clear_cust)
        c_form_layout.addLayout(c_btns, 2, 0, 1, 4)

        cust_form.setLayout(c_form_layout)
        cust_layout.addWidget(cust_form)

        splitter.addWidget(staff_widget)
        splitter.addWidget(cust_widget)
        main_layout.addWidget(splitter)