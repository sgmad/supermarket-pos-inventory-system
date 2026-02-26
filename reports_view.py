from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLabel, QHeaderView, QSplitter, QAbstractItemView)
from PyQt6.QtCore import Qt

class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # --- Top: Aggregated Daily Sales ---
        daily_widget = QWidget()
        daily_layout = QVBoxLayout(daily_widget)
        daily_layout.setContentsMargins(0, 0, 0, 0)
        
        daily_layout.addWidget(QLabel("<b>Daily Sales Aggregation (Paid Transactions Only)</b>"))
        self.table_daily = QTableWidget()
        self.table_daily.setColumnCount(4)
        self.table_daily.setHorizontalHeaderLabels(["Sale Date", "Total Transactions", "Total Revenue (₱)", "Total Tax Collected (₱)"])
        self.table_daily.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_daily.verticalHeader().setVisible(False)
        self.table_daily.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_daily.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_daily.setAlternatingRowColors(True)
        daily_layout.addWidget(self.table_daily)

        # --- Bottom: Raw Receipt History ---
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)

        history_layout.addWidget(QLabel("<b>Raw Sales History (All Statuses)</b>"))
        self.table_history = QTableWidget()
        self.table_history.setColumnCount(6)
        self.table_history.setHorizontalHeaderLabels(["Receipt ID", "Date", "Cashier ID", "Grand Total (₱)", "Payment (₱)", "Status"])
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_history.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_history.setAlternatingRowColors(True)
        history_layout.addWidget(self.table_history)

        splitter.addWidget(daily_widget)
        splitter.addWidget(history_widget)
        main_layout.addWidget(splitter)