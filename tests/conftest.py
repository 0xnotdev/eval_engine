import sys
from pathlib import Path

# Insert the src directory into sys.path so tests can resolve eval_engine
src_path = str(Path(__file__).resolve().parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
