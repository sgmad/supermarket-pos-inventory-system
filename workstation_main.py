# d:\PythonProjects\GroceryStoreInventoryPOS\workstation_main.py
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QDialog,
)

from styles import APP_STYLE
from database.db_manager import DatabaseManager
from auth.operator_context import AdminContext, CashierContext
from views.login_dialog import LoginDialog
from views.register_select_dialog import RegisterSelectDialog
from views.pos_view import POSView
from controllers.pos_controller import POSController
from admin_dashboard import Dashboard


class Workstation(QMainWindow):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.setWindowTitle("Workstation")
        self.resize(520, 320)
        self.setStyleSheet(APP_STYLE)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.btn_cashier = QPushButton("Cashier POS")
        self.btn_cashier.setMinimumHeight(54)
        self.btn_admin = QPushButton("Admin Dashboard")
        self.btn_admin.setMinimumHeight(54)

        layout.addWidget(self.btn_cashier)
        layout.addWidget(self.btn_admin)
        layout.addStretch()

        self.btn_cashier.clicked.connect(self.open_cashier_pos)
        self.btn_admin.clicked.connect(self.open_admin_dashboard)

    def open_cashier_pos(self) -> None:
        while True:
            login = LoginDialog("Cashier Login")
            result = login.exec()
            if result != QDialog.DialogCode.Accepted:
                return

            try:
                cashier_account_id = self.db.authenticate_cashier(login.username(), login.password())
                break
            except Exception as e:
                QMessageBox.warning(self, "Login Failed", str(e))

        all_registers = self.db.get_registers()
        registers = [r for r in all_registers if r.get("Status") == "Online"]
        if not registers:
            QMessageBox.critical(self, "No Registers", "No online registers are available.")
            return

        regdlg = RegisterSelectDialog(registers, self)
        reg_result = regdlg.exec()
        if reg_result != QDialog.DialogCode.Accepted:
            return

        operator = CashierContext(
            cashier_account_id=cashier_account_id,
            register_id=regdlg.selected_register_id(),
        )

        try:
            session_id = self.db.start_pos_session(operator.cashier_account_id, operator.register_id)
        except Exception as e:
            QMessageBox.critical(self, "Session Error", str(e))
            return

        pos_view = POSView()
        pos_view.set_session_text(f"Cashier Account: {operator.cashier_account_id}\nRegister: {operator.register_id}")
        POSController(pos_view, self.db, operator)
        pos_view.setWindowTitle(f"POS - Register {operator.register_id}")
        pos_view.resize(1280, 800)

        def _on_close_event(event) -> None:
            try:
                self.db.close_pos_session(session_id)
            except Exception:
                pass
            event.accept()

        pos_view.closeEvent = _on_close_event
        pos_view.show()

    def open_admin_dashboard(self) -> None:
        while True:
            dlg = LoginDialog("Admin Login")
            result = dlg.exec()
            if result != QDialog.DialogCode.Accepted:
                return

            try:
                admin_id = self.db.authenticate_admin(dlg.username(), dlg.password())
                break
            except Exception as e:
                QMessageBox.warning(self, "Login Failed", str(e))

        operator = AdminContext(admin_account_id=admin_id)
        win = Dashboard(self.db, operator)
        win.show()


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    db = DatabaseManager(user="root", password="")
    w = Workstation(db)
    w.show()

    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()