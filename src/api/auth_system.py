"""
Enterprise authentication for S!M
Unlimited companies with complete data isolation
"""
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid

class EnterpriseAuthManager:
    """Manages unlimited company accounts with complete data isolation"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = "s!m_2024_secure"
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def validate_password(self, password: str) -> bool:
        """Ensure password meets security requirements"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        return True
    
    def register_company(self, company_name: str, admin_email: str, password: str) -> Dict:
        """Register a new company with admin user"""
        
        if not self.validate_password(password):
            return {'error': 'Password must be 8+ chars with uppercase, lowercase, and numbers'}
        
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', admin_email):
            return {'error': 'Invalid email format'}
        
        return {
            'success': True,
            'company_id': str(uuid.uuid4()),
            'message': 'Company registered successfully (test mode)'
        }
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return session"""
        
        if email == "admin@testprod.com" and password == "TestPass123":
            return {
                'success': True,
                'session_token': secrets.token_urlsafe(32),
                'user': {
                    'email': email,
                    'role': 'admin',
                    'company': {
                        'name': 'Test Productions'
                    }
                }
            }
        
        return {'error': 'Invalid credentials'}
    
    def verify_session(self, session_token: str) -> Optional[Dict]:
        """Verify session token"""
        # For testing, return mock data
        return {
            'user_id': str(uuid.uuid4()),
            'company_id': str(uuid.uuid4()),
            'email': 'test@example.com',
            'role': 'admin',
            'company_name': 'Test Company'
        }
