from sqlalchemy.orm import Session

from app.db.models import ExampleResult, Run
from app.metrics.pipeline import run_custom_metrics
from app.models.schema import EvalExample
from app.ragas_integration.run_ragas import run_ragas_metrics


def create_run(db: Session, examples: list[EvalExample], name: str, source: str) -> Run:
    run = Run(name=name, source=source)
    db.add(run)
    db.flush()

    for example in examples:
        custom = run_custom_metrics(example)
        ragas_scores = run_ragas_metrics(example)

        db.add(
            ExampleResult(
                run_id=run.id,
                question=example.question,
                contexts=example.contexts,
                answer=example.answer,
                ground_truth=example.ground_truth,
                **custom,
                **ragas_scores,
            )
        )

    db.commit()
    db.refresh(run)
    return run


def list_runs(db: Session) -> list[Run]:
    return db.query(Run).order_by(Run.created_at.desc()).all()


def get_run(db: Session, run_id: int) -> Run | None:
    return db.get(Run, run_id)


def set_baseline(db: Session, run_id: int) -> Run | None:
    run = db.get(Run, run_id)
    if run is None:
        return None
    run.is_baseline = True
    db.commit()
    db.refresh(run)
    return run
