from pydantic import BaseModel


class EvalExample(BaseModel):
    question: str
    contexts: list[str]
    answer: str
    ground_truth: str | None = None
