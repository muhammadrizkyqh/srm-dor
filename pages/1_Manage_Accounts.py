"""
Page: Manage SIRAMA Accounts
Add, edit, and delete multiple SIRAMA accounts
"""
import streamlit as st
from sirama_client import SiramaClient
from utils import show_error, show_success, show_info, validate_nim, get_status_emoji

st.set_page_config(page_title="Manage Accounts", page_icon="👥", layout="wide")

# Check authentication
if not st.session_state.get("authenticated"):
    st.error("Please login first!")
    st.stop()

st.title("👥 Manage SIRAMA Accounts")
st.markdown("Add and manage multiple SIRAMA accounts for automated KRS enrollment")
st.markdown("---")

# Get user accounts
accounts = st.session_state.supabase.get_accounts(st.session_state.user.id)

# Tabs for different actions
tab1, tab2 = st.tabs(["📋 My Accounts", "➕ Add New Account"])

# =============== TAB 1: LIST ACCOUNTS ===============
with tab1:
    st.subheader("Your SIRAMA Accounts")
    
    if not accounts:
        st.info("No accounts yet. Add your first SIRAMA account in the 'Add New Account' tab!")
    else:
        for account in accounts:
            with st.expander(f"{get_status_emoji(account['status'])} **{account['name'] or account['nim']}** ({account['nim']})", expanded=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**NIM:** {account['nim']}")
                    st.write(f"**Name:** {account['name'] or 'Not set'}")
                    st.write(f"**Status:** {account['status'].upper()}")
                    
                    # Get course targets count
                    targets = st.session_state.supabase.get_course_targets(account['id'])
                    st.write(f"**Target Courses:** {len(targets)}")
                    
                    # Get stats
                    stats = st.session_state.supabase.get_enrollment_stats(account['id'])
                    st.write(f"**Total Enrollments:** {stats['success']}/{stats['total']}")
                
                with col2:
                    # Test connection button
                    if st.button("🔍 Test Connection", key=f"test_{account['id']}", use_container_width=True):
                        with st.spinner("Testing connection..."):
                            try:
                                # Decrypt password and test login
                                decrypted_pwd = st.session_state.supabase.decrypt_password(account['password_encrypted'])
                                client = SiramaClient()
                                result = client.login(account['nim'], decrypted_pwd)
                                
                                if result['success']:
                                    # Get profile
                                    profile_result = client.get_profile()
                                    if profile_result['success']:
                                        show_success(f"Connection successful! Hello, {profile_result['profile'].get('name', 'Student')}!")
                                    else:
                                        show_error("Login successful but failed to get profile")
                                else:
                                    show_error(f"Connection failed: {result.get('message', 'Unknown error')}")
                            except Exception as e:
                                show_error(f"Test failed: {str(e)}")
                    
                    # Toggle status button
                    new_status = "inactive" if account['status'] == "active" else "active"
                    status_label = "🔴 Deactivate" if account['status'] == "active" else "🟢 Activate"
                    
                    if st.button(status_label, key=f"toggle_{account['id']}", use_container_width=True):
                        result = st.session_state.supabase.update_account(account['id'], status=new_status)
                        if result['success']:
                            show_success(f"Account {new_status}d successfully!")
                            st.rerun()
                        else:
                            show_error(f"Failed to update status: {result.get('message')}")
                
                with col3:
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_{account['id']}", use_container_width=True):
                        st.session_state.editing_account = account['id']
                        st.rerun()
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_{account['id']}", use_container_width=True, type="secondary"):
                        if st.session_state.get(f"confirm_delete_{account['id']}"):
                            result = st.session_state.supabase.delete_account(account['id'])
                            if result['success']:
                                show_success("Account deleted successfully!")
                                st.rerun()
                            else:
                                show_error(f"Failed to delete: {result.get('message')}")
                        else:
                            st.session_state[f"confirm_delete_{account['id']}"] = True
                            show_info("Click delete again to confirm")
                
                # Edit form (shown if editing)
                if st.session_state.get("editing_account") == account['id']:
                    st.markdown("---")
                    with st.form(f"edit_form_{account['id']}"):
                        st.write("**Edit Account**")
                        new_name = st.text_input("Name", value=account['name'] or "")
                        new_password = st.text_input("New Password (leave empty to keep current)", type="password")
                        
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
                        with col_cancel:
                            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
                        
                        if submitted:
                            updates = {"name": new_name}
                            if new_password:
                                updates["password"] = new_password
                            
                            result = st.session_state.supabase.update_account(account['id'], **updates)
                            if result['success']:
                                show_success("Account updated successfully!")
                                del st.session_state.editing_account
                                st.rerun()
                            else:
                                show_error(f"Update failed: {result.get('message')}")
                        
                        if cancelled:
                            del st.session_state.editing_account
                            st.rerun()

# =============== TAB 2: ADD NEW ACCOUNT ===============
with tab2:
    st.subheader("Add New SIRAMA Account")
    st.write("Add credentials to enable automated course enrollment")
    
    with st.form("add_account_form"):
        nim = st.text_input(
            "Username SIRAMA", 
            placeholder="muhammadrizkyqh (username email tanpa @telkomuniversity.ac.id)",
            help="Masukkan username email Telkom University Anda (bagian sebelum @)"
        )
        password = st.text_input("SIRAMA Password", type="password")
        name = st.text_input("Name (optional)", placeholder="Your full name")
        
        test_before_save = st.checkbox("Test connection before saving", value=True)
        
        submitted = st.form_submit_button("➕ Add Account", use_container_width=True)
        
        if submitted:
            # Validation
            if not nim or not password:
                show_error("Username and password are required!")
            else:
                # Test connection first if requested
                if test_before_save:
                    with st.spinner("Testing connection to SIRAMA..."):
                        client = SiramaClient()
                        login_result = client.login(nim, password)
                        
                        if not login_result['success']:
                            show_error(f"Login test failed: {login_result.get('message', 'Invalid credentials')}")
                            st.stop()
                        
                        # Get profile to verify and get name
                        profile_result = client.get_profile()
                        if profile_result['success']:
                            profile = profile_result['profile']
                            if not name:
                                name = profile.get('name', '')
                            show_success(f"Connection test successful! Hello, {profile.get('name', 'Student')}!")
                        else:
                            show_error("Failed to retrieve profile")
                            st.stop()
                
                # Save to database
                result = st.session_state.supabase.create_account(
                    user_id=st.session_state.user.id,
                    nim=nim,
                    password=password,
                    name=name
                )
                
                if result['success']:
                    show_success(f"Account for {nim} added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    show_error(f"Failed to add account: {result.get('message', 'Unknown error')}")

st.markdown("---")
st.caption("💡 Tip: Keep your accounts active for automated enrollment. You can deactivate temporarily if needed.")
