# d:\PythonProjects\GroceryStoreInventoryPOS\main.py
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtWidgets import QDialog

from styles import APP_STYLE
from database.db_manager import DatabaseManager
from auth.operator_context import AdminContext
from views.login_dialog import LoginDialog
from admin_dashboard import Dashboard


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    db = DatabaseManager(user="root", password="")

    while True:
        dlg = LoginDialog("Admin Login")
        result = dlg.exec()
        if result != QDialog.DialogCode.Accepted:
            raise SystemExit(0)

        try:
            admin_id = db.authenticate_admin(dlg.username(), dlg.password())
            operator = AdminContext(admin_account_id=admin_id)
            break
        except Exception as e:
            QMessageBox.warning(None, "Login Failed", str(e))

    window = Dashboard(db, operator)
    window.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()