"""Run a project's tests: python check.py <project>  ->  {"ok", "passed", "failed", "output"}"""
import json
import re
import subprocess
import sys

if __name__ == "__main__":
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], cwd=sys.argv[1],
                         capture_output=True, text=True)
    tail = (out.stdout + out.stderr)[-3000:]

    def n(word):
        m = re.search(rf"(\d+) {word}", tail)
        return int(m.group(1)) if m else 0
    print(json.dumps({"ok": out.returncode == 0, "passed": n("passed"), "failed": n("failed") + n("error"), "output": tail}))
