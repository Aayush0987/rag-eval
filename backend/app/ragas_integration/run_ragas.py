from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from ragas import SingleTurnSample, evaluate
from ragas.dataset_schema import EvaluationDataset
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)

from app.config import settings
from app.models.schema import EvalExample

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"


@lru_cache
def _ragas_llm() -> LangchainLLMWrapper:
    chat = ChatOpenAI(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        base_url=_GROQ_BASE_URL,
        temperature=0,
    )
    return LangchainLLMWrapper(chat)


@lru_cache
def _ragas_embeddings() -> LangchainEmbeddingsWrapper:
    return LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))


def run_ragas_metrics(example: EvalExample) -> dict:
    """Run the same input through RAGAS's equivalent metrics for side-by-side comparison."""
    sample = SingleTurnSample(
        user_input=example.question,
        retrieved_contexts=example.contexts,
        response=example.answer,
        reference=example.ground_truth,
    )
    dataset = EvaluationDataset(samples=[sample])

    metrics = [Faithfulness(), AnswerRelevancy(), ContextPrecision()]
    if example.ground_truth:
        metrics.append(ContextRecall())

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=_ragas_llm(),
        embeddings=_ragas_embeddings(),
        show_progress=False,
    )
    scores = result.scores[0]

    return {
        "ragas_faithfulness": scores.get("faithfulness"),
        "ragas_answer_relevancy": scores.get("answer_relevancy"),
        "ragas_context_precision": scores.get("context_precision"),
        "ragas_context_recall": scores.get("context_recall"),
    }
