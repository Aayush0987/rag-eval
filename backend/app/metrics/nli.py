from functools import lru_cache

from sentence_transformers import CrossEncoder

_MODEL_NAME = "cross-encoder/nli-deberta-v3-base"


@lru_cache
def _model() -> CrossEncoder:
    return CrossEncoder(_MODEL_NAME)


def entailment_score(premise: str, hypothesis: str) -> dict:
    """Classify whether `premise` entails `hypothesis`.

    Returns label probabilities and the winning label, using the model's own
    id2label mapping rather than an assumed label order.
    """
    model = _model()
    logits = model.predict([(premise, hypothesis)])[0]
    probs = _softmax(logits)
    id2label = model.config.id2label
    scores = {id2label[i].lower(): float(probs[i]) for i in range(len(probs))}
    label = max(scores, key=scores.get)
    return {"label": label, "scores": scores}


def _softmax(logits):
    import numpy as np

    exp = np.exp(logits - np.max(logits))
    return exp / exp.sum()
