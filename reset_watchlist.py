#!/usr/bin/env python3
"""
Script to:
1. Connect to a local MariaDB instance (user 'scuser', password 'password').
2. Delete all rows from the 'watchlist' table.
3. Read 'watchlist.txt' and insert each line as a new record into the 'symbol' column.
"""

import pymysql

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'scuser'
DB_PASSWORD = 'password'
DB_NAME = 'sc'
TABLE_NAME = 'watchlist'

def main():
    # Establish database connection
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # 1. Delete all existing rows from the watchlist table
            delete_sql = f"DELETE FROM {TABLE_NAME}"
            cursor.execute(delete_sql)
            print(f"Deleted all rows from '{TABLE_NAME}'.")

            # 2. Read the file and insert each line as a new record
            file_path = 'watchlist.txt'
            insert_sql = f"INSERT INTO {TABLE_NAME} (symbol) VALUES (%s)"
            inserted_count = 0

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        symbol = line.strip()
                        if symbol:  # skip empty lines
                            cursor.execute(insert_sql, (symbol,))
                            inserted_count += 1
                print(f"Inserted {inserted_count} symbols from '{file_path}'.")
            except FileNotFoundError:
                print(f"Error: File '{file_path}' not found in the current directory.")
                return

        # Commit the transaction
        connection.commit()
        print("All changes committed successfully.")

    except pymysql.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
    finally:
        connection.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()