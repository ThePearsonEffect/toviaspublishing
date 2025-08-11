from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import ensure_output_dir


PROGRESS_FILE_NAME = "progress.jsonl"


@dataclass
class ProgressRecord:
    run_id: str
    phase: str
    step: str
    status: str  # started | success | error | info
    message: str
    timestamp: float
    extra: Optional[Dict[str, Any]] = None


def _progress_file() -> Path:
    out_dir = Path(ensure_output_dir())
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / PROGRESS_FILE_NAME


def _write_record(record: ProgressRecord) -> None:
    pf = _progress_file()
    with pf.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def generate_run_id(kind: str) -> str:
    # kind-YYYYMMDDHHMMSS-ms
    now = time.time()
    base = time.strftime("%Y%m%d%H%M%S", time.localtime(now))
    ms = int((now - int(now)) * 1000)
    return f"{kind}-{base}-{ms:03d}"


def log(run_id: str, phase: str, step: str, status: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    rec = ProgressRecord(
        run_id=run_id,
        phase=phase,
        step=step,
        status=status,
        message=message,
        timestamp=time.time(),
        extra=extra or {},
    )
    _write_record(rec)


def read_run(run_id: str) -> List[ProgressRecord]:
    pf = _progress_file()
    records: List[ProgressRecord] = []
    if not pf.exists():
        return records
    with pf.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("run_id") == run_id:
                    records.append(ProgressRecord(**obj))
            except Exception:
                continue
    return records


def tail(n: int = 50) -> List[ProgressRecord]:
    pf = _progress_file()
    if not pf.exists():
        return []
    with pf.open("r", encoding="utf-8") as f:
        lines = f.readlines()[-n:]
    recs: List[ProgressRecord] = []
    for line in lines:
        try:
            recs.append(ProgressRecord(**json.loads(line)))
        except Exception:
            continue
    return recs


def summarize_run(run_id: str) -> Dict[str, Any]:
    records = read_run(run_id)
    if not records:
        return {"run_id": run_id, "found": False}
    phases: Dict[str, List[ProgressRecord]] = {}
    for r in records:
        phases.setdefault(r.phase, []).append(r)
    status = "success"
    for r in records:
        if r.status == "error":
            status = "error"
            break
    return {
        "run_id": run_id,
        "found": True,
        "status": status,
        "phases": {p: [asdict(r) for r in rs] for p, rs in phases.items()},
        "started_at": min(r.timestamp for r in records),
        "finished_at": max(r.timestamp for r in records),
    }
