import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'company_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}

def create_database():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"Database '{DB_CONFIG['database']}' created successfully!")
        else:
            print(f"Database '{DB_CONFIG['database']}' already exists.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

def setup_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        
        conn.commit()
        print("Database schema created successfully!")
    except Exception as e:
        print(f"Error setting up database: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def populate_sample_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM departments")
        if cursor.fetchone()[0] > 0:
            print("Sample data already exists!")
            return
        
        departments = [
            ('Engineering',),
            ('Sales',),
            ('HR',),
            ('Marketing',),
            ('Finance',)
        ]
        cursor.executemany("INSERT INTO departments (name) VALUES (%s)", departments)
        
        employees = [
            ('John Doe', 1, 'john.doe@company.com', 75000.00),
            ('Jane Smith', 1, 'jane.smith@company.com', 82000.00),
            ('Mike Johnson', 2, 'mike.johnson@company.com', 65000.00),
            ('Sarah Williams', 2, 'sarah.williams@company.com', 68000.00),
            ('Tom Brown', 3, 'tom.brown@company.com', 60000.00),
            ('Emily Davis', 4, 'emily.davis@company.com', 62000.00),
            ('David Wilson', 5, 'david.wilson@company.com', 70000.00),
            ('Lisa Anderson', 1, 'lisa.anderson@company.com', 90000.00),
            ('Robert Taylor', 2, 'robert.taylor@company.com', 72000.00),
            ('Jennifer Martinez', 4, 'jennifer.martinez@company.com', 66000.00)
        ]
        cursor.executemany(
            "INSERT INTO employees (name, department_id, email, salary) VALUES (%s, %s, %s, %s)",
            employees
        )
        
        products = [
            'Laptop',
            'Wireless Mouse',
            'Mechanical Keyboard',
            'USB-C Hub',
            'Monitor',
            'Webcam',
            'Headphones',
            'Desk Lamp',
            'Office Chair',
            'Standing Desk'
        ]
        
        print("Adding products...")
        for i, product_name in enumerate(products):
            price = round(random.uniform(29.99, 999.99), 2)
            cursor.execute(
                "INSERT INTO products (name, price) VALUES (%s, %s)",
                (product_name, price)
            )
            print(f"  Added product: {product_name}")
        
        # Insert orders with embeddings
        customer_names = [
            'Acme Corporation',
            'Tech Solutions Inc',
            'Global Industries',
            'Innovative Systems',
            'Digital Dynamics',
            'Future Technologies',
            'Smart Solutions',
            'Creative Designs',
            'Enterprise Solutions',
            'Modern Business Co'
        ]
        
        print("Adding orders...")
        base_date = datetime.now() - timedelta(days=180)
        for i, customer in enumerate(customer_names):
            for j in range(random.randint(2, 5)):
                employee_id = random.randint(1, 10)
                order_total = round(random.uniform(500, 10000), 2)
                order_date = base_date + timedelta(days=random.randint(0, 180))
                
                cursor.execute(
                    "INSERT INTO orders (customer_name, employee_id, order_total, order_date) VALUES (%s, %s, %s, %s)",
                    (customer, employee_id, order_total, order_date.date())
                )
            print(f"  Added orders for: {customer}")
        
        conn.commit()
        print("\nSample data populated successfully!")
        
    except Exception as e:
        print(f"Error populating data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Starting database initialization...\n")
    create_database()
    setup_database()
    populate_sample_data()
    print("\nDatabase initialization complete!")
