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


def insert_data_into_table(connection, df, table_name):
    try:
        df.to_sql(table_name, connection, if_exists='append', index=False)
    except Error as e:
        print(f"Error inserting data into {table_name}: {e}")

def generate_sql():
    pass


# Using normalized database schema
def main():
    customers_table_sql = '''CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT NOT NULL
    )
    '''

    products_table_sql = '''CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    product_name TEXT NOT NULL 
    )'''

    sales_transactions_table_sql = ''' CREATE TABLE IF NOT EXISTS sales_transactions (
    order_id TEXT PRIMARY KEY ,
    order_date DATE NOT NULL,
    ship_date DATE,
    ship_mode TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    city TEXT NOT NULL,
    region TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    )'''

    order_details_table_sql = '''CREATE TABLE IF NOT EXISTS order_details (
    order_details_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    sales REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES sales_transactions(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
    )'''

    # Create table, filter df for each table, insert the data
    file_name = 'db.sqlite3'
    connection = create_connection(file_name)
    create_table(connection, customers_table_sql)
    create_table(connection, products_table_sql)
    create_table(connection, sales_transactions_table_sql)
    create_table(connection, order_details_table_sql)
    print('Tables Created')

    customers_df = cleaned_data.copy()[['customer_id', 'customer_name', 'segment']]
    customers_df = customers_df.drop_duplicates(subset=['customer_id'])

    products_df = cleaned_data.copy()[['product_id', 'category', 'sub_category', 'product_name']]
    products_df = products_df.drop_duplicates(subset=['product_id'])

    sales_transactions_df = cleaned_data.copy()[['order_id', 'order_date', 'ship_date', 'ship_mode', 'customer_id',
                                                 'city', 'region', 'postal_code']]
    sales_transactions_df = sales_transactions_df.drop_duplicates(subset=['order_id'])

    order_details_df = cleaned_data.copy()[['order_id', 'product_id', 'sales']]

    insert_data_into_table(connection, customers_df, 'customers')
    insert_data_into_table(connection, products_df, 'products')
    insert_data_into_table(connection, sales_transactions_df, 'sales_transactions')
    insert_data_into_table(connection, order_details_df, 'order_details')
    print('Tables Inserted')

    if connection:
        connection.close()


if __name__ == '__main__':
    main()

