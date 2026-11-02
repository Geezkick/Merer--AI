import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    projects: Mapped[list["Project"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Membership(TimestampMixin, Base):
    __tablename__ = "memberships"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_membership_organization_user",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        default="member",
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="memberships",
    )

    user: Mapped["User"] = relationship(
        back_populates="memberships",
    )


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_project_organization_slug",
        ),
        Index("ix_projects_organization_status", "organization_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="projects",
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Dataset(TimestampMixin, Base):
    __tablename__ = "datasets"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "name",
            name="uq_dataset_project_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="draft",
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        back_populates="datasets",
    )

    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
    )


class TestCase(TimestampMixin, Base):
    __tablename__ = "test_cases"

    __table_args__ = (
        UniqueConstraint(
            "dataset_id",
            "external_id",
            name="uq_test_case_dataset_external_id",
        ),
        Index("ix_test_cases_dataset_language", "dataset_id", "language"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_output: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    language: Mapped[str] = mapped_column(
        String(20),
        default="en",
        nullable=False,
    )

    case_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
    )

    dataset: Mapped["Dataset"] = relationship(
        back_populates="test_cases",
    )
