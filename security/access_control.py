"""
Access Control System for Data Governance
Implements role-based access control (RBAC) for data assets and operations.
"""

import json
import hashlib
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """System permissions."""
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    MANAGE_SCHEMA = "manage_schema"
    VIEW_PII = "view_pii"
    EXPORT_DATA = "export_data"
    MANAGE_USERS = "manage_users"
    VIEW_LINEAGE = "view_lineage"
    RUN_QUALITY_CHECKS = "run_quality_checks"
    VIEW_AUDIT_LOGS = "view_audit_logs"


class DataClassification(str, Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class Role:
    """User role definition."""
    name: str
    description: str
    permissions: Set[Permission]
    data_access_levels: Set[DataClassification]
    can_view_pii: bool = False
    max_export_rows: int = 10000
    session_timeout_minutes: int = 480  # 8 hours


@dataclass
class User:
    """User definition."""
    user_id: str
    username: str
    email: str
    full_name: str
    roles: Set[str]
    department: str
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None


@dataclass
class AccessRequest:
    """Access request for audit logging."""
    request_id: str
    user_id: str
    resource: str
    action: str
    timestamp: datetime
    granted: bool
    reason: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AccessControlManager:
    """Manages access control for data governance system."""
    
    def __init__(self):
        self.roles = self._initialize_roles()
        self.users: Dict[str, User] = {}
        self.access_log: List[AccessRequest] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    def _initialize_roles(self) -> Dict[str, Role]:
        """Initialize default roles."""
        
        return {
            "data_engineer": Role(
                name="data_engineer",
                description="Data engineers with full technical access",
                permissions={
                    Permission.READ_DATA,
                    Permission.WRITE_DATA,
                    Permission.MANAGE_SCHEMA,
                    Permission.VIEW_PII,
                    Permission.EXPORT_DATA,
                    Permission.VIEW_LINEAGE,
                    Permission.RUN_QUALITY_CHECKS,
                    Permission.VIEW_AUDIT_LOGS
                },
                data_access_levels={
                    DataClassification.PUBLIC,
                    DataClassification.INTERNAL,
                    DataClassification.CONFIDENTIAL
                },
                can_view_pii=True,
                max_export_rows=1000000
            ),
            
            "data_analyst": Role(
                name="data_analyst",
                description="Data analysts with read access to business data",
                permissions={
                    Permission.READ_DATA,
                    Permission.EXPORT_DATA,
                    Permission.VIEW_LINEAGE,
                    Permission.RUN_QUALITY_CHECKS
                },
                data_access_levels={
                    DataClassification.PUBLIC,
                    DataClassification.INTERNAL
                },
                can_view_pii=False,
                max_export_rows=100000
            ),
            
            "business_user": Role(
                name="business_user",
                description="Business users with limited read access",
                permissions={
                    Permission.READ_DATA,
                    Permission.EXPORT_DATA
                },
                data_access_levels={
                    DataClassification.PUBLIC,
                    DataClassification.INTERNAL
                },
                can_view_pii=False,
                max_export_rows=10000
            ),
            
            "auditor": Role(
                name="auditor",
                description="Auditors with read-only access to all data and logs",
                permissions={
                    Permission.READ_DATA,
                    Permission.VIEW_PII,
                    Permission.VIEW_LINEAGE,
                    Permission.VIEW_AUDIT_LOGS
                },
                data_access_levels={
                    DataClassification.PUBLIC,
                    DataClassification.INTERNAL,
                    DataClassification.CONFIDENTIAL,
                    DataClassification.RESTRICTED
                },
                can_view_pii=True,
                max_export_rows=50000
            ),
            
            "dpo": Role(
                name="dpo",
                description="Data Protection Officer with privacy management access",
                permissions={
                    Permission.READ_DATA,
                    Permission.VIEW_PII,
                    Permission.VIEW_LINEAGE,
                    Permission.VIEW_AUDIT_LOGS,
                    Permission.MANAGE_USERS
                },
                data_access_levels={
                    DataClassification.PUBLIC,
                    DataClassification.INTERNAL,
                    DataClassification.CONFIDENTIAL,
                    DataClassification.RESTRICTED
                },
                can_view_pii=True,
                max_export_rows=100000
            ),
            
            "admin": Role(
                name="admin",
                description="System administrators with full access",
                permissions=set(Permission),
                data_access_levels=set(DataClassification),
                can_view_pii=True,
                max_export_rows=float('inf')
            )
        }
    
    def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        roles: List[str],
        department: str,
        password: Optional[str] = None
    ) -> str:
        """Create a new user."""
        
        user_id = f"user_{hashlib.md5(username.encode()).hexdigest()[:8]}"
        
        invalid_roles = set(roles) - set(self.roles.keys())
        if invalid_roles:
            raise ValueError(f"Invalid roles: {invalid_roles}")
        
        password_hash = None
        if password:
            password_hash = hashlib.sha256(f"{password}salt".encode()).hexdigest()
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            full_name=full_name,
            roles=set(roles),
            department=department,
            created_at=datetime.utcnow(),
            password_hash=password_hash
        )
        
        self.users[user_id] = user
        
        logger.info(f"Created user: {username} ({user_id}) with roles: {roles}")
        
        return user_id
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return user_id if successful."""
        
        for user in self.users.values():
            if user.username == username and user.is_active:
                if user.password_hash:
                    expected_hash = hashlib.sha256(f"{password}salt".encode()).hexdigest()
                    if user.password_hash == expected_hash:
                        user.last_login = datetime.utcnow()
                        return user.user_id
        
        return None
    
    def create_session(self, user_id: str, ip_address: str = None) -> str:
        """Create user session."""
        
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        session_id = hashlib.md5(f"{user_id}{datetime.utcnow()}".encode()).hexdigest()
        
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "ip_address": ip_address,
            "last_activity": datetime.utcnow()
        }
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[str]:
        """Validate session and return user_id if valid."""
        
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        user_id = session["user_id"]
        
        if user_id not in self.users:
            del self.active_sessions[session_id]
            return None
        
        user = self.users[user_id]
        if not user.is_active:
            del self.active_sessions[session_id]
            return None
        
        user_roles = [self.roles[role] for role in user.roles if role in self.roles]
        max_timeout = min(role.session_timeout_minutes for role in user_roles) if user_roles else 480
        
        if (datetime.utcnow() - session["last_activity"]).total_seconds() > max_timeout * 60:
            del self.active_sessions[session_id]
            return None
        
        session["last_activity"] = datetime.utcnow()
        
        return user_id
    
    def check_permission(
        self,
        user_id: str,
        permission: Permission,
        resource: str = None,
        data_classification: DataClassification = DataClassification.INTERNAL
    ) -> bool:
        """Check if user has specific permission."""
        
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        if not user.is_active:
            return False
        
        user_permissions = set()
        user_data_levels = set()
        
        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                user_permissions.update(role.permissions)
                user_data_levels.update(role.data_access_levels)
        
        has_permission = permission in user_permissions
        
        has_data_access = data_classification in user_data_levels
        
        return has_permission and has_data_access
    
    def log_access_request(
        self,
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        reason: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> str:
        """Log access request for audit trail."""
        
        request_id = f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
        
        access_request = AccessRequest(
            request_id=request_id,
            user_id=user_id,
            resource=resource,
            action=action,
            timestamp=datetime.utcnow(),
            granted=granted,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.access_log.append(access_request)
        
        return request_id
    
    def authorize_data_access(
        self,
        user_id: str,
        dataset_name: str,
        action: str,
        data_classification: DataClassification = DataClassification.INTERNAL,
        row_count: int = 0,
        session_id: str = None
    ) -> Dict[str, Any]:
        """Comprehensive authorization check for data access."""
        
        if session_id:
            session_user_id = self.validate_session(session_id)
            if not session_user_id or session_user_id != user_id:
                result = {
                    "authorized": False,
                    "reason": "Invalid or expired session",
                    "user_id": user_id,
                    "dataset": dataset_name,
                    "action": action
                }
                self.log_access_request(user_id, dataset_name, action, False, result["reason"])
                return result
        
        action_permission_map = {
            "read": Permission.READ_DATA,
            "write": Permission.WRITE_DATA,
            "delete": Permission.DELETE_DATA,
            "export": Permission.EXPORT_DATA,
            "view_lineage": Permission.VIEW_LINEAGE
        }
        
        required_permission = action_permission_map.get(action)
        if not required_permission:
            result = {
                "authorized": False,
                "reason": f"Unknown action: {action}",
                "user_id": user_id,
                "dataset": dataset_name,
                "action": action
            }
            self.log_access_request(user_id, dataset_name, action, False, result["reason"])
            return result
        
        has_permission = self.check_permission(user_id, required_permission, dataset_name, data_classification)
        
        if not has_permission:
            result = {
                "authorized": False,
                "reason": f"Insufficient permissions for {action} on {data_classification.value} data",
                "user_id": user_id,
                "dataset": dataset_name,
                "action": action
            }
            self.log_access_request(user_id, dataset_name, action, False, result["reason"])
            return result
        
        if action == "export" and row_count > 0:
            user = self.users[user_id]
            max_rows = min(
                self.roles[role].max_export_rows 
                for role in user.roles 
                if role in self.roles
            )
            
            if row_count > max_rows:
                result = {
                    "authorized": False,
                    "reason": f"Export row limit exceeded: {row_count} > {max_rows}",
                    "user_id": user_id,
                    "dataset": dataset_name,
                    "action": action,
                    "max_allowed_rows": max_rows
                }
                self.log_access_request(user_id, dataset_name, action, False, result["reason"])
                return result
        
        result = {
            "authorized": True,
            "user_id": user_id,
            "dataset": dataset_name,
            "action": action,
            "data_classification": data_classification.value,
            "authorized_at": datetime.utcnow().isoformat()
        }
        
        self.log_access_request(user_id, dataset_name, action, True)
        
        return result
    
    def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user permissions."""
        
        if user_id not in self.users:
            return {"error": "User not found"}
        
        user = self.users[user_id]
        
        all_permissions = set()
        all_data_levels = set()
        max_export_rows = 0
        min_session_timeout = float('inf')
        
        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                all_permissions.update(role.permissions)
                all_data_levels.update(role.data_access_levels)
                max_export_rows = max(max_export_rows, role.max_export_rows)
                min_session_timeout = min(min_session_timeout, role.session_timeout_minutes)
        
        return {
            "user_id": user_id,
            "username": user.username,
            "roles": list(user.roles),
            "permissions": [p.value for p in all_permissions],
            "data_access_levels": [d.value for d in all_data_levels],
            "can_view_pii": any(
                self.roles[role].can_view_pii 
                for role in user.roles 
                if role in self.roles
            ),
            "max_export_rows": max_export_rows,
            "session_timeout_minutes": min_session_timeout if min_session_timeout != float('inf') else 480,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    
    def get_access_audit_report(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Generate access audit report."""
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        filtered_log = [
            req for req in self.access_log
            if start_date <= req.timestamp <= end_date
            and (not user_id or req.user_id == user_id)
        ]
        
        total_requests = len(filtered_log)
        granted_requests = sum(1 for req in filtered_log if req.granted)
        denied_requests = total_requests - granted_requests
        
        user_stats = {}
        for req in filtered_log:
            if req.user_id not in user_stats:
                user_stats[req.user_id] = {
                    "total": 0,
                    "granted": 0,
                    "denied": 0,
                    "resources": set()
                }
            
            user_stats[req.user_id]["total"] += 1
            if req.granted:
                user_stats[req.user_id]["granted"] += 1
            else:
                user_stats[req.user_id]["denied"] += 1
            user_stats[req.user_id]["resources"].add(req.resource)
        
        for stats in user_stats.values():
            stats["resources"] = list(stats["resources"])
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_requests": total_requests,
                "granted_requests": granted_requests,
                "denied_requests": denied_requests,
                "success_rate": (granted_requests / total_requests * 100) if total_requests > 0 else 0
            },
            "user_statistics": user_stats,
            "recent_denied_requests": [
                {
                    "user_id": req.user_id,
                    "resource": req.resource,
                    "action": req.action,
                    "reason": req.reason,
                    "timestamp": req.timestamp.isoformat()
                }
                for req in filtered_log[-10:] if not req.granted
            ],
            "generated_at": datetime.utcnow().isoformat()
        }


access_control = AccessControlManager()


def get_access_control() -> AccessControlManager:
    """Get global access control manager instance."""
    return access_control
