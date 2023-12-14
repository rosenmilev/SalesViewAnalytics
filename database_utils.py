import os
import sqlite3
from sqlite3 import Error
from data_import import cleaned_data


def create_path(db_filename):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    db_filepath = os.path.join(current_directory, db_filename)
    return db_filepath

def create_connection(file_name):
    conn = None
    db_filepath = create_path(file_name)
    try:
        conn = sqlite3.connect(db_filepath)
    except Error as e:
        print(e)
    return conn


def create_table(connection, sql_for_table):
    try:
        c = connection.cursor()
        c.execute(sql_for_table)
    except Error as e:
        print(e)


# Using normalized database schema
def main():
    regions_table_sql = '''CREATE TABLE IF NOT EXISTS Regions (
    postal_code INTEGER PRIMARY KEY,
    city TEXT,
    state TEXT,
    country TEXT,
    region TEXT
    );

    '''

    customers_table_sql = '''CREATE TABLE IF NOT EXISTS Customers (
    int_customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT UNIQUE NOT NULL,
    customer_name TEXT,
    segment TEXT,
    postal_code INTEGER NOT NULL,
    FOREIGN KEY(postal_code) REFERENCES Regions(postal_code)
    );
    '''

    products_table_sql = '''CREATE TABLE IF NOT EXISTS Products (
    int_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT UNIQUE NOT NULL,
    category TEXT,
    sub_category TEXT,
    product_name TEXT NOT NULL 
    );'''

    sales_table_sql = ''' CREATE TABLE IF NOT EXISTS Orders(
    int_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE NOT NULL,
    order_date DATE,
    ship_date DATE,
    ship_mode TEXT,
    int_customer_id INTEGER,
    int_product_id INTEGER,
    sales REAL NOT NULL ,
    FOREIGN KEY(int_customer_id) REFERENCES Customers(int_customer_id),
    FOREIGN KEY(int_product_id) REFERENCES Products(int_product_id)
    );'''

    file_name = 'db.sqlite3'
    connection = create_connection(file_name)
    create_table(connection, regions_table_sql)
    create_table(connection, customers_table_sql)
    create_table(connection, products_table_sql)
    create_table(connection, sales_table_sql)


if __name__ == '__main__':

    con = create_connection('db.sqlite3')

