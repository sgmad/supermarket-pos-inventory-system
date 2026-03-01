import mysql.connector
from auth.passwords import verify_password
from typing import Optional


class DatabaseManager:
    """
    Data-access layer.

    Rules:
    - Mutations go through stored procedures where available.
    - Reads prefer views (v_*) where they already exist in the DB.
    - IDs in this layer match the DB: AccountID for users, CustomerID for customers,
      RegisterID for registers, ProductID for products, ReceiptID for receipts.
    """

    def __init__(self, host: str = "127.0.0.1", database: str = "retail_db", user: str = "root", password: str = ""):
        self.config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "raise_on_warnings": True,
        }

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def _callproc_return_scalar(self, proc_name: str, args: tuple) -> int:
        """
        Calls a stored procedure and returns the first column of the first row
        of the first result set.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc(proc_name, args)
                conn.commit()

                results = list(cursor.stored_results())
                if not results:
                    raise RuntimeError(f"{proc_name} returned no result set. Expected a SELECT with a scalar ID.")

                row = results[0].fetchone()
                if not row or row[0] is None:
                    raise RuntimeError(f"{proc_name} returned an empty scalar ID.")
                return int(row[0])

    def _callproc_no_return(self, proc_name: str, args: tuple) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc(proc_name, args)
                conn.commit()

    # ======================
    # Role / status helpers
    # ======================

    def is_admin_active(self, account_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT fn_is_admin_active(%s)", (account_id,))
                return int(cursor.fetchone()[0]) == 1

    def is_cashier_active(self, account_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT fn_is_cashier_active(%s)", (account_id,))
                return int(cursor.fetchone()[0]) == 1

    def is_register_online(self, register_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT fn_is_register_online(%s)", (register_id,))
                return int(cursor.fetchone()[0]) == 1

    # =========================
    # Authentication / Sessions
    # =========================

    def _get_account_row_by_username(self, username: str):
        uname = (username or "").strip()
        if not uname:
            raise ValueError("Username is required.")

        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT AccountID, PasswordHash, Status
                    FROM user_account
                    WHERE Username = %s
                    LIMIT 1
                    """,
                    (uname,),
                )
                return cursor.fetchone()

    def _touch_last_login(self, account_id: int) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE user_account SET LastLogin = CURRENT_TIMESTAMP() WHERE AccountID = %s",
                    (account_id,),
                )
                conn.commit()

    def authenticate_user(self, username: str, password: str) -> int:
        """
        Authenticates username/password against user_account.

        This method verifies:
        - The username exists.
        - The account Status is 'Active'.
        - The password matches PasswordHash (pbkdf2 format or plaintext fallback).
        """
        row = self._get_account_row_by_username(username)
        if row is None:
            raise ValueError("Invalid username or password.")

        account_id = int(row["AccountID"])
        status = str(row.get("Status") or "")
        stored = str(row.get("PasswordHash") or "")

        if status != "Active":
            raise ValueError("Account is not active.")

        if not verify_password(password or "", stored):
            raise ValueError("Invalid username or password.")

        self._touch_last_login(account_id)
        return account_id

    def authenticate_admin(self, username: str, password: str) -> int:
        account_id = self.authenticate_user(username, password)
        if not self.is_admin_active(account_id):
            raise ValueError("This account does not have active Admin privileges.")
        return account_id

    def authenticate_cashier(self, username: str, password: str) -> int:
        account_id = self.authenticate_user(username, password)
        if not self.is_cashier_active(account_id):
            raise ValueError("This account does not have active Cashier privileges.")
        return account_id

    # ====================
    # POS session locking
    # ====================

    def start_pos_session(self, cashier_account_id: int, register_id: int) -> int:
        return self._callproc_return_scalar("sp_start_pos_session", (cashier_account_id, register_id))

    def close_pos_session(self, session_id: int) -> None:
        self._callproc_no_return("sp_close_pos_session", (session_id,))

    # ===========
    # Categories
    # ===========

    def add_category(self, name: str, status: str = "Active") -> int:
        return self._callproc_return_scalar("sp_add_category", (name, status))

    def update_category(self, category_id: int, name: str, status: str) -> None:
        self._callproc_no_return("sp_update_category", (category_id, name, status))

    def get_categories_active(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT CategoryID, CategoryName FROM category WHERE Status = 'Active' ORDER BY CategoryName"
                )
                return cursor.fetchall()

    def get_categories_all(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT CategoryID, CategoryName, Status FROM category ORDER BY CategoryName")
                return cursor.fetchall()

    # ==========
    # Suppliers
    # ==========

    def add_supplier(self, name: str, contact_number: Optional[str], address: Optional[str]) -> int:
        return self._callproc_return_scalar("sp_add_supplier", (name, contact_number, address))

    def update_supplier(self, supplier_id: int, name: str, contact_number: Optional[str], address: Optional[str]) -> None:
        self._callproc_no_return("sp_update_supplier", (supplier_id, name, contact_number, address))

    def get_suppliers(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT SupplierID, Name, ContactNumber, Address FROM supplier ORDER BY Name")
                return cursor.fetchall()

    # ==========
    # Registers
    # ==========

    def add_register(self, location: str, status: str = "Online") -> int:
        if status not in ("Online", "Offline"):
            raise ValueError("Register status must be 'Online' or 'Offline'.")
        location = (location or "").strip()
        if not location:
            raise ValueError("Register location is required.")

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO `register` (Location, Status) VALUES (%s, %s)", (location, status))
                conn.commit()
                return int(cursor.lastrowid)

    def update_register(self, register_id: int, location: str, status: str) -> None:
        if status not in ("Online", "Offline"):
            raise ValueError("Register status must be 'Online' or 'Offline'.")
        location = (location or "").strip()
        if not location:
            raise ValueError("Register location is required.")

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE `register` SET Location = %s, Status = %s WHERE RegisterID = %s",
                    (location, status, register_id),
                )
                conn.commit()
                if cursor.rowcount == 0:
                    raise RuntimeError(f"Register {register_id} does not exist.")

    def get_registers(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT RegisterID, Location, Status FROM `register` ORDER BY RegisterID")
                return cursor.fetchall()

    # =====================
    # Products + Inventory
    # =====================

    def add_product(
        self,
        supplier_id: Optional[int],
        admin_account_id: int,
        name: str,
        category_id: int,
        price: float,
        status: str,
        initial_qty: int,
        reorder_level: int,
    ) -> int:
        return self._callproc_return_scalar(
            "sp_add_product",
            (supplier_id, admin_account_id, name, category_id, price, status, initial_qty, reorder_level),
        )

    def update_product(
        self,
        product_id: int,
        supplier_id: Optional[int],
        admin_account_id: int,
        name: str,
        category_id: int,
        price: float,
        status: str,
        reorder_level: int,
    ) -> None:
        self._callproc_no_return(
            "sp_update_product",
            (product_id, supplier_id, admin_account_id, name, category_id, price, status, reorder_level),
        )

    def soft_delete_product(self, product_id: int) -> None:
        self._callproc_no_return("sp_delete_product", (product_id,))

    def stock_in(self, product_id: int, admin_account_id: int, qty: int) -> None:
        self._callproc_no_return("sp_stock_in", (product_id, admin_account_id, qty))

    def stock_out(self, product_id: int, admin_account_id: int, qty: int) -> None:
        self._callproc_no_return("sp_stock_out", (product_id, admin_account_id, qty))

    def view_product_list(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        ProductID, ProductName, CategoryName, SupplierName,
                        Price, Status, Availability,
                        QtyAvailable, ReorderLevel, LastUpdated
                    FROM v_product_list
                    ORDER BY ProductName
                    """
                )
                return cursor.fetchall()

    def view_available_stock(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        p.ProductID,
                        p.ProductName,
                        i.QtyAvailable,
                        i.ReorderLevel,
                        fn_is_low_stock(p.ProductID) AS IsLowStock,
                        i.LastUpdated
                    FROM inventory i
                    JOIN product p ON p.ProductID = i.ProductID
                    ORDER BY p.ProductName
                    """
                )
                return cursor.fetchall()

    def view_inventory_movement_logs(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM v_inventory_movement_logs")
                return cursor.fetchall()

    # ===========
    # Customers
    # ===========

    def add_customer(
        self,
        first_name: str,
        last_name: str,
        contact_number: Optional[str],
        email: Optional[str],
        status: str = "Active",
    ) -> int:
        return self._callproc_return_scalar("sp_add_customer", (first_name, last_name, contact_number, email, status))

    def update_customer_person(
        self,
        customer_id: int,
        first_name: str,
        last_name: str,
        contact_number: Optional[str],
        email: Optional[str],
    ) -> None:
        self._callproc_no_return(
            "sp_update_customer_person",
            (customer_id, first_name, last_name, contact_number, email),
        )

    def set_customer_status(self, customer_id: int, status: str) -> None:
        self._callproc_no_return("sp_set_customer_status", (customer_id, status))

    def get_customer_list(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT CustomerID, FirstName, LastName, ContactNumber, Email, Status
                    FROM v_customer
                    ORDER BY LastName, FirstName
                    """
                )
                return cursor.fetchall()

    def get_customers_active_lite(self):
        """
        For POS customer selection. Walk-in is represented by None in the UI.
        Returns: CustomerID, DisplayName
        """
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        CustomerID,
                        CONCAT(COALESCE(FirstName, ''), ' ', COALESCE(LastName, '')) AS DisplayName
                    FROM v_customer
                    WHERE Status = 'Active'
                    ORDER BY LastName, FirstName
                    """
                )
                rows = cursor.fetchall()
                for r in rows:
                    r["DisplayName"] = (r.get("DisplayName") or "").strip() or f"Customer {r.get('CustomerID')}"
                return rows

    # =================
    # Users / Roles
    # =================

    def set_user_status(self, account_id: int, status: str) -> None:
        self._callproc_no_return("sp_set_user_status", (account_id, status))

    def update_user_role(self, account_id: int, role_name: str) -> None:
        self._callproc_no_return("sp_update_user_role", (account_id, role_name))

    def get_staff_list(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT ID, Name, Role, Status, AccountType FROM v_staff_list ORDER BY Name")
                return cursor.fetchall()

    def get_cashiers_active(self):
        """
        Returns:
            CashierID (AccountID),
            CashierName (person name if present, else username)
        """
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        ua.AccountID AS CashierID,
                        COALESCE(CONCAT(p.FirstName, ' ', p.LastName), ua.Username) AS CashierName
                    FROM user_account ua
                    JOIN user_account_role uar ON uar.AccountID = ua.AccountID
                    JOIN user_role ur ON ur.RoleID = uar.RoleID
                    LEFT JOIN person p ON p.PersonID = ua.PersonID
                    WHERE ur.RoleName = 'Cashier'
                      AND ua.Status = 'Active'
                    ORDER BY COALESCE(p.LastName, ua.Username), COALESCE(p.FirstName, ua.Username)
                    """
                )
                return cursor.fetchall()

    # ======
    # Sales
    # ======

    def create_sale(self, cashier_account_id: int, register_id: int, customer_id: Optional[int]) -> int:
        return self._callproc_return_scalar("sp_create_sale", (cashier_account_id, register_id, customer_id))

    def add_sale_item(self, receipt_id: int, product_id: int, qty: int) -> None:
        self._callproc_no_return("sp_add_sale_item", (receipt_id, product_id, qty))

    def finalize_sale(self, receipt_id: int, payment_amount: float) -> None:
        self._callproc_no_return("sp_finalize_sale", (receipt_id, payment_amount))

    def cancel_sale(self, receipt_id: int) -> None:
        self._callproc_no_return("sp_cancel_sale", (receipt_id,))

    def get_receipt_summary(self, receipt_id: int):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT TotalAmount, TaxAmount, GrandTotal FROM receipt WHERE ReceiptID = %s",
                    (receipt_id,),
                )
                return cursor.fetchone()

    def get_receipt_items(self, receipt_id: int):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT rd.ProductID, p.ProductName, rd.Qty, rd.UnitPrice, rd.Subtotal
                    FROM receiptdetails rd
                    JOIN product p ON p.ProductID = rd.ProductID
                    WHERE rd.ReceiptID = %s AND rd.LineStatus = 'Active'
                    ORDER BY rd.ReceiptDetailsID
                    """,
                    (receipt_id,),
                )
                return cursor.fetchall()

    def view_sales_history(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM v_sales_history")
                return cursor.fetchall()

    def view_sales_history_detailed(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM v_sales_history_detailed")
                return cursor.fetchall()

    def view_daily_sales_report(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM v_daily_sales_report")
                return cursor.fetchall()

    def view_weekly_sales_report(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM v_weekly_sales_report")
                return cursor.fetchall()