"""Write a step record: python step.py <project root> <step number> <record.json>
record.json: {"title", "summary", "findings": [...], "tables": [{"title", "columns", "rows"}], "diagrams": [mermaid text],
"messages": [{"who": "user"|"assistant", "text"}]}"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import records  # noqa: E402

if __name__ == "__main__":
    print(records.write_step(sys.argv[1], int(sys.argv[2]), json.loads(Path(sys.argv[3]).read_text())))
