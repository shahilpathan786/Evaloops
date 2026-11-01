from sqlalchemy import (
    Text,
    String,
    Integer,
    Float,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.mixins import TimestampMixin


class Trace(Base, TimestampMixin):
    __tablename__ = "traces"

    __table_args__ = (
        CheckConstraint(
            "status IN ('success', 'error')",
            name="ck_trace_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    model_config_id: Mapped[int | None] = mapped_column(
        ForeignKey("model_configs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    input: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    output: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    prompt_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    completion_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="success",
        nullable=False
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    project = relationship(
        "Project",
        back_populates="traces"
    )

    model_config = relationship(
        "ModelConfig",
        back_populates="traces"
    )