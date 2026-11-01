from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.mixins import TimestampMixin


class DatasetRecord(Base, TimestampMixin):
    __tablename__ = "dataset_records"

    id: Mapped[int] = mapped_column(primary_key=True)

    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    input: Mapped[str] = mapped_column(Text, nullable=False)

    expected_output: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    dataset = relationship("Dataset", back_populates="records")
    
    evaluation_results = relationship(
    "EvaluationResult",
    back_populates="dataset_record"
    )