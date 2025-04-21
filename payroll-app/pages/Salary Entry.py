import streamlit as st
import mysql.connector
from db import get_connection
from auth import require_role

st.set_page_config(page_title="Salary Entry", page_icon="💸")
st.title("💸 Salary Entry")

require_role(["Admin"])

# --- Salary Entry Form ---
st.subheader("💳 Submit Salary Details")

def submit_salary_details(emp_id, gross_salary, bank_name, account_number, ifsc_code):
    connection = get_connection()
    cursor = None
    try:
        cursor = connection.cursor()

        account_query = """
            INSERT INTO AccountDetails (Employee_Id, Bank_Name, Account_Number, IFSC_Code)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(account_query, (emp_id, bank_name, account_number, ifsc_code))

        cursor.execute("SELECT LAST_INSERT_ID()")
        account_id = cursor.fetchone()[0]

        salary_query = """
            INSERT INTO Salary (Gross_Salary, Account_Id)
            VALUES (%s, %s)
        """
        cursor.execute(salary_query, (gross_salary, account_id))

        cursor.execute("SELECT LAST_INSERT_ID()")
        salary_id = cursor.fetchone()[0]

        cursor.callproc("calculate_salary_components", [salary_id, gross_salary])

        connection.commit()
        st.success("✅ Salary and account details submitted successfully!")

    except mysql.connector.IntegrityError as e:
        st.error("❌ Duplicate account number or invalid data.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

emp_id = st.number_input("Employee ID", min_value=1)
gross_salary = st.number_input("Gross Salary (₹)", min_value=0.0, format="%.2f")
bank_name = st.text_input("Bank Name")
account_number = st.text_input("Account Number")
ifsc_code = st.text_input("IFSC Code")

if st.button("Submit Salary Details"):
    submit_salary_details(emp_id, gross_salary, bank_name, account_number, ifsc_code)

# --- Overtime Bonus Calculation ---
st.divider()
st.subheader("⏱️ Calculate Overtime Bonus")

# Employee selection dropdown
conn = get_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT e.Employee_Id, u.Username FROM employee e JOIN user_roles u ON e.Employee_Id = u.Employee_Id")
employees = cursor.fetchall()
emp_options = {f"{emp['Employee_Id']} - {emp['Username']}": emp['Employee_Id'] for emp in employees}
selected_emp = st.selectbox("Select Employee for Bonus", list(emp_options.keys()))
overtime_emp_id = emp_options[selected_emp]
cursor.close()
conn.close()

overtime_hours = st.number_input("Enter Overtime Hours", min_value=0)

overtime_pay = None
updated_salary = None

if st.button("Calculate Overtime Bonus"):
    connection = get_connection()
    cursor = None
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT Account_Id FROM AccountDetails WHERE Employee_Id = %s", (overtime_emp_id,))
        acc_result = cursor.fetchone()

        if acc_result:
            account_id = acc_result[0]
            cursor.execute("""
                SELECT Hourly_Pay, Gross_Salary FROM Salary
                WHERE Account_Id = %s
                ORDER BY Salary_Id DESC LIMIT 1
            """, (account_id,))
            result = cursor.fetchone()

            if result:
                hourly_pay, base_salary = result
                overtime_pay = hourly_pay * overtime_hours
                updated_salary = base_salary + overtime_pay

                cursor.execute("""
                    UPDATE Salary
                    SET Gross_Salary = Gross_Salary + %s
                    WHERE Account_Id = %s
                    ORDER BY Salary_Id DESC LIMIT 1
                """, (overtime_pay, account_id))
                connection.commit()

                st.success(f"✅ Overtime Pay: ₹{overtime_pay:.2f}")
                st.info(f"Updated Gross Salary (incl. Overtime): ₹{updated_salary:.2f}")
            else:
                st.warning("No salary record found for the employee.")
        else:
            st.warning("Employee account not found.")

    except Exception as e:
        st.error(f"Error during calculation: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# --- Bonus Award Section ---
st.divider()
st.subheader("🏱 Award Bonus for Project Completion")

project_id = st.number_input("Project ID", min_value=1)
bonus_amount = st.number_input("Bonus Amount", min_value=0)

if st.button("Award Bonus"):
    connection = get_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.callproc("award_bonus_to_project_employees", [project_id, bonus_amount])
        connection.commit()
        st.success("✅ Bonus awarded to all employees linked to this project.")
    except Exception as e:
        st.error(f"❌ Could not award bonus: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
