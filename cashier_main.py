# d:\PythonProjects\GroceryStoreInventoryPOS\cashier_main.py
import sys
import traceback

from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog

from styles import APP_STYLE
from database.db_manager import DatabaseManager
from views.pos_view import POSView
from controllers.pos_controller import POSController
from auth.operator_context import CashierContext

from views.login_dialog import LoginDialog
from views.register_select_dialog import RegisterSelectDialog


def _fatal(title: str, exc: Exception) -> None:
    details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    QMessageBox.critical(None, title, f"{type(exc).__name__}: {exc}\n\n{details}")
    raise SystemExit(1)


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    try:
        db = DatabaseManager(user="root", password="")

        # 1) Cashier login
        while True:
            login = LoginDialog("Cashier Login")
            result = login.exec()
            if result != QDialog.DialogCode.Accepted:
                raise SystemExit(0)

            try:
                cashier_account_id = db.authenticate_cashier(login.username(), login.password())
                break
            except Exception as e:
                QMessageBox.warning(None, "Login Failed", str(e))

        # 2) Register selection (online only)
        all_registers = db.get_registers()
        registers = [r for r in all_registers if r.get("Status") == "Online"]
        if not registers:
            raise RuntimeError("No online registers found.")

        regdlg = RegisterSelectDialog(registers)
        reg_result = regdlg.exec()
        if reg_result != QDialog.DialogCode.Accepted:
            raise SystemExit(0)

        register_id = regdlg.selected_register_id()

        operator = CashierContext(
            cashier_account_id=cashier_account_id,
            register_id=register_id,
        )

        if not db.is_cashier_active(operator.cashier_account_id):
            raise RuntimeError(f"Cashier account {operator.cashier_account_id} is inactive. POS blocked.")

        if not db.is_register_online(operator.register_id):
            raise RuntimeError(f"Register {operator.register_id} is offline. POS blocked.")

        session_id = db.start_pos_session(operator.cashier_account_id, operator.register_id)

        pos_view = POSView()
        POSController(pos_view, db, operator)
        pos_view.set_session_text(f"Cashier Account: {operator.cashier_account_id}\nRegister: {operator.register_id}")

        pos_view.setWindowTitle(
            f"Cashier POS (Account {operator.cashier_account_id} / Register {operator.register_id})"
        )
        pos_view.resize(1280, 800)

        def _on_close_event(event) -> None:
            try:
                db.close_pos_session(session_id)
            except Exception:
                pass
            event.accept()

        pos_view.closeEvent = _on_close_event
        pos_view.show()

        raise SystemExit(app.exec())

    except SystemExit:
        raise
    except Exception as e:
        _fatal("Fatal POS Launch Error", e)


if __name__ == "__main__":
    main()