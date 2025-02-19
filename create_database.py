import sqlite3


def create_database():
    # Connect to SQLite database (it will create the database if it doesn't exist)
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()

    # Create clients table
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                paid_amount REAL DEFAULT 0,
                owed_amount REAL DEFAULT 0,
                total_bill REAL DEFAULT 0
            )
        """)

    # Create orders table with modified date format, Arabic day, and new 'order_type' column
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_name TEXT NOT NULL,
                client_id INTEGER,
                width REAL,
                length REAL,
                price_per_cm REAL,
                total_price REAL,
                payment_type TEXT,
                order_type TEXT,    -- New column for order type
                order_date TEXT,    -- Format: dd/mm/yyyy
                order_day TEXT,     -- Arabic day name
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
        """)

    # Create payments table with modified date format and Arabic day
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                payment_date TEXT,    -- Format: dd/mm/yyyy
                payment_day TEXT,     -- Arabic day name
                amount_paid REAL,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
        """)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database and tables created successfully.")

if __name__ == "__main__":
    create_database()