"""Exercise the actual importer with a worksheet double and both firmware fixtures."""
import importlib.util
from datetime import date
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "uploader", ROOT / "ha/custom_components/msb_show_sheet/car_sheet.py")
uploader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uploader)
FIXTURES = Path(__file__).resolve().parents[1] / "rehearsal"


class UploadRehearsal(unittest.TestCase):
    def test_close_restart_and_repeat(self):
        cells = {}
        serial = (date(2026, 11, 24) - date(1899, 12, 30)).days

        def read(address, **options):
            if address in cells:
                return cells[address]
            return {"G2:K2": [uploader.COLUMNS], "D2": [["Temp"]],
                    "B3:K37": [[serial], [serial + 1]],
                    "G3:K37": [cells.get(f"G{row}:K{row}", [[]])[0] for row in (3, 4)],
                    "D3:D37": [cells.get(f"D{row}", [[]])[0] for row in (3, 4)]}[address]

        client = MagicMock()
        sheet = client.open_by_key.return_value.worksheet.return_value
        sheet.get.side_effect = read
        sheet.batch_update.side_effect = lambda writes, **kw: cells.update(
            {w["range"]: w["values"] for w in writes})
        args = SimpleNamespace(credentials="unused", write=True)
        with patch.object(uploader, "sheets_client", return_value=client), patch.object(uploader, "datetime") as clock:
            clock.now.return_value.date.return_value = date(2026, 11, 24)
            with self.assertRaises(ValueError):
                uploader.import_sheet(args, rehearsal_book=uploader.BOOK,
                                      report_file=FIXTURES / "initial.csv")
            client.open_by_key.assert_not_called()
            def sync(filename, closing_day=None):
                return uploader.import_sheet(args, closing_day, rehearsal_book="test-copy",
                                             report_file=FIXTURES / filename)
            self.assertEqual(sync("initial.csv"), 0)
            self.assertEqual(sync("initial.csv", date(2026, 11, 24)), 2)
            clock.now.return_value.date.return_value = date(2026, 11, 26)
            self.assertEqual(sync("catch-up.csv"), 1)
            self.assertEqual(sync("catch-up.csv"), 0)
            self.assertEqual(cells, {"G3:K3": [[2, 3, 5, 7, 11]], "D3": [[30.8]],
                                     "G4:K4": [[13, 0, 17, 19, 23]]})
            self.assertTrue(all(c.args == ("test-copy",) for c in client.open_by_key.call_args_list))
