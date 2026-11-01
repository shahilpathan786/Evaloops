from sqlalchemy import (
    String,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.mixins import TimestampMixin


class ModelConfig(Base, TimestampMixin):
    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    model_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    api_base_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    config: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    project = relationship(
        "Project",
        back_populates="model_configs"
    )

    experiments = relationship(
        "Experiment",
        back_populates="model_config"
    )

    traces = relationship(
        "Trace",
        back_populates="model_config"
    )