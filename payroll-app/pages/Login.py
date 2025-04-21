import streamlit as st
from auth import authenticate_user

st.title("🔐 Employee Payroll Login")

# Show current login status
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    st.success(f"Logged in as {st.session_state['username']} ({st.session_state['role']})")

    # Sidebar message
    with st.sidebar:
        st.markdown("### 👤 Current User")
        st.markdown(f"**Username:** {st.session_state['username']}")
        st.markdown(f"**Role:** {st.session_state['role']}")

        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

else:
    # Login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user['User_Id']
            st.session_state['username'] = user['Username']
            st.session_state['role'] = user['Role']
            st.success(f"Welcome {user['Username']} ({user['Role']})")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")
