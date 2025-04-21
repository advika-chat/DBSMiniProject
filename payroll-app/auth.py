import mysql.connector
from mysql.connector import Error
from db import get_connection

def require_role(allowed_roles):
    import streamlit as st
    if 'role' not in st.session_state or st.session_state['role'] not in allowed_roles:
        st.error("Access denied.")
        st.stop()


def authenticate_user(username, password):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        print(f"Attempting login with Username: '{username}', Password: '{password}'")

        query = "SELECT * FROM User_Roles WHERE Username = %s AND Password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        print("User fetched from DB:", user)

        return user
    except Error as e:
        print("Database error:", e)
        return None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()



