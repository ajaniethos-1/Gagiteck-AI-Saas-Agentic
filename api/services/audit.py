"""Audit logging service for SOC2 compliance."""

import json
import logging
from datetime import datetime
from typing import Optional, Any
from enum import Enum
from pydantic import BaseModel

from api.config import settings

logger = logging.getLogger("audit")


class AuditEventType(str, Enum):
    """Types of audit events."""
    # Authentication events
    USER_LOGIN = "user.login"
    USER_LOGIN_FAILED = "user.login_failed"
    USER_LOGOUT = "user.logout"
    USER_SIGNUP = "user.signup"
    PASSWORD_CHANGE = "user.password_change"
    PASSWORD_RESET_REQUEST = "user.password_reset_request"
    ACCOUNT_LOCKED = "user.account_locked"
    ACCOUNT_UNLOCKED = "user.account_unlocked"

    # API Key events
    API_KEY_CREATED = "api_key.created"
    API_KEY_DELETED = "api_key.deleted"
    API_KEY_USED = "api_key.used"

    # Resource events
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    AGENT_DELETED = "agent.deleted"
    AGENT_EXECUTED = "agent.executed"

    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_UPDATED = "workflow.updated"
    WORKFLOW_DELETED = "workflow.deleted"
    WORKFLOW_TRIGGERED = "workflow.triggered"

    # Access control events
    ROLE_CREATED = "role.created"
    ROLE_UPDATED = "role.updated"
    ROLE_DELETED = "role.deleted"
    TEAM_MEMBER_INVITED = "team.member_invited"
    TEAM_MEMBER_REMOVED = "team.member_removed"
    TEAM_MEMBER_ROLE_CHANGED = "team.member_role_changed"

    # Security events
    PERMISSION_DENIED = "security.permission_denied"
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"

    # Configuration events
    SETTINGS_UPDATED = "settings.updated"
    WEBHOOK_CREATED = "webhook.created"
    WEBHOOK_UPDATED = "webhook.updated"
    WEBHOOK_DELETED = "webhook.deleted"


class AuditEvent(BaseModel):
    """Audit event model."""
    timestamp: datetime
    event_type: AuditEventType
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    status: str = "success"  # success, failure
    details: Optional[dict] = None
    request_id: Optional[str] = None


class AuditLogger:
    """
    Audit logging service for tracking security-relevant events.

    SOC2 Requirements:
    - CC7.2: System monitoring and anomaly detection
    - CC6.1: Logical access security
    - CC7.1: System availability monitoring
    """

    def __init__(self):
        self.enabled = settings.AUDIT_LOG_ENABLED
        self._setup_logger()

    def _setup_logger(self):
        """Configure the audit logger with proper formatting."""
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": %(message)s}'
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def log(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        status: str = "success",
        details: Optional[dict] = None,
        request_id: Optional[str] = None,
    ) -> AuditEvent:
        """
        Log an audit event.

        Args:
            event_type: Type of event from AuditEventType enum
            user_id: ID of the user performing the action
            user_email: Email of the user
            ip_address: Client IP address
            user_agent: Client user agent string
            resource_type: Type of resource being accessed (agent, workflow, etc.)
            resource_id: ID of the resource
            action: Specific action taken (create, update, delete, etc.)
            status: success or failure
            details: Additional event details
            request_id: Correlation ID for request tracing

        Returns:
            AuditEvent: The logged event
        """
        if not self.enabled:
            return None

        event = AuditEvent(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status=status,
            details=details,
            request_id=request_id,
        )

        # Log to structured logging
        log_data = event.model_dump()
        log_data["timestamp"] = event.timestamp.isoformat()
        log_data["event_type"] = event.event_type.value

        if status == "failure":
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

        return event

    # Convenience methods for common events

    def log_login(
        self,
        user_id: str,
        user_email: str,
        ip_address: str,
        user_agent: str,
        success: bool = True,
        failure_reason: Optional[str] = None,
    ):
        """Log a login attempt."""
        return self.log(
            event_type=AuditEventType.USER_LOGIN if success else AuditEventType.USER_LOGIN_FAILED,
            user_id=user_id if success else None,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if success else "failure",
            details={"reason": failure_reason} if failure_reason else None,
        )

    def log_logout(self, user_id: str, user_email: str, ip_address: str):
        """Log a logout event."""
        return self.log(
            event_type=AuditEventType.USER_LOGOUT,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
        )

    def log_signup(self, user_id: str, user_email: str, ip_address: str):
        """Log a new user signup."""
        return self.log(
            event_type=AuditEventType.USER_SIGNUP,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
        )

    def log_password_change(self, user_id: str, user_email: str, ip_address: str):
        """Log a password change."""
        return self.log(
            event_type=AuditEventType.PASSWORD_CHANGE,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
        )

    def log_account_locked(
        self,
        user_email: str,
        ip_address: str,
        failed_attempts: int,
    ):
        """Log an account lockout."""
        return self.log(
            event_type=AuditEventType.ACCOUNT_LOCKED,
            user_email=user_email,
            ip_address=ip_address,
            status="failure",
            details={"failed_attempts": failed_attempts},
        )

    def log_api_key_created(
        self,
        user_id: str,
        user_email: str,
        key_id: str,
        key_name: str,
        ip_address: str,
    ):
        """Log API key creation."""
        return self.log(
            event_type=AuditEventType.API_KEY_CREATED,
            user_id=user_id,
            user_email=user_email,
            resource_type="api_key",
            resource_id=key_id,
            ip_address=ip_address,
            details={"key_name": key_name},
        )

    def log_api_key_deleted(
        self,
        user_id: str,
        user_email: str,
        key_id: str,
        ip_address: str,
    ):
        """Log API key deletion."""
        return self.log(
            event_type=AuditEventType.API_KEY_DELETED,
            user_id=user_id,
            user_email=user_email,
            resource_type="api_key",
            resource_id=key_id,
            ip_address=ip_address,
        )

    def log_resource_action(
        self,
        event_type: AuditEventType,
        user_id: str,
        user_email: str,
        resource_type: str,
        resource_id: str,
        ip_address: str,
        details: Optional[dict] = None,
    ):
        """Log a resource action (create, update, delete)."""
        return self.log(
            event_type=event_type,
            user_id=user_id,
            user_email=user_email,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details,
        )

    def log_permission_denied(
        self,
        user_id: str,
        user_email: str,
        resource_type: str,
        resource_id: str,
        action: str,
        ip_address: str,
    ):
        """Log a permission denied event."""
        return self.log(
            event_type=AuditEventType.PERMISSION_DENIED,
            user_id=user_id,
            user_email=user_email,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            ip_address=ip_address,
            status="failure",
        )


# Global audit logger instance
audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get the audit logger instance."""
    return audit_logger
