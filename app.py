"""
SIRAMA Auto-KRS Bot - Main Application
"""
import streamlit as st
from supabase_client import SupabaseClient
from utils import show_error, show_success

# Page configuration
st.set_page_config(
    page_title="SIRAMA Auto-KRS Bot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = SupabaseClient()
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {str(e)}")
        st.info("""
        **Setup Required:**
        1. Copy `.env.example` to `.env`
        2. Add your Supabase credentials
        3. Generate encryption key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
        """)
        st.stop()


def check_authentication():
    """Check if user is authenticated"""
    if not st.session_state.authenticated:
        show_login_page()
        st.stop()


def show_login_page():
    """Display login/register page"""
    st.title("🎓 SIRAMA Auto-KRS Bot")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    show_error("Email and password are required")
                else:
                    result = st.session_state.supabase.sign_in(email, password)
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = result["user"]
                        show_success(f"Welcome back, {email}!")
                        st.rerun()
                    else:
                        show_error(f"Login failed: {result.get('message', 'Unknown error')}")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            email = st.text_input("Email", placeholder="your.email@example.com", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    show_error("All fields are required")
                elif password != confirm_password:
                    show_error("Passwords do not match")
                elif len(password) < 6:
                    show_error("Password must be at least 6 characters")
                else:
                    result = st.session_state.supabase.sign_up(email, password)
                    if result["success"]:
                        show_success("Account created! Please login.")
                    else:
                        show_error(f"Registration failed: {result.get('message', 'Unknown error')}")


def main():
    """Main application"""
    check_authentication()
    
    # Sidebar
    with st.sidebar:
        st.title("🎓 SIRAMA Bot")
        st.markdown("---")
        
        # User info
        if st.session_state.user:
            st.write(f"👤 **{st.session_state.user.email}**")
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "👥 Manage Accounts", "🎯 Target Courses", "🚀 Auto-Enroll", "📋 Logs"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.supabase.sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # Main content
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "👥 Manage Accounts":
        show_accounts_page()
    elif page == "🎯 Target Courses":
        show_targets_page()
    elif page == "🚀 Auto-Enroll":
        show_auto_enroll_page()
    elif page == "📋 Logs":
        show_logs_page()


def show_dashboard():
    """Dashboard page"""
    st.title("📊 Dashboard")
    st.markdown("---")
    
    # Get user accounts
    accounts = st.session_state.supabase.get_accounts(st.session_state.user.id)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Accounts", len(accounts))
    
    with col2:
        active_accounts = len([a for a in accounts if a["status"] == "active"])
        st.metric("Active Accounts", active_accounts)
    
    with col3:
        total_targets = 0
        for account in accounts:
            targets = st.session_state.supabase.get_course_targets(account["id"])
            total_targets += len(targets)
        st.metric("Target Courses", total_targets)
    
    with col4:
        total_logs = 0
        for account in accounts:
            logs = st.session_state.supabase.get_enrollment_logs(account["id"], limit=1000)
            total_logs += len(logs)
        st.metric("Total Enrollments", total_logs)
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📌 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add New Account", use_container_width=True):
            st.switch_page("pages/1_Manage_Accounts.py")
    
    with col2:
        if st.button("🎯 Set Targets", use_container_width=True):
            st.switch_page("pages/2_Target_Courses.py")
    
    with col3:
        if st.button("🚀 Run Enrollment", use_container_width=True):
            st.switch_page("pages/3_Auto_Enroll.py")
    
    st.markdown("---")
    
    # Recent logs
    st.subheader("📋 Recent Activity")
    
    all_logs = []
    for account in accounts:
        logs = st.session_state.supabase.get_enrollment_logs(account["id"], limit=10)
        all_logs.extend(logs)
    
    # Sort by date
    all_logs.sort(key=lambda x: x["created_at"], reverse=True)
    
    if all_logs:
        import pandas as pd
        from utils import format_datetime, get_status_emoji
        
        df = pd.DataFrame(all_logs[:10])
        df["created_at"] = df["created_at"].apply(format_datetime)
        df["status_icon"] = df["status"].apply(get_status_emoji)
        df["action_icon"] = df["action"].apply(get_status_emoji)
        
        st.dataframe(
            df[["created_at", "action_icon", "course_name", "status_icon", "message"]],
            column_config={
                "created_at": "Time",
                "action_icon": "Action",
                "course_name": "Course",
                "status_icon": "Status",
                "message": "Message"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No recent activity. Start by adding a SIRAMA account!")


def show_accounts_page():
    """Manage accounts page - placeholder"""
    st.title("👥 Manage SIRAMA Accounts")
    st.info("This page will be implemented in pages/1_Manage_Accounts.py")


def show_targets_page():
    """Target courses page - placeholder"""
    st.title("🎯 Target Courses")
    st.info("This page will be implemented in pages/2_Target_Courses.py")


def show_auto_enroll_page():
    """Auto-enroll page - placeholder"""
    st.title("🚀 Auto-Enroll")
    st.info("This page will be implemented in pages/3_Auto_Enroll.py")


def show_logs_page():
    """Logs page - placeholder"""
    st.title("📋 Enrollment Logs")
    st.info("This page will be implemented in pages/4_Logs.py")


if __name__ == "__main__":
    main()
