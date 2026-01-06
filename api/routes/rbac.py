"""Role-Based Access Control (RBAC) API endpoints."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import uuid

router = APIRouter()


# --- Models ---

class Permission(BaseModel):
    """Permission model."""
    resource: str  # 'agents', 'workflows', 'executions', 'webhooks', 'settings'
    actions: List[str]  # ['create', 'read', 'update', 'delete', 'execute']


class RoleCreate(BaseModel):
    """Request to create a role."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    permissions: List[Permission]


class RoleUpdate(BaseModel):
    """Request to update a role."""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[Permission]] = None


class Role(BaseModel):
    """Role response model."""
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[Permission]
    is_system: bool = False
    created_at: datetime
    updated_at: datetime


class TeamMemberCreate(BaseModel):
    """Request to add team member."""
    email: str
    role_id: str


class TeamMember(BaseModel):
    """Team member response model."""
    id: str
    email: str
    name: Optional[str] = None
    role: Role
    status: str  # 'pending', 'active', 'disabled'
    joined_at: Optional[datetime] = None
    invited_at: datetime


class Team(BaseModel):
    """Team response model."""
    id: str
    name: str
    owner_id: str
    members: List[TeamMember]
    created_at: datetime


# --- Default Roles ---

DEFAULT_ROLES = {
    "admin": {
        "id": "role_admin",
        "name": "Admin",
        "description": "Full access to all resources",
        "permissions": [
            {"resource": "agents", "actions": ["create", "read", "update", "delete", "execute"]},
            {"resource": "workflows", "actions": ["create", "read", "update", "delete", "execute"]},
            {"resource": "executions", "actions": ["read", "cancel"]},
            {"resource": "webhooks", "actions": ["create", "read", "update", "delete"]},
            {"resource": "settings", "actions": ["read", "update"]},
            {"resource": "team", "actions": ["create", "read", "update", "delete"]},
        ],
        "is_system": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    "developer": {
        "id": "role_developer",
        "name": "Developer",
        "description": "Can create and manage agents and workflows",
        "permissions": [
            {"resource": "agents", "actions": ["create", "read", "update", "delete", "execute"]},
            {"resource": "workflows", "actions": ["create", "read", "update", "delete", "execute"]},
            {"resource": "executions", "actions": ["read", "cancel"]},
            {"resource": "webhooks", "actions": ["create", "read", "update", "delete"]},
            {"resource": "settings", "actions": ["read"]},
        ],
        "is_system": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    "viewer": {
        "id": "role_viewer",
        "name": "Viewer",
        "description": "Read-only access to resources",
        "permissions": [
            {"resource": "agents", "actions": ["read"]},
            {"resource": "workflows", "actions": ["read"]},
            {"resource": "executions", "actions": ["read"]},
            {"resource": "webhooks", "actions": ["read"]},
        ],
        "is_system": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    "operator": {
        "id": "role_operator",
        "name": "Operator",
        "description": "Can execute agents and workflows, view results",
        "permissions": [
            {"resource": "agents", "actions": ["read", "execute"]},
            {"resource": "workflows", "actions": ["read", "execute"]},
            {"resource": "executions", "actions": ["read", "cancel"]},
        ],
        "is_system": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
}


# --- In-memory storage ---
_roles_db: dict[str, dict] = {**DEFAULT_ROLES}
_teams_db: dict[str, dict] = {}
_team_members_db: dict[str, dict] = {}


# --- Permission Checker ---

class PermissionChecker:
    """Service for checking permissions."""

    @staticmethod
    def has_permission(role: dict, resource: str, action: str) -> bool:
        """Check if role has permission for action on resource."""
        for perm in role.get('permissions', []):
            if perm['resource'] == resource and action in perm['actions']:
                return True
        return False

    @staticmethod
    def get_user_role(user_id: str) -> Optional[dict]:
        """Get user's role. Returns None if not in a team."""
        for member in _team_members_db.values():
            if member.get('user_id') == user_id:
                role_id = member.get('role_id')
                return _roles_db.get(role_id)
        return None


permission_checker = PermissionChecker()


# --- Role Endpoints ---

@router.get(
    "/roles",
    response_model=List[Role],
    summary="List roles",
    description="Get all available roles.",
)
async def list_roles():
    """List all roles."""
    return [Role(**r) for r in _roles_db.values()]


@router.post(
    "/roles",
    response_model=Role,
    status_code=201,
    summary="Create role",
    description="Create a custom role.",
)
async def create_role(request: RoleCreate):
    """Create a new custom role."""
    role_id = f"role_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    role = {
        "id": role_id,
        "name": request.name,
        "description": request.description,
        "permissions": [p.model_dump() for p in request.permissions],
        "is_system": False,
        "created_at": now,
        "updated_at": now,
    }

    _roles_db[role_id] = role
    return Role(**role)


@router.get(
    "/roles/{role_id}",
    response_model=Role,
    summary="Get role",
    description="Get a specific role by ID.",
)
async def get_role(role_id: str):
    """Get a role by ID."""
    if role_id not in _roles_db:
        raise HTTPException(status_code=404, detail="Role not found")
    return Role(**_roles_db[role_id])


@router.patch(
    "/roles/{role_id}",
    response_model=Role,
    summary="Update role",
    description="Update a custom role.",
)
async def update_role(role_id: str, request: RoleUpdate):
    """Update a custom role."""
    if role_id not in _roles_db:
        raise HTTPException(status_code=404, detail="Role not found")

    role = _roles_db[role_id]

    if role.get('is_system'):
        raise HTTPException(status_code=400, detail="Cannot modify system roles")

    if request.name is not None:
        role['name'] = request.name
    if request.description is not None:
        role['description'] = request.description
    if request.permissions is not None:
        role['permissions'] = [p.model_dump() for p in request.permissions]

    role['updated_at'] = datetime.utcnow()
    return Role(**role)


@router.delete(
    "/roles/{role_id}",
    status_code=204,
    summary="Delete role",
    description="Delete a custom role.",
)
async def delete_role(role_id: str):
    """Delete a custom role."""
    if role_id not in _roles_db:
        raise HTTPException(status_code=404, detail="Role not found")

    role = _roles_db[role_id]
    if role.get('is_system'):
        raise HTTPException(status_code=400, detail="Cannot delete system roles")

    del _roles_db[role_id]


# --- Team Endpoints ---

@router.get(
    "/team",
    summary="Get team",
    description="Get current user's team.",
)
async def get_team():
    """Get team details."""
    # In production, get team based on authenticated user
    if not _teams_db:
        return {"message": "No team configured"}

    team = list(_teams_db.values())[0]
    members = [m for m in _team_members_db.values() if m.get('team_id') == team['id']]

    return {
        "id": team['id'],
        "name": team['name'],
        "owner_id": team['owner_id'],
        "members": [
            {
                "id": m['id'],
                "email": m['email'],
                "name": m.get('name'),
                "role": _roles_db.get(m['role_id'], {}),
                "status": m['status'],
                "invited_at": m['invited_at'],
            }
            for m in members
        ],
        "created_at": team['created_at'],
    }


@router.post(
    "/team/members",
    status_code=201,
    summary="Invite team member",
    description="Invite a new team member.",
)
async def invite_team_member(request: TeamMemberCreate):
    """Invite a new team member."""
    if request.role_id not in _roles_db:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check if already invited
    for member in _team_members_db.values():
        if member.get('email') == request.email:
            raise HTTPException(status_code=400, detail="Email already invited")

    member_id = f"member_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    # Create or get team
    if not _teams_db:
        team_id = f"team_{uuid.uuid4().hex[:12]}"
        _teams_db[team_id] = {
            "id": team_id,
            "name": "Default Team",
            "owner_id": "current_user",  # Would be actual user ID
            "created_at": now,
        }
    else:
        team_id = list(_teams_db.keys())[0]

    member = {
        "id": member_id,
        "team_id": team_id,
        "email": request.email,
        "name": None,
        "role_id": request.role_id,
        "status": "pending",
        "invited_at": now,
        "joined_at": None,
    }

    _team_members_db[member_id] = member

    return {
        "id": member_id,
        "email": request.email,
        "role": _roles_db[request.role_id],
        "status": "pending",
        "message": f"Invitation sent to {request.email}",
    }


@router.patch(
    "/team/members/{member_id}",
    summary="Update team member",
    description="Update a team member's role.",
)
async def update_team_member(member_id: str, role_id: str):
    """Update team member role."""
    if member_id not in _team_members_db:
        raise HTTPException(status_code=404, detail="Member not found")

    if role_id not in _roles_db:
        raise HTTPException(status_code=400, detail="Invalid role")

    _team_members_db[member_id]['role_id'] = role_id

    return {"message": "Member role updated"}


@router.delete(
    "/team/members/{member_id}",
    status_code=204,
    summary="Remove team member",
    description="Remove a member from the team.",
)
async def remove_team_member(member_id: str):
    """Remove team member."""
    if member_id not in _team_members_db:
        raise HTTPException(status_code=404, detail="Member not found")

    del _team_members_db[member_id]


# --- Permissions Endpoints ---

@router.get(
    "/permissions",
    summary="List permissions",
    description="Get all available permissions.",
)
async def list_permissions():
    """List all available permissions."""
    return {
        "resources": {
            "agents": {
                "description": "AI agents management",
                "actions": ["create", "read", "update", "delete", "execute"],
            },
            "workflows": {
                "description": "Workflow management",
                "actions": ["create", "read", "update", "delete", "execute"],
            },
            "executions": {
                "description": "Execution monitoring",
                "actions": ["read", "cancel"],
            },
            "webhooks": {
                "description": "Webhook configuration",
                "actions": ["create", "read", "update", "delete"],
            },
            "settings": {
                "description": "Account settings",
                "actions": ["read", "update"],
            },
            "team": {
                "description": "Team management",
                "actions": ["create", "read", "update", "delete"],
            },
        }
    }
