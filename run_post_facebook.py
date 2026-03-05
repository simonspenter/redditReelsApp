import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
POSTER = PROJECT_ROOT / "post_one_facebook.py"

def main():
    python = sys.executable
    result = subprocess.run([python, str(POSTER)], cwd=str(PROJECT_ROOT))
    raise SystemExit(result.returncode)

if __name__ == "__main__":
    main()
