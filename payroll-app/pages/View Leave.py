import streamlit as st
import mysql.connector
from db import get_connection
from auth import require_role
from datetime import date

require_role(["Admin", "HR", "Employee"])
role = st.session_state.get("role")
emp_id = st.session_state.get("user_id")

st.title("📅 View & Manage Leave Balance")

try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Employee selection for Admin/HR
    if role in ["Admin", "HR"]:
        cursor.execute("""
            SELECT e.Employee_Id, u.Username
            FROM employee e
            JOIN user_roles u ON e.Employee_Id = u.Employee_Id
        """)
        employees = cursor.fetchall()
        employee_options = {f"{emp['Employee_Id']} - {emp['Username']}": emp['Employee_Id'] for emp in employees}
        selected_label = st.selectbox("👤 Choose Employee", list(employee_options.keys()))
        emp_id = employee_options[selected_label]
    else:
        st.markdown(f"👤 Viewing leave balance for your ID: `{emp_id}`")

    # Allow only Admin/HR to mark leave
    if role in ["Admin", "HR"]:
        st.markdown("### 📆 Mark Leave")
        selected_date = st.date_input("Choose Date", value=date.today())
        if st.button("Mark Absent"):
            try:
                cursor.execute("""
                    INSERT INTO Attendance (Employee_Id, Date, Status)
                    VALUES (%s, %s, 'Leave')
                """, (emp_id, selected_date))
                conn.commit()
                st.success(f"{selected_label} marked as on leave for {selected_date}. Leave balance updated.")
            except mysql.connector.Error as e:
                st.error(f"Database Error: {e}")

    st.markdown("---")

    # Show leave balance
    cursor.execute("""
        SELECT Total_Leaves, Leaves_Taken, (Total_Leaves - Leaves_Taken) AS Leaves_Remaining
        FROM Leave_Balance WHERE Employee_Id = %s
    """, (emp_id,))
    leave_data = cursor.fetchone()

    if leave_data:
        st.markdown(f"""
        **🗓️ Total Leaves:** {leave_data['Total_Leaves']}  
        **🚫 Leaves Taken:** {leave_data['Leaves_Taken']}  
        **✅ Leaves Remaining:** {leave_data['Leaves_Remaining']}
        """)
    else:
        st.warning("No leave balance data found for this employee.")

except mysql.connector.Error as e:
    st.error(f"MySQL connection error: {e}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
