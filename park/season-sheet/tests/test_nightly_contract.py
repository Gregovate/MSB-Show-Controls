import runpy
import unittest
from datetime import date
from pathlib import Path

root = Path(__file__).resolve().parents[3]
entries = runpy.run_path(str(root / "ha/custom_components/msb_show_sheet/car_sheet.py"))["entries"]
night = date(2026, 11, 27)


class NightlyContract(unittest.TestCase):
    def read(self, header, row):
        return entries(header + "\n" + row, {night}, night, night)[night]

    def test_current_and_legacy(self):
        base = "Date,DaysRunning,6PM,7PM,8PM,9PM,"
        row = "2026-11-27,1,8,3,0,0,"
        current = base + "After9PM,DailyTotal,ShowTotal,DailyAvgTemp,ExtensionMin"
        legacy = base + "DailyTotal,ShowTotal,DailyAvgTemp,10PM,ExtensionMin"
        for late, extension in [(2, 0), (2, 30), (0, 0)]:
            self.assertEqual(self.read(current, row + f"{late},{11+late},34,,{extension}"),
                             ([8, 3, 0, 0, late], None))
        self.assertEqual(self.read(legacy, row + "13,34,0,,"), ([8, 3, 0, 0, 2], 0.0))
        with self.assertRaises(ValueError):
            self.read(current, row + "0,13,34,,0")
        with self.assertRaises(ValueError):
            self.read(current.replace("6PM", "Before5,6PM"), row + "0,13,34,,0")
