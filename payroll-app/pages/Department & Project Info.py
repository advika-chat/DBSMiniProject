import streamlit as st
import mysql.connector
from db import get_connection
from auth import require_role

require_role(["Admin", "HR", "Employee"])
role = st.session_state.get("role")
user_id = st.session_state.get("user_id")

st.set_page_config(page_title="Departments & Projects", page_icon="🏢")
st.title("🏢 Departments & Projects Overview")

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# --- Admin UI for Adding Data ---
if role == "Admin":
    st.subheader("➕ Add Department")
    new_dept = st.text_input("Department Name")
    if st.button("Add Department"):
        try:
            cursor.execute("INSERT INTO Department (Department_Name) VALUES (%s)", (new_dept,))
            conn.commit()
            st.success("Department added successfully.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.subheader("➕ Add Project")
    cursor.execute("SELECT * FROM Department")
    dept_rows = cursor.fetchall()
    dept_map = {row['Department_Name']: row['Department_Id'] for row in dept_rows}
    project_name = st.text_input("Project Name")
    selected_dept = st.selectbox("Assign to Department", list(dept_map.keys()))
    if st.button("Add Project"):
        try:
            cursor.execute("INSERT INTO Project (Project_Name) VALUES (%s)", (project_name,))
            project_id = cursor.lastrowid
            cursor.execute("INSERT INTO Department_Project (Department_Id, Project_Id) VALUES (%s, %s)", (dept_map[selected_dept], project_id))
            conn.commit()
            st.success("Project added and linked to department.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.subheader("👤 Add Employee to Department and Project")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    dob = st.date_input("Date of Birth")
    designation = st.text_input("Designation")
    emp_dept = st.selectbox("Department", list(dept_map.keys()), key="emp_dept")
    cursor.execute("SELECT Project_Name FROM Project")
    proj_names = [row['Project_Name'] for row in cursor.fetchall()]
    proj_names = []

    emp_proj = st.selectbox("Assign Project", proj_names, key="emp_proj")

    if st.button("Add Employee"):
        try:
            cursor.execute("INSERT INTO Employee (First_Name, Last_Name, Date_Of_Birth, Gender, Phone_Number, Email, Department_Id, Designation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (first_name, last_name, dob, gender, phone, email, dept_map[emp_dept], designation))
            emp_id = cursor.lastrowid
            cursor.execute("SELECT Project_Id FROM Project WHERE Project_Name = %s", (emp_proj,))
            project_id = cursor.fetchone()['Project_Id']
            cursor.execute("INSERT INTO Department_Project (Department_Id, Project_Id) VALUES (%s, %s)", (dept_map[emp_dept], project_id))
            conn.commit()
            st.success("Employee added and assigned to department and project.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Filter UI ---
cursor.execute("SELECT Department_Name FROM Department")
dept_options = [row['Department_Name'] for row in cursor.fetchall()]
selected_filter = st.selectbox("📊 Filter by Department", ["All"] + dept_options)

# --- Query to Show Project Assignments ---
query = """
    SELECT 
        d.Department_Name,
        p.Project_Name,
        e.Employee_Id,
        CONCAT(e.First_Name, ' ', e.Last_Name) AS Employee_Name
    FROM Department d
    JOIN Department_Project dp ON d.Department_Id = dp.Department_Id
    JOIN Project p ON dp.Project_Id = p.Project_Id
    JOIN Employee e ON e.Department_Id = d.Department_Id
"""
params = []

if role == "Employee":
    query += " WHERE e.Employee_Id = %s"
    params.append(user_id)
elif selected_filter != "All":
    query += " WHERE d.Department_Name = %s"
    params.append(selected_filter)

query += " ORDER BY d.Department_Name, p.Project_Name"

cursor.execute(query, params)
data = cursor.fetchall()

if data:
    st.subheader("📄 Department-wise Project Assignments")
    st.dataframe(data)
else:
    st.info("No data found for the selected criteria.")

cursor.close()
conn.close()
