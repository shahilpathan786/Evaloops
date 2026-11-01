from sqlalchemy import (
    String,
    Integer,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.mixins import TimestampMixin


class Prompt(Base, TimestampMixin):
    __tablename__ = "prompts"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "name",
            "version",
            name="uq_prompt_project_name_version"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    template: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    system_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    project = relationship(
        "Project",
        back_populates="prompts"
    )

    experiments = relationship(
        "Experiment",
        back_populates="prompt"
    )