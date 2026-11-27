"""Import completed sheet rows from the park's Car Counter.

Install: python3 -m pip install 'gspread>=6,<7'
Share the 2026 Show Stats workbook with the service account as an editor.
On a park-network host with a private credentials file, run:
  python3 car_sheet.py --credentials /private/sheets.json
After checking the dates and buckets, add --write. Run with --write at 1 AM
local time daily; each run also processes missed earlier dates. Keep the
sheet credential on that host. A submitted zero is a real count.
"""
import argparse
import csv
from copy import deepcopy
import io
import json
import math
from datetime import date, datetime
from urllib.request import urlopen
from zoneinfo import ZoneInfo

BOOK = "1mcr-l7yX5TYO5tNqYIZwlm0_5AZgAX36NpHxjfmq5MQ"
SOURCE = "http://192.168.3.31/ShowSummaryBuckets.csv"
HOURS = ["6PM", "7PM", "8PM", "9PM"]
COLUMNS = ["Cars 5:00-6:00", "Cars 6:00-7:00", "Cars 7:00-8:00",
           "Cars 8:00-9:00", "Cars After 9 PM"]


def entries(data, scheduled, today, closing_day=None):
    # Source is the incremental sheet. The other sheet has a similar name
    # and cumulative counts; its header must never pass this check.
    data = csv.DictReader(io.StringIO(data))
    headers = data.fieldnames or []
    if "Before5" in headers or not {"Date", "DailyTotal", *HOURS}.issubset(headers):
        raise ValueError("Expected the Car Counter's ShowSummaryBuckets.csv")
    found = {}
    for record in data:
        day = date.fromisoformat(record["Date"])
        if day not in scheduled or day > today or (day == today and day != closing_day):
            continue
        if day in found:
            raise ValueError(f"Duplicate source date {day}")
        nums = [int(record[k]) for k in HOURS]
        total = int(record["DailyTotal"])
        if "After9PM" in headers:
            late = int(record["After9PM"])
            if sum(nums) + late != total:
                raise ValueError(f"After9PM and DailyTotal disagree for {day}")
        else:
            late = total - sum(nums)
        if min([late, *nums]) < 0:
            raise ValueError(f"Invalid vehicle count for {day}")
        # Blank means no verified show-window reading. Preserve a real zero.
        raw_temp = (record.get("DailyAvgTemp") or "").strip()
        temp = float(raw_temp) if raw_temp else None
        if temp is not None and not math.isfinite(temp):
            raise ValueError(f"Invalid DailyAvgTemp for {day}")
        found[day] = (nums + [late], temp)
    return found


def sheets_client(filename):
    import gspread

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    with open(filename, encoding="utf-8") as stream:
        info = json.load(stream)
    if info.get("type") == "authorized_user":
        from google.oauth2.credentials import Credentials
        credentials = Credentials.from_authorized_user_info(info, scopes=scopes)
        return gspread.authorize(credentials)
    if info.get("type") == "service_account":
        return gspread.service_account_from_dict(info, scopes=scopes)
    raise ValueError("Expected an authorized Workspace user or service account credential")


def import_sheet(args, closing_day=None, *, rehearsal_book=None, report_file=None):
    if report_file is not None and (not rehearsal_book or rehearsal_book.strip() == BOOK):
        raise ValueError("A rehearsal requires a separate workbook")
    sheet = sheets_client(args.credentials).open_by_key(rehearsal_book or BOOK).worksheet("Park Data 2026")
    header = sheet.get("G2:K2")[0]
    if [s.strip() for s in header] != COLUMNS:
        raise ValueError("Sheet layout changed; refusing to write")
    # Use sheet-local calendar serials; never parse locale-dependent amounts or dates.
    if sheet.get("D2")[0][0].strip() != "Temp":
        raise ValueError("Expected the sheet’s Temp header at D2")
    temps = sheet.get("D3:D37", value_render_option="FORMULA")
    rows = sheet.get("B3:K37", value_render_option="UNFORMATTED_VALUE")
    formulas = sheet.get("G3:K37", value_render_option="FORMULA")
    schedule = {}
    for ix, row in enumerate(rows):
        if row and isinstance(row[0], (int, float)):
            if len(row) > 3 and str(row[3]).strip().upper() == "CLOSED":
                continue
            day = date.fromordinal(date(1899, 12, 30).toordinal() + int(row[0]))
            if day in schedule:
                raise ValueError(f"Duplicate show date {day}")
            schedule[day] = ix
    # The rehearsal uses a local report so a simulated close never touches the counter.
    with (open(report_file, "rb") if report_file else urlopen(SOURCE, timeout=15)) as response:
        data = response.read(65537)
    if len(data) > 65536:
        raise ValueError("Unexpectedly large car sheet")
    today = datetime.now(ZoneInfo("America/Chicago")).date()
    source = entries(data.decode("utf-8-sig"), schedule, today, closing_day)
    if closing_day in schedule and closing_day <= today and closing_day not in source:
        raise ValueError(f"Expected a sheet for {closing_day}; firmware export missing")
    writes = []
    conflicts = []
    for day, (values, temp) in sorted(source.items()):
        ix = schedule[day]
        number = ix + 3
        initial = temps[ix][0] if ix < len(temps) and temps[ix] else None
        if temp is not None and initial in (None, ""):
            sheet_value = {"range": f"D{number}", "values": [[temp]]}
            writes.append(sheet_value)
        existing = list(formulas[ix]) if ix < len(formulas) else []
        existing.extend([""] * (5-len(existing)))
        if existing == values:
            continue
        if any(v is not None and v != "" for v in existing):
            conflicts.append(str(day))
            continue
        writes.append({"range": f"G{number}:K{number}", "values": [values]})
        print(day, values)
    if args.write and writes:
        # gspread qualifies ranges in place; preserve local ranges for readback.
        sheet.batch_update(deepcopy(writes), value_input_option="RAW")
        for item in writes:
            if sheet.get(item["range"], value_render_option="UNFORMATTED_VALUE") != item["values"]:
                raise ValueError(f"Readback failed at {item['range']}")
    if conflicts:
        raise ValueError("Review existing vehicle cells for " + ", ".join(conflicts))
    print(f"{len(writes)} sheet entries {'written' if args.write else 'pending'}")
    return len(writes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare or import completed Car Beam sheet records.")
    parser.add_argument("--credentials", required=True, help="Private Google service-account JSON file")
    parser.add_argument("--write", action="store_true", help="Write and check worksheet rows")
    import_sheet(parser.parse_args())
