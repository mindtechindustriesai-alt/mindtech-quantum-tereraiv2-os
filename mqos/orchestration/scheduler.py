"""Multi-tenant quantum job scheduler (in-memory, for future expansion)."""

import time
import uuid
from typing import Dict, Any, List, Optional
from collections import deque


class Scheduler:
    """Simple FIFO scheduler with priority support."""

    def __init__(self):
        self._queue: deque = deque()
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def submit(self, payload: Dict[str, Any], priority: int = 1) -> str:
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        entry = {
            "job_id": job_id,
            "payload": payload,
            "priority": priority,
            "submitted_at": time.time(),
            "status": "queued",
        }
        self._jobs[job_id] = entry
        self._queue.append(entry)
        return job_id

    def next_job(self) -> Optional[Dict[str, Any]]:
        if not self._queue:
            return None
        highest = max(self._queue, key=lambda e: e["priority"])
        self._queue.remove(highest)
        highest["status"] = "running"
        return highest

    def complete(self, job_id: str, result: Dict[str, Any]) -> None:
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = "completed"
            self._jobs[job_id]["result"] = result
            self._jobs[job_id]["completed_at"] = time.time()

    def status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

    def all_jobs(self) -> List[Dict[str, Any]]:
        return list(self._jobs.values())


scheduler = Scheduler()
