import os
import sqlite3
from sqlite3 import Error
# from data.database.data_import import cleaned_data


# Helper function for database creation
def create_path(db_filename):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    db_filepath = os.path.join(current_directory, db_filename)
    return db_filepath



def create_connection(file_name):
    conn = None
    db_filepath = create_path(file_name)
    print(db_filepath)
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
