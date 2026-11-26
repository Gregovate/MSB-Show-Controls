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
import io
from datetime import date, datetime
from urllib.request import urlopen
from zoneinfo import ZoneInfo

BOOK = "1mcr-l7yX5TYO5tNqYIZwlm0_5AZgAX36NpHxjfmq5MQ"
SOURCE = "http://192.168.3.31/ShowSummaryBuckets.csv"
HOURS = ["6PM", "7PM", "8PM", "9PM"]
COLUMNS = ["Cars 5:00-6:00", "Cars 6:00-7:00", "Cars 7:00-8:00",
           "Cars 8:00-9:00", "Cars After 9 PM"]


def entries(data, scheduled, today):
    # Source is the incremental sheet. The other sheet has a similar name
    # and cumulative counts; its header must never pass this check.
    data = csv.DictReader(io.StringIO(data))
    if not set(["Date", "DailyTotal", *HOURS]).issubset(data.fieldnames or []):
        raise ValueError("Expected the Car Counter's ShowSummaryBuckets.csv")
    found = {}
    for record in data:
        day = date.fromisoformat(record["Date"])
        if day not in scheduled or day >= today:
            continue
        if day in found:
            raise ValueError(f"Duplicate source date {day}")
        nums = [int(record[k]) for k in HOURS]
        late = int(record["DailyTotal"]) - sum(nums)
        if min([late, *nums]) < 0:
            raise ValueError(f"Invalid vehicle count for {day}")
        found[day] = nums + [late]
    return found


def import_sheet(args):
    import gspread
    sheet = gspread.service_account(filename=args.credentials).open_by_key(BOOK).worksheet("Park Data 2026")
    header = sheet.get("G2:K2")[0]
    if [s.strip() for s in header] != COLUMNS:
        raise ValueError("Sheet layout changed; refusing to write")
    # Use sheet-local calendar serials; never parse locale-dependent cash or dates.
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
    with urlopen(SOURCE, timeout=15) as response:
        data = response.read(65537)
    if len(data) > 65536:
        raise ValueError("Unexpectedly large car sheet")
    source = entries(data.decode("utf-8-sig"), schedule, datetime.now(ZoneInfo("America/Chicago")).date())
    writes = []
    for day, values in sorted(source.items()):
        ix = schedule[day]
        existing = list(formulas[ix]) if ix < len(formulas) else []
        existing.extend([""] * (5-len(existing)))
        if existing == values:
            continue
        if any(v is not None and v != "" for v in existing):
            raise ValueError(f"{day}: car cells already populated or contain formulas; review before recalculating")
        number = ix + 3
        writes.append({"range": f"G{number}:K{number}", "values": [values]})
        print(day, values)
    if args.write and writes:
        sheet.batch_update(writes, value_input_option="RAW")
        for item in writes:
            if sheet.get(item["range"], value_render_option="UNFORMATTED_VALUE") != item["values"]:
                raise ValueError(f"Readback failed at {item['range']}")
    print(f"{len(writes)} vehicle rows {'written' if args.write else 'pending'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare or import completed Car Beam sheet records.")
    parser.add_argument("--credentials", required=True, help="Private Google service-account JSON file")
    parser.add_argument("--write", action="store_true", help="Write and check worksheet rows")
    import_sheet(parser.parse_args())
