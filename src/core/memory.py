from __future__ import annotations
import json, os, time
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
METRICS_FILE = os.path.join(DATA_DIR, "metrics.jsonl")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.jsonl")

def save_session_turn(user_text: str, agent_text: str, meta: Dict[str, Any]):
    rec = {
        "ts": time.time(),
        "user": user_text,
        "agent": agent_text,
        "meta": meta,
    }
    with open(SESSIONS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

def save_metric(label: str, value: float, extra: Dict[str, Any] | None = None):
    rec = {"ts": time.time(), "label": label, "value": value, "extra": extra or {}}
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

EMO_FILE = os.path.join(DATA_DIR, "emotions.jsonl")

def save_emotion(tag: str, summary: str):
    rec = {
        "ts": time.time(),
        "tag": tag,
        "summary": summary,
    }
    with open(EMO_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
