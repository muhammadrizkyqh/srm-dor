"""
Page: Manage Courses
View enrolled courses, browse available courses, and add/drop courses
"""
import streamlit as st
from utils import show_error, show_success, show_info, show_warning
from sirama_client import SiramaClient

st.set_page_config(page_title="Manage Courses", page_icon="📚", layout="wide")

# Check authentication
if not st.session_state.get("authenticated"):
    st.error("Please login first!")
    st.stop()

st.title("📚 Manage Courses")
st.markdown("View and manage your course registration (KRS)")
st.markdown("---")

# Get user accounts
accounts = st.session_state.supabase.get_accounts(st.session_state.user.id)

if not accounts:
    st.warning("No SIRAMA accounts found. Please add an account first!")
    if st.button("➕ Add Account"):
        st.switch_page("pages/1_Manage_Accounts.py")
    st.stop()

# Select account
selected_account_id = st.selectbox(
    "Select SIRAMA Account",
    options=[acc['id'] for acc in accounts],
    format_func=lambda x: f"{next((a['name'] or a['nim'] for a in accounts if a['id'] == x), 'Unknown')} - {next((a['nim'] for a in accounts if a['id'] == x), '')}"
)

selected_account = next((a for a in accounts if a['id'] == selected_account_id), None)

if selected_account:
    st.markdown(f"### Managing courses for: **{selected_account['name'] or selected_account['nim']}** ({selected_account['nim']})")
    
    # Initialize SIRAMA session
    if f'token_{selected_account_id}' not in st.session_state:
        st.session_state[f'token_{selected_account_id}'] = None
        st.session_state[f'student_id_{selected_account_id}'] = None
        st.session_state[f'logged_in_{selected_account_id}'] = False
    
    # Login section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state[f'logged_in_{selected_account_id}']:
            profile = st.session_state.get(f'profile_{selected_account_id}', {})
            st.success(f"✅ Logged in as {profile.get('fullname', selected_account['nim'])}")
        else:
            st.info("👆 Please login to SIRAMA first")
    
    with col2:
        if not st.session_state[f'logged_in_{selected_account_id}']:
            if st.button("🔐 Login to SIRAMA", use_container_width=True, type="primary"):
                with st.spinner("Logging in..."):
                    try:
                        client = SiramaClient()
                        decrypted_password = st.session_state.supabase.decrypt_password(selected_account['password_encrypted'])
                        
                        login_result = client.login(selected_account['nim'], decrypted_password)
                        
                        if login_result['success']:
                            # Get profile
                            profile_result = client.get_profile()
                            
                            if profile_result['success']:
                                # Store token and student_id in session
                                st.session_state[f'token_{selected_account_id}'] = client.token
                                st.session_state[f'student_id_{selected_account_id}'] = client.student_id
                                st.session_state[f'logged_in_{selected_account_id}'] = True
                                st.session_state[f'profile_{selected_account_id}'] = profile_result['profile']
                                show_success(f"Welcome, {profile_result['profile'].get('fullname', 'Student')}!")
                                st.rerun()
                            else:
                                show_error(f"Failed to get profile: {profile_result.get('message')}")
                        else:
                            show_error(f"Login failed: {login_result.get('message')}")
                    except Exception as e:
                        show_error(f"Error: {str(e)}")
        else:
            if st.button("🔓 Logout", use_container_width=True):
                st.session_state[f'token_{selected_account_id}'] = None
                st.session_state[f'student_id_{selected_account_id}'] = None
                st.session_state[f'logged_in_{selected_account_id}'] = False
                st.session_state[f'profile_{selected_account_id}'] = None
                st.session_state.pop(f'enrolled_{selected_account_id}', None)
                st.session_state.pop(f'available_{selected_account_id}', None)
                show_info("Logged out successfully")
                st.rerun()
    
    st.markdown("---")
    
    # Only show course management if logged in
    if st.session_state[f'logged_in_{selected_account_id}']:
        # Create client with stored token and student_id
        client = SiramaClient()
        client.token = st.session_state[f'token_{selected_account_id}']
        client.student_id = st.session_state[f'student_id_{selected_account_id}']
        
        # Ensure session is initialized
        if not hasattr(client, 'session') or client.session is None:
            import requests
            client.session = requests.Session()
        
        # =============== ENROLLED COURSES SECTION ===============
        st.markdown("## 📋 Enrolled Courses (KRS Aktif)")
        
        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button("🔄 Refresh Enrolled", use_container_width=True):
                with st.spinner("Fetching enrolled courses..."):
                    try:
                        enrolled_result = client.get_enrolled_courses()
                        if enrolled_result['success']:
                            st.session_state[f'enrolled_{selected_account_id}'] = enrolled_result.get('courses', [])
                            show_success(f"Found {len(enrolled_result.get('courses', []))} enrolled courses!")
                            st.rerun()
                        else:
                            show_error(f"Failed to fetch: {enrolled_result.get('message')}")
                    except Exception as e:
                        show_error(f"Error: {str(e)}")
        
        # Display enrolled courses
        enrolled_courses = st.session_state.get(f'enrolled_{selected_account_id}', [])
        
        # Ensure enrolled_courses is a list
        if not isinstance(enrolled_courses, list):
            enrolled_courses = []
            st.session_state[f'enrolled_{selected_account_id}'] = []
        
        if enrolled_courses:
            total_credits = sum(c.get('credit', 0) for c in enrolled_courses if isinstance(c, dict))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Courses", len(enrolled_courses))
            with col2:
                st.metric("Total Credits (SKS)", total_credits)
            with col3:
                max_credit = st.session_state.get(f'profile_{selected_account_id}', {}).get('max_credit', 24)
                st.metric("Max Allowed", f"{max_credit} SKS")
            
            st.markdown("")
            
            # Add schedule preview button
            if st.button("📅 Preview Schedule", use_container_width=True, type="secondary"):
                with st.spinner("Loading schedule..."):
                    schedule_result = client.get_schedule()
                    if schedule_result['success']:
                        st.session_state[f'schedule_{selected_account_id}'] = schedule_result.get('schedule', [])
                        st.session_state[f'show_schedule_{selected_account_id}'] = True
                        st.rerun()
                    else:
                        show_error(f"Failed to load schedule: {schedule_result.get('message')}")
            
            # Display schedule if loaded
            if st.session_state.get(f'show_schedule_{selected_account_id}', False):
                schedule_data = st.session_state.get(f'schedule_{selected_account_id}', [])
                
                if schedule_data:
                    st.markdown("### 📅 Weekly Schedule Preview")
                    
                    # Close button
                    if st.button("❌ Close Schedule", use_container_width=True):
                        st.session_state[f'show_schedule_{selected_account_id}'] = False
                        st.rerun()
                    
                    # Create schedule table
                    import pandas as pd
                    
                    # Days of week
                    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                    day_labels = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                    
                    # Detect conflicts
                    conflicts = []
                    for shift in schedule_data:
                        time = shift.get('shift_time', 'N/A')
                        shift_data = shift.get('shift_data', {})
                        for day, day_label in zip(days, day_labels):
                            courses = shift_data.get(day, [])
                            if len(courses) > 1:  # Conflict detected!
                                course_details = []
                                for c in courses:
                                    course_name = c.get('course_name', 'Unknown')
                                    start = c.get('start_hour', 'N/A')
                                    end = c.get('end_hour', 'N/A')
                                    course_details.append(f"{course_name} ({start}-{end})")
                                conflicts.append({
                                    'day': day_label,
                                    'time': time,
                                    'courses': course_details
                                })
                    
                    # Show conflict warning
                    if conflicts:
                        st.error(f"⚠️ **Terdeteksi {len(conflicts)} jadwal yang bentrok!**")
                        with st.expander("📋 Detail Bentrokan Jadwal", expanded=True):
                            for conflict in conflicts:
                                st.warning(f"**{conflict['day']} - {conflict['time']}**")
                                for course in conflict['courses']:
                                    st.write(f"  • {course}")
                    else:
                        st.success("✅ Tidak ada jadwal yang bentrok")
                    
                    st.markdown("---")
                    
                    # Build schedule dict
                    schedule_dict = {"Time": []}
                    for day_label in day_labels:
                        schedule_dict[day_label] = []
                    
                    for shift in schedule_data:
                        time = shift.get('shift_time', 'N/A')
                        schedule_dict["Time"].append(time)
                        
                        shift_data = shift.get('shift_data', {})
                        for day, day_label in zip(days, day_labels):
                            courses = shift_data.get(day, [])
                            if courses:
                                course_details = []
                                for c in courses:
                                    course_name = c.get('course_name', 'Unknown')
                                    start = c.get('start_hour', 'N/A')
                                    end = c.get('end_hour', 'N/A')
                                    sks = c.get('credit', '')
                                    course_details.append(f"{course_name}\n({start}-{end}, {sks} SKS)")
                                
                                # Add conflict indicator
                                if len(courses) > 1:
                                    cell_value = "⚠️ BENTROK!\n" + "\n---\n".join(course_details)
                                else:
                                    cell_value = "\n".join(course_details)
                                schedule_dict[day_label].append(cell_value)
                            else:
                                schedule_dict[day_label].append("")
                    
                    # Create DataFrame
                    df_schedule = pd.DataFrame(schedule_dict)
                    
                    # Display with custom styling
                    st.dataframe(
                        df_schedule,
                        use_container_width=True,
                        height=600,
                        hide_index=True
                    )
                    
                    st.markdown("---")
            
            # Table view
            for course in enrolled_courses:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{course.get('subject_name', 'Unknown')}**")
                        st.caption(f"Code: {course.get('subject_code', 'N/A')} | Class: {course.get('class', 'N/A')}")
                    
                    with col2:
                        color = course.get('color', 'N/A')
                        if color == 'WAJIB PRODI':
                            st.write("🔴 " + color)
                        elif color == 'PILIHAN':
                            st.write("🟡 " + color)
                        else:
                            st.write("🔵 " + color)
                    
                    with col3:
                        st.write(f"**{course.get('credit', 0)} SKS**")
                    
                    with col4:
                        status = course.get('taking_status', 'N/A')
                        if status == 'FIX':
                            st.write("✅ FIX")
                        else:
                            st.write(f"⚠️ {status}")
                    
                    with col5:
                        # Drop button
                        if st.button("🗑️ Drop", key=f"drop_{course.get('course_id')}", use_container_width=True):
                            drop_hash = '05d8af8b7a6a9b1a1a16be2841ec0152c8e6ec31'
                            
                            with st.spinner(f"Dropping course..."):
                                try:
                                    # Create fresh client
                                    drop_client = SiramaClient()
                                    drop_client.token = st.session_state[f'token_{selected_account_id}']
                                    drop_client.student_id = st.session_state[f'student_id_{selected_account_id}']
                                    
                                    if not hasattr(drop_client, 'session') or drop_client.session is None:
                                        import requests
                                        drop_client.session = requests.Session()
                                    
                                    # Use registrationid for drop, not course_id
                                    registration_id = str(course.get('registrationid', course.get('course_id')))
                                    course_id = str(course.get('course_id'))
                                    
                                    drop_result = drop_client.drop_course(registration_id, drop_hash, flag="1")
                                    
                                    if drop_result['success']:
                                        # Log to database
                                        st.session_state.supabase.log_enrollment(
                                            account_id=selected_account_id,
                                            action='drop',
                                            course_id=course_id,
                                            course_name=course.get('subject_name', 'Unknown'),
                                            status='success',
                                            message=drop_result.get('message', 'Successfully dropped')
                                        )
                                        show_success(f"✅ Successfully dropped {course.get('subject_name')}!")
                                        
                                        # Refresh enrolled courses
                                        enrolled_result = drop_client.get_enrolled_courses()
                                        if enrolled_result['success']:
                                            st.session_state[f'enrolled_{selected_account_id}'] = enrolled_result.get('courses', [])
                                        
                                        st.rerun()
                                    else:
                                        # Log failure
                                        st.session_state.supabase.log_enrollment(
                                            account_id=selected_account_id,
                                            action='drop',
                                            course_id=course_id,
                                            course_name=course.get('subject_name', 'Unknown'),
                                            status='failed',
                                            message=drop_result.get('message', 'Failed to drop')
                                        )
                                        show_error(f"Failed: {drop_result.get('message')}")
                                except Exception as e:
                                    show_error(f"Error: {str(e)}")
                    
                    st.markdown("---")
        
        else:
            st.info("👆 Click 'Refresh Enrolled' to load your enrolled courses")
        
        st.markdown("---")
        
        # =============== AVAILABLE COURSES SECTION ===============
        st.markdown("## 📚 Browse Available Courses")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            study_program_id = st.number_input("Study Program ID", min_value=1, value=117, help="Default: 117 (Informatika S1)")
        
        with col2:
            semester = st.number_input("Tingkat", min_value=1, max_value=8, value=2, help="Tingkat semester (1-8)")
        
        with col3:
            show_full_only = st.checkbox("Hide full courses", value=True)
        
        with col4:
            if st.button("🔍 Fetch Available", use_container_width=True, type="primary"):
                with st.spinner("Fetching available courses..."):
                    try:
                        courses_result = client.get_available_courses(study_program_id, semester)
                        
                        if courses_result['success']:
                            st.session_state[f'available_{selected_account_id}'] = courses_result.get('courses', [])
                            show_success(f"Found {len(courses_result.get('courses', []))} available courses!")
                            st.rerun()
                        else:
                            show_error(f"Failed to fetch: {courses_result.get('message')}")
                    except Exception as e:
                        show_error(f"Error: {str(e)}")
        
        # Display available courses
        available_courses = st.session_state.get(f'available_{selected_account_id}', [])
        
        if available_courses:
            # Filter
            if show_full_only:
                available_courses = [c for c in available_courses if c.get('remaining_quota', 0) > 0]
            
            # Search
            search = st.text_input("🔍 Search course name", placeholder="Type to filter...")
            if search:
                available_courses = [c for c in available_courses if search.lower() in c.get('subject_name', '').lower()]
            
            st.write(f"**Showing {len(available_courses)} courses**")
            st.markdown("")
            
            # Get currently enrolled course IDs
            enrolled_ids = [str(c.get('course_id')) for c in st.session_state.get(f'enrolled_{selected_account_id}', [])]
            
            # Display courses
            for course in available_courses:
                course_id = str(course.get('courseid', ''))
                subject_name = course.get('subject_name', 'Unknown')
                class_name = course.get('class', 'N/A')
                quota = course.get('quota', 0)
                remaining = course.get('remaining_quota', 0)
                subject_code = course.get('subject_code', 'N/A')
                credit = course.get('credit', 'N/A')
                color = course.get('color', '')
                
                is_enrolled = course_id in enrolled_ids
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{subject_name}**")
                        st.caption(f"Code: {subject_code} | Class: {class_name} | Credits: {credit} SKS")
                        if color:
                            st.caption(f"🏷️ {color}")
                    
                    with col2:
                        st.write(f"📊 **Quota:** {remaining}/{quota}")
                        if remaining == 0:
                            st.caption("🔴 Full")
                        elif remaining < 5:
                            st.caption("🟡 Almost full")
                        else:
                            st.caption("🟢 Available")
                    
                    with col3:
                        st.caption(f"ID: {course_id}")
                    
                    with col4:
                        if is_enrolled:
                            st.button("✅ Enrolled", key=f"enrolled_{course_id}", disabled=True, use_container_width=True)
                        else:
                            if st.button("➕ Add", key=f"add_{course_id}", use_container_width=True):
                                # Add course functionality
                                enrollment_hash = st.session_state.get('enrollment_hash', '')
                                
                                if not enrollment_hash:
                                    show_warning("Please set enrollment hash first! (Check network tab or ask admin)")
                                    # Add input for hash
                                    with st.expander("⚙️ Set Enrollment Hash"):
                                        hash_input = st.text_input("Enrollment Hash", placeholder="05d8af8b7a6a9b1a1a16be2841ec0152c8e6ec31")
                                        if st.button("Save Hash"):
                                            st.session_state['enrollment_hash'] = hash_input
                                            show_success("Hash saved!")
                                            st.rerun()
                                else:
                                    with st.spinner(f"Adding {subject_name}..."):
                                        try:
                                            # Create fresh client with stored credentials
                                            add_client = SiramaClient()
                                            add_client.token = st.session_state[f'token_{selected_account_id}']
                                            add_client.student_id = st.session_state[f'student_id_{selected_account_id}']
                                            
                                            # Ensure session exists
                                            if not hasattr(add_client, 'session') or add_client.session is None:
                                                import requests
                                                add_client.session = requests.Session()
                                            
                                            add_result = add_client.add_course(course_id, enrollment_hash)
                                            
                                            if add_result['success']:
                                                # Log to database
                                                st.session_state.supabase.log_enrollment(
                                                    account_id=selected_account_id,
                                                    action='add',
                                                    course_id=course_id,
                                                    course_name=f"{subject_name} ({class_name})",
                                                    status='success',
                                                    message=add_result.get('message', 'Successfully enrolled')
                                                )
                                                show_success(f"✅ Successfully added {subject_name}!")
                                                
                                                # Refresh enrolled courses
                                                enrolled_result = add_client.get_enrolled_courses()
                                                if enrolled_result['success']:
                                                    st.session_state[f'enrolled_{selected_account_id}'] = enrolled_result.get('courses', [])
                                                
                                                st.rerun()
                                            else:
                                                # Log failure
                                                st.session_state.supabase.log_enrollment(
                                                    account_id=selected_account_id,
                                                    action='add',
                                                    course_id=course_id,
                                                    course_name=f"{subject_name} ({class_name})",
                                                    status='failed',
                                                    message=add_result.get('message', 'Failed to enroll')
                                                )
                                                show_error(f"Failed: {add_result.get('message')}")
                                        except Exception as e:
                                            show_error(f"Error: {str(e)}")
                    
                    st.markdown("---")
        
        else:
            st.info("👆 Click 'Fetch Available' to see courses you can enroll in")
        
        # Enrollment hash settings
        st.markdown("---")
        with st.expander("⚙️ Enrollment Settings"):
            # Set default hash if not exists
            if 'enrollment_hash' not in st.session_state:
                st.session_state['enrollment_hash'] = '20f11ee4d4672f5dbf3b219c96b33c50f630819b'
            
            current_hash = st.session_state.get('enrollment_hash', '')
            st.write("**Current Hash:**", current_hash if current_hash else "Not set")
            
            new_hash = st.text_input("Update Enrollment Hash", placeholder="20f11ee4d4672f5dbf3b219c96b33c50f630819b", value=current_hash)
            if st.button("💾 Save Hash"):
                st.session_state['enrollment_hash'] = new_hash
                show_success("Hash saved successfully!")
                st.rerun()
            
            st.caption("💡 Tip: Default hash is set to 20f11ee4d4672f5dbf3b219c96b33c50f630819b (from HAR file)")
            st.caption("⚠️ Hash may change per semester/period. Check DevTools > Network if enrollment fails.")

st.markdown("---")
st.caption("💡 Tip: Login → Refresh Enrolled → Browse Available → Add courses!")
