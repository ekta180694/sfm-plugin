"""Record a decision made in the chat: python decide.py <project root> <step> approve|feedback|back [--text T] [--who W]"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import records  # noqa: E402

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("root"), a.add_argument("step", type=int), a.add_argument("decision")
    a.add_argument("--text", default=""), a.add_argument("--who", default="")
    x = a.parse_args()
    print(json.dumps(records.decide(x.root, x.step, x.decision, x.text, x.who, "chat")))
