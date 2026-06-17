import json
from datetime import datetime
from pathlib import Path

ATTEMPTS_PATH = Path("data/attempts.json")
ATTEMPTS_PATH.parent.mkdir(exist_ok=True)


def save_attempt(case_data, clarification, answer, feedback):
    attempt = {
        "timestamp": datetime.now().isoformat(),
        "case": case_data,
        "clarification": clarification,
        "answer": answer,
        "feedback": feedback,
    }

    if ATTEMPTS_PATH.exists():
        attempts = json.loads(ATTEMPTS_PATH.read_text())
    else:
        attempts = []

    attempts.append(attempt)
    ATTEMPTS_PATH.write_text(json.dumps(attempts, indent=2))


def load_attempts():
    if not ATTEMPTS_PATH.exists():
        return []

    return json.loads(ATTEMPTS_PATH.read_text())