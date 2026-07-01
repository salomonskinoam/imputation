"""Objective -> (primary, gates) split, decided in one place (parity with fusion).

v1 has a single graded metric (macro-F1) and no gate metrics, but keep the SSOT so verify and the
prompt never disagree if gates are added later.
"""
from __future__ import annotations

from typing import Iterable, List, Tuple


def resolve(objective: str, metrics: Iterable[str]) -> Tuple[str, List[str]]:
    primary = objective
    gates = [m for m in metrics if m != primary]
    return primary, gates
