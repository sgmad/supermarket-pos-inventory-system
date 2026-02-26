import mysql.connector

class DatabaseManager:
    def __init__(self, host="127.0.0.1", database="retail_db", user="root", password=""):
        self.config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'raise_on_warnings': True
        }

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def get_categories(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT CategoryID, CategoryName FROM category WHERE Status = 'Active'")
                return cursor.fetchall()

    def get_suppliers(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT SupplierID, Name FROM supplier")
                return cursor.fetchall()
            
    def get_receipt_summary(self, receipt_id):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = "SELECT TotalAmount, TaxAmount, GrandTotal FROM receipt WHERE ReceiptID = %s"
                cursor.execute(query, (receipt_id,))
                return cursor.fetchone()

    def get_receipt_items(self, receipt_id):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT rd.ProductID, p.ProductName, rd.Qty, rd.UnitPrice, rd.Subtotal 
                    FROM receiptdetails rd
                    JOIN product p ON rd.ProductID = p.ProductID
                    WHERE rd.ReceiptID = %s AND rd.LineStatus = 'Active'
                """
                cursor.execute(query, (receipt_id,))
                return cursor.fetchall()

    def cancel_sale(self, receipt_id):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc('sp_cancel_sale', (receipt_id,))
                conn.commit()

    def get_staff_list(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Union to view both Admins and Cashiers in one table
                query = """
                    SELECT AdminID AS ID, Username AS Name, Role, Status, 'Admin' AS AccountType 
                    FROM admin
                    UNION ALL
                    SELECT CashierID AS ID, CONCAT(FirstName, ' ', LastName) AS Name, 'Cashier' AS Role, Status, 'Cashier' AS AccountType 
                    FROM cashier
                """
                cursor.execute(query)
                return cursor.fetchall()

    def get_customer_list(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT CustomerID, FirstName, LastName, ContactNumber, Email, Status FROM customer")
                return cursor.fetchall()

    # ---------------------------------------------------------
    # CREATE (INSERT)
    # ---------------------------------------------------------

    def add_product(self, supplier_id, admin_id, name, category_id, price, status, initial_qty, reorder_level):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                args = (supplier_id, admin_id, name, category_id, price, status, initial_qty, reorder_level)
                cursor.callproc('sp_add_product', args)
                conn.commit()
                for result in cursor.stored_results():
                    return result.fetchone()[0]

    def add_category(self, category_name, status='Active'):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "INSERT INTO category (CategoryName, Status) VALUES (%s, %s)"
                cursor.execute(query, (category_name, status))
                conn.commit()
                return cursor.lastrowid

    def add_supplier(self, admin_id, name, contact_number, address):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "INSERT INTO supplier (AdminID, Name, ContactNumber, Address) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (admin_id, name, contact_number, address))
                conn.commit()
                return cursor.lastrowid

    def add_customer(self, first_name, last_name, contact_number, email, status='Active'):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO customer (FirstName, LastName, ContactNumber, Email, Status) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (first_name, last_name, contact_number, email, status))
                conn.commit()
                return cursor.lastrowid

    def record_stock_in(self, product_id, admin_id, qty):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc('sp_stock_in', (product_id, admin_id, qty))
                conn.commit()

    def create_sale(self, cashier_id, register_id, customer_id=None):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc('sp_create_sale', (cashier_id, register_id, customer_id))
                conn.commit()
                for result in cursor.stored_results():
                    return result.fetchone()[0]

    def add_sale_item(self, receipt_id, product_id, qty):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc('sp_add_sale_item', (receipt_id, product_id, qty))
                conn.commit()

    def finalize_sale(self, receipt_id, payment_amount):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc('sp_finalize_sale', (receipt_id, payment_amount))
                conn.commit()

    # ---------------------------------------------------------
    # READ (SELECT)
    # ---------------------------------------------------------

    def view_product_list(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT p.ProductID, p.ProductName, p.Price, p.Status, p.Availability, 
                           p.CategoryID, c.CategoryName, 
                           p.SupplierID, s.Name AS SupplierName,
                           i.ReorderLevel
                    FROM product p
                    LEFT JOIN category c ON p.CategoryID = c.CategoryID
                    LEFT JOIN supplier s ON p.SupplierID = s.SupplierID
                    LEFT JOIN inventory i ON p.ProductID = i.ProductID
                """
                cursor.execute(query)
                return cursor.fetchall()

    def view_available_stock(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT p.ProductID, i.InventoryID, p.ProductName, i.QtyAvailable, i.ReorderLevel, i.LastUpdated
                    FROM inventory i
                    JOIN product p ON i.ProductID = p.ProductID
                """
                cursor.execute(query)
                return cursor.fetchall()

    def view_sales_history(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM receipt ORDER BY ReceiptDate DESC"
                cursor.execute(query)
                return cursor.fetchall()

    def view_inventory_movement_logs(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT a.AuditDateTime, p.ProductName, a.ChangeAmount, a.Reason, 
                           a.PreviousQty, a.NewQty, a.AdminID, a.ReceiptID, a.CashierID
                    FROM inventoryaudit a
                    LEFT JOIN product p ON a.ProductID = p.ProductID
                    ORDER BY a.AuditDateTime DESC
                """
                cursor.execute(query)
                return cursor.fetchall()

    def view_daily_sales_report(self):
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT DATE(ReceiptDate) AS SaleDate, COUNT(ReceiptID) AS TotalTransactions,
                           SUM(GrandTotal) AS TotalRevenue, SUM(TaxAmount) AS TotalTax
                    FROM receipt
                    WHERE SaleStatus = 'Paid'
                    GROUP BY DATE(ReceiptDate)
                    ORDER BY SaleDate DESC
                """
                cursor.execute(query)
                return cursor.fetchall()

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update_product(self, product_id, supplier_id, admin_id, name, category_id, price, status, reorder_level):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                args = (product_id, supplier_id, admin_id, name, category_id, price, status, reorder_level)
                cursor.callproc('sp_update_product', args)
                conn.commit()

    def update_category(self, category_id, name, status):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "UPDATE category SET CategoryName = %s, Status = %s WHERE CategoryID = %s"
                cursor.execute(query, (name, status, category_id))
                conn.commit()

    def update_supplier(self, supplier_id, name, contact_number, address):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "UPDATE supplier SET Name = %s, ContactNumber = %s, Address = %s WHERE SupplierID = %s"
                cursor.execute(query, (name, contact_number, address, supplier_id))
                conn.commit()

    def update_user_role(self, admin_id, new_role):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc('sp_update_admin_role', (admin_id, new_role))
                conn.commit()

    # ---------------------------------------------------------
    # DELETE (SOFT DELETE / DISABLE)
    # ---------------------------------------------------------

    def soft_delete_product(self, product_id):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc('sp_delete_product', (product_id,))
                conn.commit()

    def disable_admin(self, admin_id):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "UPDATE admin SET Status = 'Inactive' WHERE AdminID = %s"
                cursor.execute(query, (admin_id,))
                conn.commit()

    def disable_cashier(self, cashier_id):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "UPDATE cashier SET Status = 'Inactive' WHERE CashierID = %s"
                cursor.execute(query, (cashier_id,))
                conn.commit()
        
    def disable_customer(self, customer_id):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "UPDATE customer SET Status = 'Inactive' WHERE CustomerID = %s"
                cursor.execute(query, (customer_id,))
                conn.commit()