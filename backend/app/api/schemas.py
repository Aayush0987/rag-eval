from pydantic import BaseModel

from app.models.schema import EvalExample


class RunSummary(BaseModel):
    id: int
    name: str
    created_at: str
    source: str
    is_baseline: bool
    num_examples: int
    avg_custom_faithfulness: float | None
    avg_ragas_faithfulness: float | None


class ExampleResultOut(BaseModel):
    id: int
    question: str
    contexts: list[str]
    answer: str
    ground_truth: str | None
    custom_faithfulness: float | None
    custom_answer_relevance_embedding: float | None
    custom_answer_relevance_llm: float | None
    custom_context_precision: float | None
    custom_context_recall: float | None
    ragas_faithfulness: float | None
    ragas_answer_relevancy: float | None
    ragas_context_precision: float | None
    ragas_context_recall: float | None
    details: dict


class RunDetail(BaseModel):
    id: int
    name: str
    created_at: str
    source: str
    is_baseline: bool
    examples: list[ExampleResultOut]


class SingleExampleRequest(EvalExample):
    run_name: str = "single-example"
