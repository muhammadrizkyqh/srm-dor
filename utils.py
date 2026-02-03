"""
Utility functions and helpers
"""
from datetime import datetime
from typing import Dict, Any
import streamlit as st


def format_datetime(dt_str: str) -> str:
    """Format datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return dt_str


def show_success(message: str):
    """Show success message"""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Show error message"""
    st.error(f"❌ {message}")


def show_info(message: str):
    """Show info message"""
    st.info(f"ℹ️ {message}")


def show_warning(message: str):
    """Show warning message"""
    st.warning(f"⚠️ {message}")


def validate_nim(nim: str) -> bool:
    """Validate NIM format"""
    return nim.isdigit() and len(nim) == 10


def validate_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email


def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    status_emojis = {
        "success": "✅",
        "failed": "❌",
        "active": "🟢",
        "inactive": "⚪",
        "add": "➕",
        "drop": "➖"
    }
    return status_emojis.get(status.lower(), "⚫")


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate long text"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
