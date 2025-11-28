import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class CodeRecorder:
    """
    Records code blocks generated during a SADI analysis job.
    Manages the state for a specific job_id.
    """
    _instances: Dict[str, "CodeRecorder"] = {}

    def __new__(cls, job_id: str):
        if job_id not in cls._instances:
            cls._instances[job_id] = super(CodeRecorder, cls).__new__(cls)
        return cls._instances[job_id]

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.base_dir = Path(f"data/processed/{self.job_id}/code")
        self.history_file = self.base_dir / "history.json"
        # Keywords that are not allowed for security reasons
        self._harmful_keywords = [
            "os.system", "subprocess", "eval(", "exec(",
            "rm -rf", "drop table", "alter table", "delete from"
        ]
        self.start_capture()

    def start_capture(self):
        """Initializes the storage directory and history file for a new session."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            with open(self.history_file, "w") as f:
                json.dump([], f)

    def _is_harmful(self, code_string: str) -> bool:
        """Performs a basic check for potentially harmful code keywords."""
        lower_code = code_string.lower()
        return any(keyword in lower_code for keyword in self._harmful_keywords)

    def save_block(self, step_name: str, code_string: str, explanation: str = ""):
        """
        Saves a block of code to the job's history, enforcing business rules.
        """
        if not code_string or not code_string.strip():
            print(f"INFO: Skipping empty code block for step: {step_name}")
            return

        if self._is_harmful(code_string):
            # In a real scenario, this should also trigger a security alert.
            raise ValueError("Potentially harmful code detected. Operation aborted for security reasons.")

        history = self.get_history()

        # Rule: Do not save duplicate code
        if any(block['code'] == code_string for block in history):
            print(f"INFO: Skipping duplicate code block for step: {step_name}")
            return

        new_block = {
            "timestamp": datetime.utcnow().isoformat(),
            "step_name": step_name,
            "code": code_string,
            "explanation": explanation
        }
        history.append(new_block)

        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieves the full code history for the job."""
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Handle case where file is corrupted or empty
            return []

    def clear_history(self):
        """Clears the code history for the job by deleting the history file."""
        if self.history_file.exists():
            os.remove(self.history_file)
        # Re-initialize the empty list
        self.start_capture()
