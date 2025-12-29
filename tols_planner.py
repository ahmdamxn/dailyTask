from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class PlannedItem:
    id: str
    title: str
    risk: int
    est_minutes: int
    tags: List[str]
    reason: str


def plan_tests(tasks: List[Dict[str, Any]], changed_files: List[str]) -> List[PlannedItem]:
    """
    Simple v1 heuristic:
    - Base score = risk
    - Bonus if task tags appear in any changed file path (e.g. "ethercat", "power")
    - Sort by score desc then shorter tasks first
    """
    lower_files = " ".join(changed_files).lower()

    planned: List[PlannedItem] = []
    for t in tasks:
        tags = [x.lower() for x in t.get("tags", [])]
        risk = int(t.get("risk", 3))
        est = int(t.get("est_minutes", 30))
        bonus = 0

        matched = [tag for tag in tags if tag and tag in lower_files]
        if matched:
            bonus = 2
            reason = f"Related to recent changes: {', '.join(matched)}"
        else:
            reason = "High-risk or routine coverage"

        score = risk + bonus

        planned.append(
            PlannedItem(
                id=str(t.get("id", "")),
                title=str(t.get("title", "")),
                risk=score,
                est_minutes=est,
                tags=[x for x in t.get("tags", [])],
                reason=reason,
            )
        )

    planned.sort(key=lambda x: (-x.risk, x.est_minutes, x.id))
    return planned
