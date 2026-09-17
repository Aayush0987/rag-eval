import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    source: Mapped[str] = mapped_column(String, default="batch")  # "batch" | "single"
    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)

    examples: Mapped[list["ExampleResult"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class ExampleResult(Base):
    __tablename__ = "example_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))

    question: Mapped[str] = mapped_column(Text)
    contexts: Mapped[list[str]] = mapped_column(JSON)
    answer: Mapped[str] = mapped_column(Text)
    ground_truth: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Custom, from-scratch metrics
    custom_faithfulness: Mapped[float | None] = mapped_column(Float, nullable=True)
    custom_answer_relevance_embedding: Mapped[float | None] = mapped_column(Float, nullable=True)
    custom_answer_relevance_llm: Mapped[float | None] = mapped_column(Float, nullable=True)
    custom_context_precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    custom_context_recall: Mapped[float | None] = mapped_column(Float, nullable=True)

    # RAGAS equivalents
    ragas_faithfulness: Mapped[float | None] = mapped_column(Float, nullable=True)
    ragas_answer_relevancy: Mapped[float | None] = mapped_column(Float, nullable=True)
    ragas_context_precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    ragas_context_recall: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Transparency: claims, per-claim entailment labels, judge reasoning, etc.
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    run: Mapped["Run"] = relationship(back_populates="examples")
