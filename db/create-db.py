import sqlite3


def create_proposition_table():
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS proposition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bank TEXT NOT NULL,
            city TEXT NOT NULL,
            product_type TEXT NOT NULL,
            subcount1 INTEGER,
            subcount2 INTEGER,
            subcount3 INTEGER,
            product_name TEXT NOT NULL,
            revenue TEXT,
            money_needs TEXT,
            customer_exp_needs TEXT,
            sustainability_needs TEXT,
            matching_topologies TEXT,
            predicted_subscriber_take_out INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    # create a database connection
    try:
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()
    except sqlite3.Error as e:
        print(e)


def create_user_table():
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                user_name TEXT NOT NULL, 
                password TEXT NOT NULL, 
                email_address TEXT NOT NULL,
                bank TEXT NOT NULL
        );"""
    ]

    # create a database connection
    try:
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()
    except sqlite3.Error as e:
        print(e)


def create_budget_table():
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS budget (
                budget_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                bank TEXT NOT NULL,
                csBudget INTEGER,
                itBudget INTEGER,
                marketingBudget INTEGER,
                salesBudget INTEGER,
                opsBudget INTEGER,
                valid_until DATETIME
        );"""
    ]

    # create a database connection
    try:
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()
    except sqlite3.Error as e:
        print(e)

def create_regulation_table():
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS regulation (
                regulations_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                bank TEXT NOT NULL,
                reg1 TEXT,
                reg2 TEXT,
                reg3 TEXT,
                reg4 TEXT,
                valid_until DATETIME
        );"""
    ]

    # create a database connection
    try:
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()
    except sqlite3.Error as e:
        print(e)

def insert_user(user_name, password, email_address):
    try:
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (user_name, password, email_address) 
                VALUES (?, ?, ?, ?)
            """, (user_name, password, email_address))
            conn.commit()
            print("User inserted successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def view_all_users():
    try:
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    print(
                        f"user_id: {row[0]}, user_name: {row[1]}, email_address: {row[2]}"
                    )
            else:
                print("No users found in the table.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def insert_regulation():
    try:
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO regulation (bank, reg1, reg2, reg3, reg4, valid_until) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('bank1', 'dasdas', 'asdaa', 'sakdjsa', 'adasjdah', None))
            conn.commit()
            print("reg inserted successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


#create_user_table()
#create_proposition_table()
#insert_user('ruchibonkers', 'ruchibonkers', 'ruchibonkers', 'ruchibonkers@gmail.com')
#view_all_users()
#create_user_table()
#create_budget_table()
#create_regulation_table()
insert_regulation()