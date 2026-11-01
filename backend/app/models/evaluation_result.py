from sqlalchemy import (
    Text,
    Float,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.mixins import TimestampMixin


class EvaluationResult(Base, TimestampMixin):
    __tablename__ = "evaluation_results"

    __table_args__ = (
        UniqueConstraint(
            "experiment_id",
            "dataset_record_id",
            name="uq_experiment_dataset_record"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    experiment_id: Mapped[int] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    dataset_record_id: Mapped[int] = mapped_column(
        ForeignKey("dataset_records.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    actual_output: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    scores: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )

    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    experiment = relationship(
        "Experiment",
        back_populates="results"
    )

    dataset_record = relationship(
        "DatasetRecord",
        back_populates="evaluation_results"
    )