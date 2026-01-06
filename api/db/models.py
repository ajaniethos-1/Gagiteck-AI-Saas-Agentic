"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class User(Base):
    """User model."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    workflows: Mapped[list["Workflow"]] = relationship("Workflow", back_populates="owner", cascade="all, delete-orphan")
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")


class Agent(Base):
    """Agent model."""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(50), default="claude-3-sonnet")
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_iterations: Mapped[int] = mapped_column(Integer, default=25)
    timeout_ms: Mapped[int] = mapped_column(Integer, default=120000)
    tools: Mapped[list] = mapped_column(JSON, default=list)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="active")
    owner_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="agents")
    executions: Mapped[list["Execution"]] = relationship("Execution", back_populates="agent", cascade="all, delete-orphan")


class Workflow(Base):
    """Workflow model."""
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    steps: Mapped[list] = mapped_column(JSON, default=list)
    triggers: Mapped[list] = mapped_column(JSON, default=list)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="active")
    owner_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="workflows")
    executions: Mapped[list["Execution"]] = relationship("Execution", back_populates="workflow", cascade="all, delete-orphan")


class Execution(Base):
    """Execution model for tracking agent and workflow runs."""
    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'agent' or 'workflow'
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, running, completed, failed, cancelled
    input_data: Mapped[dict] = mapped_column(JSON, default=dict)
    output_data: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("agents.id"), nullable=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("workflows.id"), nullable=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="executions")
    workflow: Mapped[Optional["Workflow"]] = relationship("Workflow", back_populates="executions")
    user: Mapped["User"] = relationship("User")


class APIKey(Base):
    """API Key model."""
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)  # First chars for display
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
