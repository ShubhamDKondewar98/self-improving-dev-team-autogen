import json
import os
from datetime import datetime, timezone
from config.constants import ATTEMPT_LOG_DIR


def log_attempt(run_result: dict) -> str:
    """
    Writes a single run's outcome (the dict returned by run_dev_team) to
    a timestamped JSON file on disk under ATTEMPT_LOG_DIR.
    Returns the path of the file written.
    """
    os.makedirs(ATTEMPT_LOG_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"run_{timestamp}.json"
    filepath = os.path.join(ATTEMPT_LOG_DIR, filename)

    log_entry = {
        "timestamp": timestamp,
        **run_result,
    }

    with open(filepath, "w") as f:
        json.dump(log_entry, f, indent=2)

    return filepath


def load_attempt(filepath: str) -> dict | None:
    """
    Reads back a previously logged run for display (Streamlit / PDF report).
    Returns None if the file is missing or contains malformed/truncated
    JSON (e.g. from a run that was interrupted mid-write) -- callers must
    check for None rather than assume every logged file is readable.
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"WARNING: could not load attempt log '{filepath}': {e}")
        return None


def list_attempts() -> list[str]:
    """Returns paths of all logged runs, most recent first."""
    if not os.path.exists(ATTEMPT_LOG_DIR):
        return []
    files = [
        os.path.join(ATTEMPT_LOG_DIR, f)
        for f in os.listdir(ATTEMPT_LOG_DIR)
        if f.startswith("run_") and f.endswith(".json")
    ]
    return sorted(files, reverse=True)


def update_attempt_decision(filepath: str, decision: str) -> None:
    """
    Updates an EXISTING attempt log file with a human's approve/reject
    decision -- does not create a new file, writes back to the same
    filepath the run was originally logged to.
    """
    data = load_attempt(filepath)
    data["human_decision"] = decision

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)