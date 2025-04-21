import streamlit as st
from db import get_connection
from auth import require_role

# Enforce login and role restrictions
require_role(["Admin", "HR", "Employee"])
role = st.session_state.get("role")
user_id = st.session_state.get("user_id")

st.title("📊 Tax Summary Report")

try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if role == "Employee":
        # Employee sees only their own latest tax summary
        query = """
            SELECT 
                s.Salary_Id,
                a.Employee_Id,
                CONCAT(e.First_Name, ' ', e.Last_Name) AS Employee_Name,
                s.Gross_Salary,
                s.Provident_Fund,
                s.Income_Tax,
                (s.Gross_Salary - s.Provident_Fund - s.Income_Tax) AS Net_Salary
            FROM Salary s
            JOIN AccountDetails a ON s.Account_Id = a.Account_Id
            JOIN Employee e ON a.Employee_Id = e.Employee_Id
            WHERE a.Employee_Id = %s
            ORDER BY s.Salary_Id DESC
            LIMIT 1
        """
        cursor.execute(query, (user_id,))
        records = cursor.fetchall()

    else:
        # Admin and HR can view all tax summaries
        query = """
            SELECT 
                s.Salary_Id,
                a.Employee_Id,
                CONCAT(e.First_Name, ' ', e.Last_Name) AS Employee_Name,
                s.Gross_Salary,
                s.Provident_Fund,
                s.Income_Tax,
                (s.Gross_Salary - s.Provident_Fund - s.Income_Tax) AS Net_Salary
            FROM Salary s
            JOIN AccountDetails a ON s.Account_Id = a.Account_Id
            JOIN Employee e ON a.Employee_Id = e.Employee_Id
            ORDER BY s.Salary_Id DESC
        """
        cursor.execute(query)
        records = cursor.fetchall()

    # Display results
    if records:
        st.dataframe(records, use_container_width=True)
    else:
        st.info("No tax summary records found.")

except Exception as e:
    st.error(f"❌ Error loading tax data: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
