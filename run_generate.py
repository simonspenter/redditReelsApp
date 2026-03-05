import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
APP_PY = PROJECT_ROOT / "app.py"

def main():
    # Use the same python interpreter that runs this file
    python = sys.executable
    result = subprocess.run([python, str(APP_PY)], cwd=str(PROJECT_ROOT))
    raise SystemExit(result.returncode)

if __name__ == "__main__":
    main()
