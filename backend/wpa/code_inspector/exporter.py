import json
from pathlib import Path
from typing import List, Dict, Any

from .recorder import CodeRecorder

class CodeExporter:
    """
    Exports the recorded code history for a given job_id into various formats.
    """
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.recorder = CodeRecorder(job_id)
        self.history = self.recorder.get_history()
        self.export_dir = self.recorder.base_dir

    def _generate_header(self, file_format: str) -> str:
        """Creates a standard header for the exported files."""
        header = {
            "py": "#",
            "json": "//",
            "txt": "#"
        }
        comment_char = header.get(file_format, "#")
        return (
            f"{comment_char} SADI Code Export\n"
            f"{comment_char} Job ID: {self.job_id}\n"
            f"{comment_char} Total Steps: {len(self.history)}\n"
            f"{comment_char} {'-'*40}\n\n"
        )

    def export_to_python(self) -> Path:
        """Exports the code history to a single Python (.py) file."""
        file_path = self.export_dir / "export.py"
        content = self._generate_header("py")

        for i, block in enumerate(self.history):
            content += f"# --- Step {i+1}: {block['step_name']} ---\n"
            content += f"# Timestamp: {block['timestamp']}\n"
            if block.get("explanation"):
                content += f"# Explanation: {block['explanation']}\n"
            content += block['code']
            content += "\n\n"

        with open(file_path, "w") as f:
            f.write(content)

        return file_path

    def export_to_json(self) -> Path:
        """Exports the code history to a JSON file (which is its native format)."""
        # The history is already in JSON format, so we just ensure it's saved.
        file_path = self.export_dir / "export.json"
        with open(file_path, "w") as f:
            json.dump(self.history, f, indent=2)
        return file_path

    def export_to_text(self) -> Path:
        """Exports the code history to a human-readable text (.txt) file."""
        file_path = self.export_dir / "export.txt"
        content = self._generate_header("txt")

        for i, block in enumerate(self.history):
            content += f"--- Step {i+1}: {block['step_name']} ---\n"
            content += f"Timestamp: {block['timestamp']}\n"
            if block.get("explanation"):
                content += f"Explanation: {block['explanation']}\n"
            content += f"Code:\n```python\n{block['code']}\n```\n\n"

        with open(file_path, "w") as f:
            f.write(content)

        return file_path

    def prepare_for_report(self) -> List[Dict[str, Any]]:
        """
        Prepares the code history in a simple list format suitable for
        being embedded in other reports (e.g., DOCX, PDF).
        """
        # This is already the native format, but this function makes the intent clear.
        return self.history
