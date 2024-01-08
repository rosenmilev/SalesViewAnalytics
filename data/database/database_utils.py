import os
import sqlite3
from sqlite3 import Error


DATABASE_NAME = 'db.sqlite3'


def create_connection():
    conn = None
    # Build the full path to the database file based on the current file's directory
    current_directory = os.path.dirname(os.path.abspath(__file__))
    db_file_path = os.path.join(current_directory, DATABASE_NAME)

    try:
        conn = sqlite3.connect(db_file_path)
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
