import json

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.schemas import ExampleResultOut, RunDetail, RunSummary, SingleExampleRequest
from app.db import crud
from app.db.database import get_db
from app.db.models import Run
from app.metrics.regression import compare_runs
from app.models.schema import EvalExample

router = APIRouter()


def _run_avg(run: Run, field: str) -> float | None:
    values = [getattr(e, field) for e in run.examples if getattr(e, field) is not None]
    return sum(values) / len(values) if values else None


def _run_summary(run: Run) -> RunSummary:
    return RunSummary(
        id=run.id,
        name=run.name,
        created_at=run.created_at.isoformat(),
        source=run.source,
        is_baseline=run.is_baseline,
        num_examples=len(run.examples),
        avg_custom_faithfulness=_run_avg(run, "custom_faithfulness"),
        avg_ragas_faithfulness=_run_avg(run, "ragas_faithfulness"),
    )


def _run_detail(run: Run) -> RunDetail:
    return RunDetail(
        id=run.id,
        name=run.name,
        created_at=run.created_at.isoformat(),
        source=run.source,
        is_baseline=run.is_baseline,
        examples=[ExampleResultOut.model_validate(e, from_attributes=True) for e in run.examples],
    )


@router.post("/runs/batch", response_model=RunSummary)
async def submit_batch(
    file: UploadFile, run_name: str = Form("batch-run"), db: Session = Depends(get_db)
):
    raw = (await file.read()).decode("utf-8")
    examples = []
    for line_no, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise HTTPException(400, f"Invalid JSON on line {line_no}: {exc}") from exc
        examples.append(EvalExample.model_validate(payload))

    if not examples:
        raise HTTPException(400, "No examples found in uploaded file")

    run = crud.create_run(db, examples, name=run_name, source="batch")
    return _run_summary(run)


@router.post("/runs/single", response_model=RunSummary)
def submit_single(request: SingleExampleRequest, db: Session = Depends(get_db)):
    example = EvalExample(**request.model_dump(exclude={"run_name"}))
    run = crud.create_run(db, [example], name=request.run_name, source="single")
    return _run_summary(run)


@router.get("/runs", response_model=list[RunSummary])
def get_runs(db: Session = Depends(get_db)):
    return [_run_summary(r) for r in crud.list_runs(db)]


@router.get("/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = crud.get_run(db, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return _run_detail(run)


@router.post("/runs/{run_id}/baseline", response_model=RunSummary)
def mark_baseline(run_id: int, db: Session = Depends(get_db)):
    run = crud.set_baseline(db, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return _run_summary(run)


@router.get("/regression")
def get_regression(baseline_id: int, run_id: int, db: Session = Depends(get_db)):
    baseline = crud.get_run(db, baseline_id)
    new = crud.get_run(db, run_id)
    if baseline is None or new is None:
        raise HTTPException(404, "Run not found")
    if not baseline.is_baseline:
        raise HTTPException(400, f"Run {baseline_id} is not marked as a baseline")
    return compare_runs(baseline.examples, new.examples)
