import sqlite3
from datetime import datetime
import hashlib

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('pizza_delivery.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')

        # Create orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            customer_mobile TEXT NOT NULL,
            order_date TIMESTAMP NOT NULL,
            status TEXT NOT NULL,
            total_amount REAL NOT NULL
        )
        ''')

        # Create order_items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
        ''')

        self.conn.commit()

    def add_order(self, customer_name, customer_address, customer_mobile, total_amount):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO orders (customer_name, customer_address, customer_mobile, order_date, status, total_amount)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_name, customer_address, customer_mobile, datetime.now(), 'pending', total_amount))
        self.conn.commit()
        return cursor.lastrowid

    def add_order_item(self, order_id, item_type, item_name, quantity, price):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO order_items (order_id, item_type, item_name, quantity, price)
        VALUES (?, ?, ?, ?, ?)
        ''', (order_id, item_type, item_name, quantity, price))
        self.conn.commit()

    def get_all_orders(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM orders ORDER BY order_date DESC
        ''')
        return cursor.fetchall()

    def get_order_details(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM orders WHERE order_id = ?
        ''', (order_id,))
        order = cursor.fetchone()
        
        cursor.execute('''
        SELECT * FROM order_items WHERE order_id = ?
        ''', (order_id,))
        items = cursor.fetchall()
        
        return order, items

    def update_order_status(self, order_id, status):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE orders SET status = ? WHERE order_id = ?
        ''', (status, order_id))
        self.conn.commit()

    def get_orders_by_status(self, status):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM orders WHERE status = ? ORDER BY order_date DESC
        ''', (status,))
        return cursor.fetchall()

    def get_pending_orders(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM orders WHERE status = 'pending' ORDER BY order_date DESC
        ''')
        return cursor.fetchall()

    def get_completed_orders(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM orders WHERE status = 'completed' ORDER BY order_date DESC
        ''')
        return cursor.fetchall()

    def get_cancelled_orders(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM orders WHERE status = 'cancelled' ORDER BY order_date DESC
        ''')
        return cursor.fetchall()

    def get_orders_by_mobile(self, mobile):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM orders WHERE customer_mobile = ? ORDER BY order_date DESC
        ''', (mobile,))
        return cursor.fetchall()

    # User management methods
    def register_user(self, name, mobile, address, password):
        cursor = self.conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute('''
            INSERT INTO users (name, mobile, address, password)
            VALUES (?, ?, ?, ?)
            ''', (name, mobile, address, password_hash))
            self.conn.commit()
            return True, None
        except sqlite3.IntegrityError:
            return False, 'Mobile number already registered.'

    def authenticate_user(self, mobile, password):
        cursor = self.conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('''
        SELECT * FROM users WHERE mobile = ? AND password = ?
        ''', (mobile, password_hash))
        user = cursor.fetchone()
        return user

    def get_user_by_mobile(self, mobile):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM users WHERE mobile = ?
        ''', (mobile,))
        return cursor.fetchone()

    def update_user_profile(self, mobile, name, address):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE users SET name = ?, address = ? WHERE mobile = ?
        ''', (name, address, mobile))
        self.conn.commit()

    def __del__(self):
        self.conn.close() 