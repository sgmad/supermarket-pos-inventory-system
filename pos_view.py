# d:\PythonProjects\GroceryStoreInventoryPOS\views\pos_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QPushButton, QLabel, QLineEdit, QAbstractItemView,
    QHeaderView, QGroupBox, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class POSView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Customer (optional)
        customer_group = QGroupBox("Customer (Optional)")
        customer_layout = QHBoxLayout()
        customer_layout.setContentsMargins(12, 10, 12, 12)

        self.combo_customer = QComboBox()
        self.combo_customer.setMinimumWidth(320)

        customer_layout.addWidget(QLabel("Customer:"))
        customer_layout.addWidget(self.combo_customer)
        customer_group.setLayout(customer_layout)
        left_layout.addWidget(customer_group)

        # Item Entry
        entry_group = QGroupBox("Scan / Enter Product")
        entry_layout = QHBoxLayout()
        entry_layout.setContentsMargins(12, 10, 12, 12)

        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Scan barcode or enter Product ID")

        self.input_qty = QLineEdit()
        self.input_qty.setPlaceholderText("Qty")
        self.input_qty.setText("1")
        self.input_qty.setFixedWidth(70)

        self.btn_add_item = QPushButton("Add Item")

        entry_layout.addWidget(QLabel("Code:"))
        entry_layout.addWidget(self.input_barcode)
        entry_layout.addWidget(QLabel("Qty:"))
        entry_layout.addWidget(self.input_qty)
        entry_layout.addWidget(self.btn_add_item)
        entry_group.setLayout(entry_layout)
        left_layout.addWidget(entry_group)

        # Cart
        self.table_cart = QTableWidget()
        self.table_cart.setColumnCount(5)
        self.table_cart.setHorizontalHeaderLabels(["ID", "Product Name", "Qty", "Unit Price", "Subtotal"])
        self.table_cart.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_cart.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_cart.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_cart.setAlternatingRowColors(True)
        left_layout.addWidget(self.table_cart)

        # Right Panel
        right_panel = QWidget()
        right_panel.setFixedWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Session identity
        self.lbl_session = QLabel("Not signed in")
        self.lbl_session.setWordWrap(True)
        right_layout.addWidget(self.lbl_session)

        totals_group = QGroupBox("Transaction Summary")
        totals_layout = QGridLayout()

        val_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        grand_font = QFont("Segoe UI", 18, QFont.Weight.Bold)

        self.lbl_subtotal = QLabel("0.00")
        self.lbl_subtotal.setFont(val_font)
        self.lbl_subtotal.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_tax = QLabel("0.00")
        self.lbl_tax.setFont(val_font)
        self.lbl_tax.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_grand_total = QLabel("0.00")
        self.lbl_grand_total.setFont(grand_font)
        self.lbl_grand_total.setStyleSheet("color: #27ae60;")
        self.lbl_grand_total.setAlignment(Qt.AlignmentFlag.AlignRight)

        totals_layout.addWidget(QLabel("Subtotal (₱):"), 0, 0)
        totals_layout.addWidget(self.lbl_subtotal, 0, 1)
        totals_layout.addWidget(QLabel("Tax (12% VAT):"), 1, 0)
        totals_layout.addWidget(self.lbl_tax, 1, 1)
        totals_layout.addWidget(QLabel("Grand Total (₱):"), 2, 0)
        totals_layout.addWidget(self.lbl_grand_total, 2, 1)

        totals_group.setLayout(totals_layout)
        right_layout.addWidget(totals_group)

        payment_group = QGroupBox("Payment")
        payment_layout = QVBoxLayout()
        payment_layout.setContentsMargins(12, 10, 12, 12)
        payment_layout.setSpacing(10)

        self.input_payment = QLineEdit()
        self.input_payment.setPlaceholderText("Enter Amount Received")
        self.input_payment.setFont(val_font)
        self.input_payment.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.btn_pay = QPushButton("Complete Sale")
        self.btn_pay.setStyleSheet("background-color: #27ae60; font-size: 14px; padding: 12px;")

        self.btn_cancel = QPushButton("Cancel Transaction")
        self.btn_cancel.setObjectName("btn_delete")

        payment_layout.addWidget(QLabel("Amount Tendered (₱):"))
        payment_layout.addWidget(self.input_payment)
        payment_layout.addWidget(self.btn_pay)
        payment_layout.addWidget(self.btn_cancel)

        payment_group.setLayout(payment_layout)
        right_layout.addWidget(payment_group)

        # Manager + Logout (always visible)
        self.btn_manager = QPushButton("Manager")
        self.btn_logout = QPushButton("Logout / Lock")

        self.btn_manager.setShortcut("F12")
        self.btn_pay.setShortcut("F9")
        self.btn_cancel.setShortcut("Esc")
        self.btn_logout.setShortcut("Ctrl+L")

        right_layout.addWidget(self.btn_manager)
        right_layout.addWidget(self.btn_logout)
        right_layout.addStretch()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def set_session_text(self, text: str) -> None:
        self.lbl_session.setText(text)

    def selected_customer_id(self):
        data = self.combo_customer.currentData()
        if data is None:
            return None
        try:
            return int(data)
        except (TypeError, ValueError):
            return None

    def reset_ui(self):
        self.input_barcode.clear()
        self.input_qty.setText("1")
        self.input_payment.clear()
        self.table_cart.setRowCount(0)
        self.lbl_subtotal.setText("0.00")
        self.lbl_tax.setText("0.00")
        self.lbl_grand_total.setText("0.00")
        self.input_barcode.setFocus()