from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.mixins import TimestampMixin


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    __table_args__ = (
        UniqueConstraint(
            "project_id", "name",
            name="uq_dataset_project_name"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    project = relationship("Project", back_populates="datasets")
    records = relationship(
        "DatasetRecord",
        back_populates="dataset",
        cascade="all, delete-orphan"
    )

    experiments = relationship(
    "Experiment",
    back_populates="dataset"
    )