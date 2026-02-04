"""
SIRAMA API Client
Handles all interactions with SIRAMA authentication and service endpoints
"""
import requests
from typing import Dict, Optional, Any
from config import ENDPOINTS, DEFAULT_HEADERS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SiramaClient:
    """Client for SIRAMA API interactions"""
    
    def __init__(self):
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.student_id: Optional[str] = None
        
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login to SIRAMA and get access token
        
        Args:
            username: Username SIRAMA (email tanpa @telkomuniversity.ac.id atau NIM)
            password: Password SIRAMA
            
        Returns:
            Dict containing login response with access_token
            
        Raises:
            Exception: If login fails
        """
        try:
            logger.info(f"Attempting login for username: {username}")
            
            # Add accept-language header for Indonesian locale
            headers = DEFAULT_HEADERS.copy()
            headers['accept-language'] = 'id'
            
            # Prepare login request (dari HAR line 20446)
            response = self.session.post(
                ENDPOINTS["login"],
                headers=headers,
                data={
                    "username": username,
                    "password": password
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Log response for debugging
            logger.info(f"Login response: {data}")
            
            # Store token for subsequent requests
            # Response format: {"meta": {"status": 200, "message": "success"}, "token": "...", "expires": ...}
            if "token" in data and data.get("meta", {}).get("status") == 200:
                self.token = data["token"]
                logger.info(f"Login successful for username: {username}")
                return {
                    "success": True,
                    "access_token": data["token"],
                    "token_type": "Bearer",
                    "expires_in": data.get("expires")
                }
            elif "access_token" in data:
                # Fallback for old format
                self.token = data["access_token"]
                logger.info(f"Login successful for username: {username}")
                return {
                    "success": True,
                    "access_token": data["access_token"],
                    "token_type": data.get("token_type", "Bearer"),
                    "expires_in": data.get("expires_in")
                }
            else:
                error_msg = data.get("meta", {}).get("message", "Invalid response from server")
                logger.error(f"Login failed: {error_msg}. Response: {data}")
                return {
                    "success": False,
                    "message": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Login error: {str(e)}")
            return {
                "success": False,
                "message": f"Login failed: {str(e)}"
            }
    
    def get_scope(self) -> Dict[str, Any]:
        """
        Get user scopes/permissions
        
        Returns:
            Dict containing user scopes
        """
        if not self.token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(
                ENDPOINTS["scope"],
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Scopes retrieved: {data.get('scope', [])}")
            return {
                "success": True,
                "scopes": data.get("scope", [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get scope error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Get student profile information
        
        Returns:
            Dict containing student profile data
        """
        if not self.token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(
                ENDPOINTS["profile"],
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Store student_id for future use (field name is 'numberid' in API)
            if "numberid" in data:
                self.student_id = data["numberid"]
            
            logger.info(f"Profile retrieved for: {data.get('fullname', 'Unknown')}")
            return {
                "success": True,
                "profile": data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get profile error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_student_status(self) -> Dict[str, Any]:
        """
        Get student status (Active/Graduated)
        
        Returns:
            Dict containing student status
        """
        if not self.token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(
                ENDPOINTS["student_status"],
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Student status: {data.get('status', 'Unknown')}")
            return {
                "success": True,
                "status": data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get student status error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_available_courses(self, study_program_id: int = 117, semester: int = 2) -> Dict[str, Any]:
        """
        Get list of available courses for registration
        
        Args:
            study_program_id: Program studi ID (default: 117 for IS)
            semester: Semester number (default: 2)
            
        Returns:
            Dict containing list of available courses
        """
        if not self.token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            url = ENDPOINTS["available_courses"].format(
                study_program_id=study_program_id,
                semester=semester
            )
            
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            logger.info(f"Fetching available courses for program {study_program_id}, semester {semester}")
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            courses = response.json()
            
            logger.info(f"Retrieved {len(courses)} available courses")
            return {
                "success": True,
                "courses": courses,
                "count": len(courses)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get available courses error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_enrolled_courses(self) -> Dict[str, Any]:
        """
        Get list of currently enrolled courses (course selected)
        
        Returns:
            Dict containing list of enrolled courses
        """
        if not self.token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            # No student_id needed - uses token for authentication
            url = ENDPOINTS["enrolled_courses"]
            
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            logger.info(f"Fetching enrolled courses")
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Response is a direct array of enrolled courses
            if isinstance(response_data, list):
                courses = response_data
            else:
                logger.warning(f"Unexpected response type: {type(response_data)}, value: {response_data}")
                courses = []
            
            logger.info(f"Retrieved {len(courses)} enrolled courses")
            return {
                "success": True,
                "courses": courses,
                "count": len(courses)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get enrolled courses error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def add_course(self, course_id: str, enrollment_hash: str) -> Dict[str, Any]:
        """
        Add/enroll a course
        
        Args:
            course_id: ID of the course to enroll
            enrollment_hash: Hash identifier for the transaction
            
        Returns:
            Dict containing enrollment result
        """
        if not self.token or not self.student_id:
            return {"success": False, "message": "Not authenticated or missing student_id"}
        
        try:
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Endpoint dengan hash (dari HAR line 169130)
            url = ENDPOINTS["add_course"].format(hash=enrollment_hash)
            
            # Data dalam format multipart/form-data
            data = {
                "studentid": self.student_id,
                "courseid": course_id
            }
            
            logger.info(f"Adding course {course_id} for student {self.student_id}")
            
            response = self.session.post(
                url,
                headers=headers,
                data=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "Success":
                logger.info(f"Course {course_id} added successfully")
                return {
                    "success": True,
                    "message": result.get("message", "Success record registration"),
                    "data": result
                }
            else:
                logger.warning(f"Failed to add course {course_id}: {result.get('message')}")
                return {
                    "success": False,
                    "message": result.get("message", "Failed to add course"),
                    "data": result
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Add course error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def drop_course(self, course_schedule_id: str, drop_hash: str, flag: str = "1") -> Dict[str, Any]:
        """
        Drop/remove an enrolled course
        
        Args:
            course_schedule_id: ID of the course schedule to drop
            drop_hash: Hash identifier for the transaction
            flag: Flag parameter (default "1")
            
        Returns:
            Dict containing drop result
        """
        if not self.token or not self.student_id:
            return {"success": False, "message": "Not authenticated or missing student_id"}
        
        try:
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            # Endpoint dengan parameters (dari HAR line 172720)
            url = ENDPOINTS["drop_course"].format(
                hash=drop_hash,
                course_id=course_schedule_id,
                student_id=self.student_id,
                flag=flag
            )
            
            logger.info(f"Dropping course {course_schedule_id} for student {self.student_id}")
            
            response = self.session.delete(
                url,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "Success":
                logger.info(f"Course {course_schedule_id} dropped successfully")
                return {
                    "success": True,
                    "message": result.get("message", "Berhasil menghapus data registration"),
                    "data": result
                }
            else:
                logger.warning(f"Failed to drop course {course_schedule_id}: {result.get('message')}")
                return {
                    "success": False,
                    "message": result.get("message", "Failed to drop course"),
                    "data": result
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Drop course error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_academic_year(self) -> Dict[str, Any]:
        """
        Get current academic year information
        
        Returns:
            Dict containing academic year data
        """
        if not self.token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(
                ENDPOINTS["academic_year"],
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Academic year retrieved: {data}")
            return {
                "success": True,
                "data": data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get academic year error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_registration_schedule(self) -> Dict[str, Any]:
        """
        Get course registration schedule
        
        Returns:
            Dict containing registration schedule
        """
        if not self.token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(
                ENDPOINTS["registration_schedule"],
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Registration schedule retrieved")
            return {
                "success": True,
                "data": data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get registration schedule error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_schedule(self) -> Dict[str, Any]:
        """
        Get student's course schedule (timetable)
        
        Returns:
            Dict containing schedule data organized by shifts and days
        """
        if not self.token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            headers = {
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {self.token}"
            }
            
            # Endpoint untuk schedule (dari API call user)
            schedule_hash = "cd3ba337b4dbea0b0976f40e77cad6d5ab264b2e"
            url = f"https://service-v2.telkomuniversity.ac.id/read/api/read/{schedule_hash}/"
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Schedule retrieved: {len(data)} time slots")
            return {
                "success": True,
                "schedule": data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get schedule error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def logout(self):
        """Clear session and token"""
        self.token = None
        self.student_id = None
        self.session.close()
        self.session = requests.Session()
        logger.info("Logged out successfully")
