# d:\PythonProjects\GroceryStoreInventoryPOS\views\inventory_view.py

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton,
    QLabel, QLineEdit, QGridLayout, QHeaderView, QAbstractItemView, 
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator


class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter)

        # ====================
        # LEFT: Live Stock
        # ====================
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(15)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        lbl_search = QLabel("SEARCH:")
        lbl_search.setObjectName("LedgerLabel")
        self.input_search = QLineEdit()

        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.input_search, 1)
        left_layout.addLayout(search_layout)

        self.table_stock = QTableWidget()
        self.table_stock.setColumnCount(6)
        self.table_stock.setHorizontalHeaderLabels(
            ["Product ID", "Name", "Available", "Reorder", "Low Stock", "Last Updated"]
        )
        self.table_stock.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_stock.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_stock.setAlternatingRowColors(True)
        self.table_stock.verticalHeader().setVisible(False)
        self.table_stock.setSortingEnabled(True)

        sh = self.table_stock.horizontalHeader()
        sh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        sh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        sh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        sh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        sh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        sh.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        left_layout.addWidget(self.table_stock, stretch=1)
        splitter.addWidget(left_pane)

        # ====================
        # RIGHT: Adjustments & Logs
        # ====================
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(15)

        # --- Stock Adjustment Block ---
        lbl_adjust_title = QLabel("STOCK ADJUSTMENT")
        lbl_adjust_title.setObjectName("PanelTitle")

        adjust_frame = QFrame()
        adjust_frame.setObjectName("PanelFrame")
        grid = QGridLayout(adjust_frame)
        grid.setContentsMargins(15, 15, 15, 15)
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(15)

        self.input_prod_id = QLineEdit()
        self.input_prod_id.setReadOnly(True)

        self.input_prod_name = QLineEdit()
        self.input_prod_name.setReadOnly(True)

        self.input_qty = QLineEdit()
        self.input_qty.setValidator(QIntValidator(1, 999_999, self))
        self.input_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_stock_in = QPushButton("STOCK IN (+)")
        self.btn_stock_in.setObjectName("SuccessButton")
        self.btn_stock_in.setEnabled(False)

        self.btn_stock_out = QPushButton("STOCK OUT (-)")
        self.btn_stock_out.setObjectName("DangerButton")
        self.btn_stock_out.setEnabled(False)

        lbl_id = QLabel("Product ID:")
        lbl_id.setObjectName("LedgerLabel")
        lbl_name = QLabel("Name:")
        lbl_name.setObjectName("LedgerLabel")
        lbl_qty = QLabel("Qty to Adjust:")
        lbl_qty.setObjectName("LedgerLabel")

        grid.addWidget(lbl_id, 0, 0)
        grid.addWidget(self.input_prod_id, 0, 1)

        grid.addWidget(lbl_name, 1, 0)
        grid.addWidget(self.input_prod_name, 1, 1)

        grid.addWidget(lbl_qty, 2, 0)
        grid.addWidget(self.input_qty, 2, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addWidget(self.btn_stock_in)
        btn_row.addWidget(self.btn_stock_out)
        grid.addLayout(btn_row, 3, 0, 1, 2)

        adjust_section = QVBoxLayout()
        adjust_section.setSpacing(2)
        adjust_section.addWidget(lbl_adjust_title)
        adjust_section.addWidget(adjust_frame)
        right_layout.addLayout(adjust_section)

        # --- Movement Logs Block ---
        lbl_logs_title = QLabel("MOVEMENT LOGS")
        lbl_logs_title.setObjectName("PanelTitle")

        logs_frame = QFrame()
        logs_frame.setObjectName("PanelFrame")
        logs_layout = QVBoxLayout(logs_frame)
        logs_layout.setContentsMargins(15, 15, 15, 15)
        logs_layout.setSpacing(0)

        self.table_logs = QTableWidget()
        self.table_logs.setColumnCount(6)
        self.table_logs.setHorizontalHeaderLabels(["Timestamp", "Product", "Change", "Reason", "Prev", "New"])
        self.table_logs.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_logs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_logs.setAlternatingRowColors(True)
        self.table_logs.verticalHeader().setVisible(False)
        self.table_logs.setSortingEnabled(True)

        lh = self.table_logs.horizontalHeader()
        lh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        lh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        lh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        lh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        lh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        lh.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        logs_layout.addWidget(self.table_logs)

        logs_section = QVBoxLayout()
        logs_section.setSpacing(2)
        logs_section.addWidget(lbl_logs_title)
        logs_section.addWidget(logs_frame)
        right_layout.addLayout(logs_section, stretch=1)
        
        splitter.addWidget(right_pane)
        splitter.setSizes([650, 450])

        self.input_qty.returnPressed.connect(self._enter_primary_adjust)

    def _enter_primary_adjust(self) -> None:
        if self.btn_stock_in.isEnabled():
            self.btn_stock_in.click()