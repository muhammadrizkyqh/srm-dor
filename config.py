"""
Configuration module for SIRAMA Auto-KRS Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to use Streamlit secrets first (for Streamlit Cloud), fallback to .env
try:
    import streamlit as st
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
    ENCRYPTION_KEY = st.secrets.get("ENCRYPTION_KEY", os.getenv("ENCRYPTION_KEY"))
except:
    # Fallback to environment variables (for local development)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# App Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# SIRAMA API Endpoints (dari HAR file)
SIRAMA_AUTH_URL = "https://auth-v2.telkomuniversity.ac.id"
SIRAMA_SERVICE_URL = "https://service-v2.telkomuniversity.ac.id"

# API Endpoints
ENDPOINTS = {
    "login": f"{SIRAMA_AUTH_URL}/api/oauth/issueauth",
    "scope": f"{SIRAMA_AUTH_URL}/api/oauth/issuescope",
    "profile": f"{SIRAMA_SERVICE_URL}/read/api/read/issueprofile",
    "student_status": f"{SIRAMA_SERVICE_URL}/filter/api/read/d5766829095ade253c73f309124ec702n2132344",
    "academic_year": f"{SIRAMA_SERVICE_URL}/course-schedule/academic/current-school-year",
    "registration_schedule": f"{SIRAMA_SERVICE_URL}/course-schedule/course/registration-schedule",
    "available_courses": f"{SIRAMA_SERVICE_URL}/read/api/read/d6c09f330d8af5c7d63f64d2c251498fbdfed81d/{{study_program_id}}/{{semester}}",
    "enrolled_courses": f"{SIRAMA_SERVICE_URL}/read/api/read/87ec6ce42c5f860413f696957c33d9f3ee70acf2/",
    "add_course": f"{SIRAMA_SERVICE_URL}/trans/api/transaction/{{hash}}",
    "drop_course": f"{SIRAMA_SERVICE_URL}/trans/api/transaction/{{hash}}/{{course_id}}/{{student_id}}/{{flag}}",
}

# HTTP Headers Template
DEFAULT_HEADERS = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "id",
    "origin": "https://sirama.telkomuniversity.ac.id",
    "referer": "https://sirama.telkomuniversity.ac.id/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}
