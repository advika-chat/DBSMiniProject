import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Admin_123",
            database="PayRollDB"
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None