import sqlite3
import os
import pandas as pd

DB_DIR = "db"

USER_DB = 'user.db'
class UserNotFoundError(Exception):
    """Custom exception when a user is not found in the database."""
    pass


def fetch_db_rows_as_dicts(db_path, table_name):
    conn = None
    try:
        # Connect to the SQLite database
        dbPath = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,db_path))
        conn = sqlite3.connect(dbPath)
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        cursor = conn.cursor()

        # Get the column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Execute a query to fetch all rows from the table
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        assert len(rows) > 1
        return column_names, rows[1:]
            
    except sqlite3.Error as e:
        #print(f"SQLite error: {e}")
        pass
    finally:
        # Close the connection
        if conn:
            conn.close()


def fetchTopologies():
    topologiesPath = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,'topologies_desc.csv'))
    topologiesDf = pd.read_csv(topologiesPath,  encoding = "ISO-8859-1")
    return topologiesDf

def insert_user(user_name, team_name, email_address, password, bank):
    dbPath = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,USER_DB))
    print(dbPath)
    try:
        with sqlite3.connect(dbPath) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_name, team_name, password, email_address, bank) 
                VALUES (?, ?, ?, ?, ?)
            """, (user_name, team_name, password, email_address, bank))
            conn.commit()
            print("User inserted successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def fetch_user(user_name, password):
    dbPath = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,USER_DB))
    print(dbPath)
    try:
        with sqlite3.connect(dbPath) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, user_name, team_name, email_address, bank 
                FROM users 
                WHERE user_name = ? AND password = ?
            """, (user_name, password))
            user = cursor.fetchone()
            
            if user:
                return {
                    "user_id": user[0],
                    "user_name": user[1],
                    "team_name": user[2],
                    "email_address": user[3],
                    "bank": user[4]
                }
            else:
                raise UserNotFoundError(f"User with username '{user_name}' not found.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")



#user = fetch_user('ruchibonkers', 'ruchibonkers')                 
#print(user)   

#insert_user('ruchibonkers', 'ruchibonkers', 'ruchibonkers', 'ruchibonkers@gmail.com')

# Example usage:
#dbPath = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,'topologies.sqlite'))
#fetch_db_rows_as_dicts(dbPath, 'topologies')
