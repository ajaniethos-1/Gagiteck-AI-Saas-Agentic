"""Database repositories for data access."""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import User, Agent, Workflow, Execution, APIKey


class UserRepository:
    """Repository for User operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: User) -> User:
        """Update user."""
        user.updated_at = datetime.utcnow()
        await self.session.flush()
        return user


class AgentRepository:
    """Repository for Agent operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, agent_id: str, owner_id: Optional[str] = None) -> Optional[Agent]:
        """Get agent by ID, optionally filtered by owner."""
        query = select(Agent).where(Agent.id == agent_id)
        if owner_id:
            query = query.where(Agent.owner_id == owner_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        owner_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Agent], int]:
        """List agents with pagination."""
        # Get total count
        count_query = select(func.count()).select_from(Agent).where(Agent.owner_id == owner_id)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get agents
        query = (
            select(Agent)
            .where(Agent.owner_id == owner_id)
            .order_by(Agent.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        agents = result.scalars().all()

        return list(agents), total

    async def create(self, agent: Agent) -> Agent:
        """Create a new agent."""
        self.session.add(agent)
        await self.session.flush()
        return agent

    async def update(self, agent: Agent) -> Agent:
        """Update agent."""
        agent.updated_at = datetime.utcnow()
        await self.session.flush()
        return agent

    async def delete(self, agent_id: str, owner_id: str) -> bool:
        """Delete agent."""
        result = await self.session.execute(
            delete(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        )
        return result.rowcount > 0


class WorkflowRepository:
    """Repository for Workflow operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, workflow_id: str, owner_id: Optional[str] = None) -> Optional[Workflow]:
        """Get workflow by ID."""
        query = select(Workflow).where(Workflow.id == workflow_id)
        if owner_id:
            query = query.where(Workflow.owner_id == owner_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        owner_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Workflow], int]:
        """List workflows with pagination."""
        count_query = select(func.count()).select_from(Workflow).where(Workflow.owner_id == owner_id)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        query = (
            select(Workflow)
            .where(Workflow.owner_id == owner_id)
            .order_by(Workflow.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        workflows = result.scalars().all()

        return list(workflows), total

    async def create(self, workflow: Workflow) -> Workflow:
        """Create a new workflow."""
        self.session.add(workflow)
        await self.session.flush()
        return workflow

    async def update(self, workflow: Workflow) -> Workflow:
        """Update workflow."""
        workflow.updated_at = datetime.utcnow()
        await self.session.flush()
        return workflow

    async def delete(self, workflow_id: str, owner_id: str) -> bool:
        """Delete workflow."""
        result = await self.session.execute(
            delete(Workflow).where(Workflow.id == workflow_id, Workflow.owner_id == owner_id)
        )
        return result.rowcount > 0


class ExecutionRepository:
    """Repository for Execution operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, execution_id: str, user_id: Optional[str] = None) -> Optional[Execution]:
        """Get execution by ID."""
        query = select(Execution).where(Execution.id == execution_id)
        if user_id:
            query = query.where(Execution.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> Tuple[List[Execution], int]:
        """List executions with pagination."""
        base_query = select(Execution).where(Execution.user_id == user_id)
        if status:
            base_query = base_query.where(Execution.status == status)

        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        query = base_query.order_by(Execution.started_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        executions = result.scalars().all()

        return list(executions), total

    async def create(self, execution: Execution) -> Execution:
        """Create a new execution."""
        self.session.add(execution)
        await self.session.flush()
        return execution

    async def update(self, execution: Execution) -> Execution:
        """Update execution."""
        await self.session.flush()
        return execution


class APIKeyRepository:
    """Repository for API Key operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """Get API key by hash."""
        result = await self.session.execute(
            select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> List[APIKey]:
        """List API keys for user."""
        result = await self.session.execute(
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .order_by(APIKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, api_key: APIKey) -> APIKey:
        """Create a new API key."""
        self.session.add(api_key)
        await self.session.flush()
        return api_key

    async def delete(self, key_id: str, user_id: str) -> bool:
        """Delete API key."""
        result = await self.session.execute(
            delete(APIKey).where(APIKey.id == key_id, APIKey.user_id == user_id)
        )
        return result.rowcount > 0

    async def update_last_used(self, api_key: APIKey) -> None:
        """Update last used timestamp."""
        api_key.last_used_at = datetime.utcnow()
        await self.session.flush()
