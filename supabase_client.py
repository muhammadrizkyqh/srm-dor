"""
Supabase Client & Database Operations
Handles all Supabase interactions for accounts, courses, and logs
"""
from supabase import create_client, Client
from cryptography.fernet import Fernet
from typing import Dict, List, Optional, Any
from datetime import datetime
from config import SUPABASE_URL, SUPABASE_KEY, ENCRYPTION_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase database operations"""
    
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        if not ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY must be set in environment variables")
        
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.cipher = Fernet(ENCRYPTION_KEY.encode())
    
    # =============== AUTHENTICATION ===============
    
    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """Register new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            logger.info(f"User registered: {email}")
            return {"success": True, "user": response.user}
        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            logger.info(f"User logged in: {email}")
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def sign_out(self) -> Dict[str, Any]:
        """Logout user"""
        try:
            self.client.auth.sign_out()
            logger.info("User signed out")
            return {"success": True}
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_session(self) -> Optional[Any]:
        """Get current session"""
        try:
            session = self.client.auth.get_session()
            return session
        except Exception as e:
            logger.error(f"Get session error: {str(e)}")
            return None
    
    # =============== ENCRYPTION ===============
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt password"""
        return self.cipher.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt password"""
        return self.cipher.decrypt(encrypted_password.encode()).decode()
    
    # =============== ACCOUNT MANAGEMENT ===============
    
    def create_account(self, user_id: str, nim: str, password: str, name: str = None) -> Dict[str, Any]:
        """
        Create new SIRAMA account
        
        Args:
            user_id: Supabase auth user ID
            nim: Student NIM
            password: SIRAMA password (will be encrypted)
            name: Student name
            
        Returns:
            Dict with success status and account data
        """
        try:
            encrypted_password = self.encrypt_password(password)
            
            data = {
                "user_id": user_id,
                "nim": nim,
                "password_encrypted": encrypted_password,
                "name": name,
                "status": "active"
            }
            
            response = self.client.table("accounts").insert(data).execute()
            logger.info(f"Account created for NIM: {nim}")
            
            return {
                "success": True,
                "account": response.data[0] if response.data else None
            }
        except Exception as e:
            logger.error(f"Create account error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all accounts for a user"""
        try:
            response = self.client.table("accounts").select("*").eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Get accounts error: {str(e)}")
            return []
    
    def get_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account by ID"""
        try:
            response = self.client.table("accounts").select("*").eq("id", account_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Get account error: {str(e)}")
            return None
    
    def update_account(self, account_id: str, **kwargs) -> Dict[str, Any]:
        """Update account fields"""
        try:
            # Encrypt password if provided
            if "password" in kwargs:
                kwargs["password_encrypted"] = self.encrypt_password(kwargs.pop("password"))
            
            kwargs["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table("accounts").update(kwargs).eq("id", account_id).execute()
            logger.info(f"Account updated: {account_id}")
            
            return {
                "success": True,
                "account": response.data[0] if response.data else None
            }
        except Exception as e:
            logger.error(f"Update account error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def delete_account(self, account_id: str) -> Dict[str, Any]:
        """Delete account"""
        try:
            self.client.table("accounts").delete().eq("id", account_id).execute()
            logger.info(f"Account deleted: {account_id}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Delete account error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    # =============== ENROLLMENT LOGS ===============
    
    def log_enrollment(self, account_id: str, action: str, course_id: str, 
                       course_name: str, status: str, message: str) -> Dict[str, Any]:
        """Log enrollment action"""
        try:
            data = {
                "account_id": account_id,
                "action": action,  # 'add' or 'drop'
                "course_id": course_id,
                "course_name": course_name,
                "status": status,  # 'success' or 'failed'
                "message": message
            }
            
            response = self.client.table("enrollment_logs").insert(data).execute()
            logger.info(f"Enrollment logged: {action} {course_name} - {status}")
            
            return {
                "success": True,
                "log": response.data[0] if response.data else None
            }
        except Exception as e:
            logger.error(f"Log enrollment error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_enrollment_logs(self, account_id: str = None, limit: int = 100, 
                           status_filter: str = None) -> List[Dict[str, Any]]:
        """
        Get enrollment logs
        
        Args:
            account_id: Filter by account (optional)
            limit: Maximum number of logs to return
            status_filter: Filter by status (optional)
            
        Returns:
            List of enrollment logs
        """
        try:
            query = self.client.table("enrollment_logs").select("*")
            
            if account_id:
                query = query.eq("account_id", account_id)
            
            if status_filter:
                query = query.eq("status", status_filter)
            
            response = query.order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Get enrollment logs error: {str(e)}")
            return []
    
    def get_enrollment_stats(self, account_id: str) -> Dict[str, int]:
        """Get enrollment statistics for an account"""
        try:
            logs = self.get_enrollment_logs(account_id=account_id, limit=1000)
            
            stats = {
                "total": len(logs),
                "success": len([l for l in logs if l["status"] == "success"]),
                "failed": len([l for l in logs if l["status"] == "failed"]),
                "add_actions": len([l for l in logs if l["action"] == "add"]),
                "drop_actions": len([l for l in logs if l["action"] == "drop"])
            }
            
            return stats
        except Exception as e:
            logger.error(f"Get enrollment stats error: {str(e)}")
            return {"total": 0, "success": 0, "failed": 0, "add_actions": 0, "drop_actions": 0}
