from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QPushButton, QLabel, QLineEdit,
    QGridLayout, QHeaderView, QGroupBox,
    QSplitter, QAbstractItemView
)
from PyQt6.QtCore import Qt


class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # --- Top: Current Stock Table ---
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        top_layout.addWidget(QLabel("<b>Current Stock</b>"))
        self.table_stock = QTableWidget()
        self.table_stock.setColumnCount(6)
        self.table_stock.setHorizontalHeaderLabels(
            ["Product ID", "Product Name", "Qty Available", "Reorder Level", "Low Stock", "Last Updated"]
        )
        self.table_stock.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_stock.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_stock.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_stock.setAlternatingRowColors(True)
        self.table_stock.verticalHeader().setVisible(False)
        top_layout.addWidget(self.table_stock)

        # --- Middle: Adjustment Controls ---
        control_group = QGroupBox("Stock Adjustment")
        control_layout = QGridLayout()

        self.input_prod_id = QLineEdit()
        self.input_prod_id.setReadOnly(True)

        self.input_prod_name = QLineEdit()
        self.input_prod_name.setReadOnly(True)

        self.input_qty = QLineEdit()
        self.input_qty.setPlaceholderText("Enter quantity to adjust")

        self.btn_stock_in = QPushButton("Stock In (Add)")
        self.btn_stock_in.setEnabled(False)

        self.btn_stock_out = QPushButton("Stock Out (Deduct)")
        self.btn_stock_out.setObjectName("btn_delete")
        self.btn_stock_out.setEnabled(False)

        control_layout.addWidget(QLabel("Selected ID:"), 0, 0)
        control_layout.addWidget(self.input_prod_id, 0, 1)
        control_layout.addWidget(QLabel("Product:"), 0, 2)
        control_layout.addWidget(self.input_prod_name, 0, 3)

        control_layout.addWidget(QLabel("Adjustment Qty:"), 1, 0)
        control_layout.addWidget(self.input_qty, 1, 1)
        control_layout.addWidget(self.btn_stock_in, 1, 2)
        control_layout.addWidget(self.btn_stock_out, 1, 3)

        control_group.setLayout(control_layout)
        top_layout.addWidget(control_group)

        # --- Bottom: Movement Logs Table ---
        bot_widget = QWidget()
        bot_layout = QVBoxLayout(bot_widget)
        bot_layout.setContentsMargins(0, 0, 0, 0)

        bot_layout.addWidget(QLabel("<b>Inventory Movement Logs</b>"))
        self.table_logs = QTableWidget()
        self.table_logs.setColumnCount(6)
        self.table_logs.setHorizontalHeaderLabels(["Date/Time", "Product", "Change", "Reason", "Prev Qty", "New Qty"])
        self.table_logs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_logs.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_logs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_logs.setAlternatingRowColors(True)
        self.table_logs.verticalHeader().setVisible(False)
        bot_layout.addWidget(self.table_logs)

        splitter.addWidget(top_widget)
        splitter.addWidget(bot_widget)
        main_layout.addWidget(splitter)