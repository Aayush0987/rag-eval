import math
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
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
_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"


@lru_cache
def _groq_llm() -> LangchainLLMWrapper:
    chat = ChatOpenAI(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        base_url=_GROQ_BASE_URL,
        temperature=0,
    )
    return LangchainLLMWrapper(chat)


@lru_cache
def _gemini_llm() -> LangchainLLMWrapper:
    chat = ChatOpenAI(
        model=settings.gemini_model,
        api_key=settings.gemini_api_key,
        base_url=_GEMINI_BASE_URL,
        temperature=0,
    )
    return LangchainLLMWrapper(chat)


@lru_cache
def _ragas_embeddings() -> LangchainEmbeddingsWrapper:
    return LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))


def _evaluate(sample: SingleTurnSample, metrics: list, llm: LangchainLLMWrapper) -> dict:
    dataset = EvaluationDataset(samples=[sample])
    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm,
        embeddings=_ragas_embeddings(),
        show_progress=False,
        raise_exceptions=False,
    )
    return result.scores[0]


def _has_failures(scores: dict) -> bool:
    return any(v is None or (isinstance(v, float) and math.isnan(v)) for v in scores.values())


def run_ragas_metrics(example: EvalExample) -> dict:
    """Run the same input through RAGAS's equivalent metrics for side-by-side comparison.

    Tries Groq first; if any metric comes back NaN (RAGAS's own signal for a
    failed judge call — covers both the per-minute and the harder-to-retry
    daily rate limit) and a Gemini key is configured, retries the whole
    evaluation against Gemini instead. Composing the two providers into one
    LangChain fallback runnable was tried first but breaks RAGAS's internal
    temperature-setting logic, which expects a plain ChatModel.
    """
    sample = SingleTurnSample(
        user_input=example.question,
        retrieved_contexts=example.contexts,
        response=example.answer,
        reference=example.ground_truth,
    )

    metrics = [Faithfulness(), AnswerRelevancy(), ContextPrecision()]
    if example.ground_truth:
        metrics.append(ContextRecall())

    scores = _evaluate(sample, metrics, _groq_llm())
    if _has_failures(scores) and settings.gemini_api_key:
        scores = _evaluate(sample, metrics, _gemini_llm())

    return {
        "ragas_faithfulness": scores.get("faithfulness"),
        "ragas_answer_relevancy": scores.get("answer_relevancy"),
        "ragas_context_precision": scores.get("context_precision"),
        "ragas_context_recall": scores.get("context_recall"),
    }
