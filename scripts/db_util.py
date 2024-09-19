import sqlite3
import os
import pandas as pd

DB_DIR = "db"
USER_DB = 'user.db'
REPORTS_DIR = 'reports'

class UserNotFoundError(Exception):
    """Custom exception when a user is not found in the database."""
    pass

class PropositionDatabase:
    def __init__(self):
        self.db_path = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,USER_DB))
    
    def _get_connection(self):
        """Helper method to get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def fetch_propositions(self):
        """Fetch propositions from the database and return them as a list of dictionaries."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, bank, product_name, predicted_subscriber_take_out, 
                           revenue, (predicted_subscriber_take_out * CAST(revenue AS REAL)) as full_revenue, product_type, city
                    FROM proposition order by full_revenue desc
                """)
                
                propositions = []
                for row in cursor.fetchall():
                    print(row[0])
                    user = fetch_user_by_id(str(row[1]))
                    propositions.append({
                        "proposition_id": row[0],
                        "user_id": row[1],
                        "product_name": row[2],
                        "predicted_subscriber_take_out": row[3],
                        "revenue": row[4],
                        "full_revenue": row[5],
                        "product_type": row[6],
                        "city": row[7],
                        "team_name": user['team_name'] if user else ''
                    })
                
                if not propositions:
                    raise UserNotFoundError("No propositions found in the database.")
                
                return propositions

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None

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

def fetch_user_by_id(user_id):
    dbPath = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,USER_DB))
    print(dbPath)
    try:
        with sqlite3.connect(dbPath) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, user_name, team_name, email_address, bank 
                FROM users 
                WHERE user_id = ?
            """, (user_id))
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
                raise UserNotFoundError(f"User with user_id '{user_id}' not found.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def savePropositionResults(userId, bank, city, productType, subcount1, subcount2, subcount3, productName, revenue, moneyNeeds, customerExpNeeds, sustainabilityNeeds, matchingTopologies, predictedSubscriberTakeOut):
    dbPath = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,USER_DB))
    
    try:
        with sqlite3.connect(dbPath) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO proposition (user_id, bank, city, product_type, subcount1, subcount2, subcount3, product_name, revenue, money_needs, customer_exp_needs, sustainability_needs, matching_topologies, predicted_subscriber_take_out, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (userId, bank, city, productType, subcount1, subcount2, subcount3, productName, revenue, moneyNeeds, customerExpNeeds, sustainabilityNeeds, matchingTopologies, predictedSubscriberTakeOut))
            conn.commit()
            propositionId = cursor.lastrowid
            print("Proposition inserted successfully.")

            output = {'key':
            ['Bank','City', 'Product Type', 'Subscriber count for Year 1', 'Subscriber count for Year 2', 'Subscriber count for Year 3',
            'Product Name', 'Revenue per subscriber', ' Money Needs', 'Customer Needs', 'Sustainability Needs', 'Topologies you are targeting',
            'Predicted Subscriber Count', 'Total Revenue'], 'value': [
                bank, city, productType, subcount1, subcount2, subcount3, productName, revenue, moneyNeeds, customerExpNeeds, sustainabilityNeeds, matchingTopologies, predictedSubscriberTakeOut, (int(predictedSubscriberTakeOut)*int(revenue))
            ]}
        
            print(output)
            df = pd.DataFrame(output)
            reportsPath = os.path.abspath(os.path.join(os.getcwd(), REPORTS_DIR, 'Proposition_{}.csv'.format(propositionId)))
            df.to_csv(reportsPath, index=False)
            return propositionId

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")



#user = fetch_user('ruchibonkers', 'ruchibonkers')                 
#print(user)   

#insert_user('ruchibonkers', 'ruchibonkers', 'ruchibonkers', 'ruchibonkers@gmail.com')

# Example usage:
#dbPath = os.path.abspath(os.path.join(os.getcwd(), DB_DIR,'topologies.sqlite'))
#fetch_db_rows_as_dicts(dbPath, 'topologies')


#db = PropositionDatabase()
#p = db.fetch_propositions()
#print(p)