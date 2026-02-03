"""
Page: Enrollment Logs
View history and statistics of course enrollments
"""
import streamlit as st
import pandas as pd
from utils import format_datetime, get_status_emoji
from datetime import datetime, timedelta

st.set_page_config(page_title="Enrollment Logs", page_icon="📋", layout="wide")

# Check authentication
if not st.session_state.get("authenticated"):
    st.error("Please login first!")
    st.stop()

st.title("📋 Enrollment Logs")
st.markdown("View enrollment history and statistics")
st.markdown("---")

# Get user accounts
accounts = st.session_state.supabase.get_accounts(st.session_state.user.id)

if not accounts:
    st.info("No accounts yet. Add an account to start tracking enrollment history!")
    st.stop()

# Filters
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    selected_account_id = st.selectbox(
        "Filter by Account",
        options=["all"] + [acc['id'] for acc in accounts],
        format_func=lambda x: "All Accounts" if x == "all" else f"{next((a['name'] or a['nim'] for a in accounts if a['id'] == x), 'Unknown')} ({next((a['nim'] for a in accounts if a['id'] == x), '')})"
    )

with col2:
    status_filter = st.selectbox(
        "Filter by Status",
        options=["all", "success", "failed"]
    )

with col3:
    limit = st.number_input("Max logs", min_value=10, max_value=500, value=100)

st.markdown("---")

# Get logs
if selected_account_id == "all":
    all_logs = []
    for account in accounts:
        logs = st.session_state.supabase.get_enrollment_logs(
            account_id=account['id'],
            limit=limit,
            status_filter=None if status_filter == "all" else status_filter
        )
        # Add account info to logs
        for log in logs:
            log['account_name'] = account['name'] or account['nim']
            log['account_nim'] = account['nim']
        all_logs.extend(logs)
    
    # Sort by date
    all_logs.sort(key=lambda x: x['created_at'], reverse=True)
    logs = all_logs[:limit]
else:
    logs = st.session_state.supabase.get_enrollment_logs(
        account_id=selected_account_id,
        limit=limit,
        status_filter=None if status_filter == "all" else status_filter
    )
    selected_account = next((a for a in accounts if a['id'] == selected_account_id), None)
    if selected_account:
        for log in logs:
            log['account_name'] = selected_account['name'] or selected_account['nim']
            log['account_nim'] = selected_account['nim']

# Statistics
if logs:
    st.subheader("📊 Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_logs = len(logs)
    success_logs = len([l for l in logs if l['status'] == 'success'])
    failed_logs = len([l for l in logs if l['status'] == 'failed'])
    success_rate = (success_logs / total_logs * 100) if total_logs > 0 else 0
    
    with col1:
        st.metric("Total Attempts", total_logs)
    
    with col2:
        st.metric("Successful", success_logs, delta=f"{success_rate:.1f}%")
    
    with col3:
        st.metric("Failed", failed_logs)
    
    with col4:
        add_count = len([l for l in logs if l['action'] == 'add'])
        drop_count = len([l for l in logs if l['action'] == 'drop'])
        st.metric("Add/Drop", f"{add_count}/{drop_count}")
    
    st.markdown("---")
    
    # Logs table
    st.subheader("📜 Enrollment History")
    
    if logs:
        # Prepare dataframe
        df = pd.DataFrame(logs)
        
        # Format columns
        df['Time'] = df['created_at'].apply(format_datetime)
        df['Account'] = df.apply(lambda x: f"{x['account_name']} ({x['account_nim']})", axis=1) if 'account_name' in df.columns else df.get('account_nim', 'Unknown')
        df['Action'] = df['action'].apply(lambda x: '➕ Add' if x == 'add' else '➖ Drop')
        df['Course'] = df['course_name']
        df['Status'] = df['status'].apply(lambda x: '✅ Success' if x == 'success' else '❌ Failed')
        df['Message'] = df['message'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x)
        
        # Display table
        st.dataframe(
            df[['Time', 'Account', 'Action', 'Course', 'Status', 'Message']],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Time": st.column_config.TextColumn("Time", width="medium"),
                "Account": st.column_config.TextColumn("Account", width="medium"),
                "Action": st.column_config.TextColumn("Action", width="small"),
                "Course": st.column_config.TextColumn("Course", width="large"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Message": st.column_config.TextColumn("Message", width="large")
            }
        )
        
        # Export option
        st.markdown("---")
        st.subheader("📥 Export Logs")
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"enrollment_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No logs found for selected filters")
    
    # Success/Fail Distribution
    if total_logs > 0:
        st.markdown("---")
        st.subheader("📈 Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**By Status:**")
            status_data = pd.DataFrame({
                'Status': ['Success', 'Failed'],
                'Count': [success_logs, failed_logs]
            })
            st.bar_chart(status_data.set_index('Status'))
        
        with col2:
            st.write("**By Action:**")
            action_data = pd.DataFrame({
                'Action': ['Add', 'Drop'],
                'Count': [add_count, drop_count]
            })
            st.bar_chart(action_data.set_index('Action'))

else:
    st.info("No enrollment logs yet. Run your first enrollment to see history here!")
    if st.button("🚀 Go to Auto-Enroll"):
        st.switch_page("pages/3_Auto_Enroll.py")

st.markdown("---")
st.caption("💡 Logs are kept permanently. You can filter and export them anytime.")
