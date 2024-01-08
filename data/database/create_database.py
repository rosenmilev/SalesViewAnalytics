import os
import sqlite3
from sqlite3 import Error
from data.database.data_import import clean_data
from data.database.database_utils import create_connection, create_table, insert_data_into_table


# Using normalized database schema to create and fill the tables, based on dataset format.
def main(name_of_db_file, path_to_db_file):
    db_file_path = os.path.join(path_to_db_file, name_of_db_file)
    if os.path.exists(db_file_path):
        print("Database already exists. Skipping creation.")
        return
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
    state TEXT NOT NULL,
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

    connection = create_connection(name_of_db_file, path_to_db_file)
    create_table(connection, customers_table_sql)
    create_table(connection, products_table_sql)
    create_table(connection, sales_transactions_table_sql)
    create_table(connection, order_details_table_sql)
    print('Tables Created')

    cleaned_data = clean_data()

    customers_df = cleaned_data.copy()[['customer_id', 'customer_name', 'segment']]
    customers_df = customers_df.drop_duplicates(subset=['customer_id'])

    products_df = cleaned_data.copy()[['product_id', 'category', 'sub_category', 'product_name']]
    products_df = products_df.drop_duplicates(subset=['product_id'])

    sales_transactions_df = cleaned_data.copy()[['order_id', 'order_date', 'ship_date', 'ship_mode', 'customer_id',
                                                 'city', 'state', 'region', 'postal_code']]
    sales_transactions_df = sales_transactions_df.drop_duplicates(subset=['order_id'])

    order_details_df = cleaned_data.copy()[['order_id', 'product_id', 'sales']]

    print("Customers:", customers_df.shape[0])
    print("Products:", products_df.shape[0])
    print("Sales Transactions:", sales_transactions_df.shape[0])
    print("Order Details:", order_details_df.shape[0])

    insert_data_into_table(connection, customers_df, 'customers')
    insert_data_into_table(connection, products_df, 'products')
    insert_data_into_table(connection, sales_transactions_df, 'sales_transactions')
    insert_data_into_table(connection, order_details_df, 'order_details')
    print('Tables Inserted')

    if connection:
        connection.close()


path_to_db_file = '/home/traxx90/PycharmProjects/SalesViewAnalytics/app/data/db.sqlite3'
db_file_name = "db.sqlite3"

# if __name__ == "__main__":
#     main(db_file_name, path_to_db_file)
