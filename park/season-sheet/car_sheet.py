"""Run the same sheet importer as the Home Assistant sheet service."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    sheet_module = Path(__file__).resolve().parents[2] / "ha/custom_components/msb_show_sheet/car_sheet.py"
    runpy.run_path(str(sheet_module), run_name="__main__")
