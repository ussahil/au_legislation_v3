import subprocess
import sys
from pathlib import Path

'''
Ensure data path  is near data folder
'''

BASE_DIR = Path(__file__).resolve().parent

INITIAL_SCRIPT = BASE_DIR / "xml_to_rag_chunks.py"
MERGE_SCRIPT = BASE_DIR / "final_merge.py"

def run(script_path):
    print(f"\n▶ Running: {script_path.name}")
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"❌ Failed: {script_path.name}")

if __name__ == "__main__":
    run(INITIAL_SCRIPT)
    run(MERGE_SCRIPT)
    print("\n✅ Pipeline completed successfully")
