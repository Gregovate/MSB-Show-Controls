# Volunteer Trailer sheet reporting from Home Assistant

The Home Assistant automation watches the Car device's ShowSummary MQTT date,
then reads the Car Counter's own seasonal /ShowSummaryBuckets.csv from its
private LAN IP. The firmware publishes its cumulative MQTT summary only after
successfully writing both sheet archives. Cash and sheet-form access are independent.

## Install in the HA configuration directory

1. With the Google Sheets API enabled for the service account's project, place
   its private service account JSON at /config/msb-show-sheets.json on HA.
   Share **MSB 2026 Show Stats** with the JSON's client_email as Editor. Keep the
   key outside the kiosk, the repository, and /config/www. The writer uses only
   the Google Sheets OAuth scope.
2. Copy the entire ha/custom_components/msb_show_sheet directory into
   /config/custom_components/msb_show_sheet. Copy ha/packages/volunteer_vehicle_sheet.yaml
   into /config/packages/volunteer_vehicle_sheet.yaml. This assumes the existing
   Home Assistant configuration includes packages from /config/packages.
3. Check the Home Assistant configuration and restart Home Assistant, then
   open the Settings → Automations entry **Vehicle Sheets - Sync Car Counter**.
   In Developer Tools → Actions, run **msb_show_sheet.sync** with an empty set
   of parameters to perform an actual sheet scan now. Inspect the automation's
   trace or Settings → System → Logs for the error on failure. If the firmware
   has not created its sheet yet, the endpoint may return 404; check the sheet
   endpoint and the device's counter diagnostics after the first qualifying close.

## Season checks

Park Data 2026 G–K hold sheet entries for the four hours ending at 6, 7, 8,
and 9 PM, plus the official daily total minus those four amounts. The last
amount includes the closing allowance. The source's 10PM value starts only
when the gate is extended. Sheet column S should equal the Car sheet's
DailyTotal for the same show date. A scheduled show and a confirmed zero
are distinguished from a closed date, missing sheet, or unreported day.

The subject is msb/traffic/CarCounter/Calendar/showSummary. A scheduled
same-day entry is eligible only when the matching Show sheet is published.
Earlier show dates are checked at startup and at local 1 AM
and noon (use America/Chicago in HA). The process retries missed nights while
the sheet is available on the counter, and handles repeated messages and
same-date source matches without overwriting. If an existing spreadsheet
row disagrees, the service reports the conflict and preserves the row. A missing park
row cannot be reconstructed from the season total.

The sheet filter is for the 2026 sheet and its current kiosk calendar layout.
For a standalone check, park/season-sheet/car_sheet.py remains
the existing command-line entry point when run from a full repository checkout.
