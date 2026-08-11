from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

WORKBOOK_PATH = BASE_DIR / "data" / "project_tracker.xlsx"