from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.mixins import TimestampMixin
from app.models.dataset import Dataset


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_project_user_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner = relationship("User", back_populates="projects")

    datasets = relationship(
    "Dataset",
    back_populates="project",
    cascade="all, delete-orphan"
    )

    model_configs = relationship(
    "ModelConfig",
    back_populates="project",
    cascade="all, delete-orphan"
    )

    prompts = relationship(
    "Prompt",
    back_populates="project",
    cascade="all, delete-orphan"
    )

    experiments = relationship(
    "Experiment",
    back_populates="project",
    cascade="all, delete-orphan"
    )

    traces = relationship(
    "Trace",
    back_populates="project",
    cascade="all, delete-orphan"
    )