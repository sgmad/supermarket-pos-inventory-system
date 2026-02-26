APP_STYLE = """
QWidget {
    background-color: #ffffff;
    color: #212529;
    font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QStackedWidget {
    background-color: #ffffff;
}

/* Sidebar Update: Neutral Corporate Gray */
#sidebar {
    background-color: #f0f2f5;
    border-right: 1px solid #dee2e6;
}
#sidebar QLabel {
    background-color: transparent;
    color: #212529;
    font-size: 18px;
    font-weight: bold;
}
#sidebar QPushButton {
    background-color: transparent;
    color: #495057;
    text-align: left;
    padding: 12px 20px;
    border: none;
    font-size: 14px;
}
#sidebar QPushButton:hover {
    background-color: #e9ecef;
    color: #212529;
}
#sidebar QPushButton:checked {
    background-color: #e2e6ea;
    color: #000000;
    font-weight: bold;
    border-left: 4px solid #007bff;
}

/* Tables */
QTableWidget {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
    gridline-color: #e9ecef;
    selection-background-color: #ebf5fb;
    selection-color: #212529;
    outline: none;
}
QHeaderView::section {
    background-color: #f8f9fa;
    color: #495057;
    font-weight: bold;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #dee2e6;
    border-right: 1px solid #e9ecef;
}
QTableCornerButton::section {
    background-color: #f8f9fa;
    border: none;
    border-bottom: 2px solid #dee2e6;
    border-right: 1px solid #e9ecef;
}

/* Inputs */
QLineEdit, QComboBox {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 6px;
    min-height: 20px;
}
QLineEdit:disabled, QComboBox:disabled { 
    background-color: #f8f9fa;
    color: #6c757d;
    border: 1px solid #ced4da;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #007bff;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
    selection-background-color: #007bff;
    selection-color: #ffffff;
    outline: none;
}

/* Buttons */
QPushButton {
    background-color: #007bff;
    color: #ffffff;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    border: none;
}
QPushButton:hover { background-color: #0056b3; }
QPushButton:disabled { background-color: #adb5bd; color: #ffffff; }
QPushButton#btn_delete { background-color: #dc3545; }
QPushButton#btn_delete:hover { background-color: #c82333; }
QPushButton#btn_clear { background-color: #6c757d; }
QPushButton#btn_clear:hover { background-color: #5a6268; }

/* GroupBox */
QGroupBox {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    margin-top: 15px;
    padding-top: 15px;
    background-color: #fdfdfd;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #495057;
    font-weight: bold;
    background-color: transparent;
}

QLabel {
    color: #212529;
    background-color: transparent;
}
"""