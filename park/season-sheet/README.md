# Volunteer Trailer sheet reporting from Home Assistant

The Home Assistant automation watches the Car device's ShowSummary MQTT date,
then reads the Car Counter's own seasonal /ShowSummaryBuckets.csv from its
private LAN IP. The firmware publishes its cumulative MQTT summary only after
successfully writing both sheet archives. Cash and sheet-form access are independent.

## Install in the HA configuration directory

Create the private data directory `/config/msb_show_sheet/` on HA. Existing root-level credentials remain supported.

1. For the MSB shared drive, use an internal Workspace OAuth desktop client
   in the **MSB Show Controls** Cloud project. Enable Google Sheets API,
   configure Google Auth Platform with Internal audience, and create a client of
   type **Desktop app**. Download its client JSON privately on the laptop.
   From the repo root on Windows, run:

   ```powershell
   py -m pip install google-auth-oauthlib
   py park/season-sheet/authorize_workspace.py "$HOME/Downloads/desktop-client.json" "$HOME/Downloads/msb-show-sheets.json"
   ```

   Substitute the actual downloaded client filename. Sign in with an MSB
   account that can edit the rehearsal workbook. Copy the resulting
   msb-show-sheets.json privately to /config/msb_show_sheet/msb-show-sheets.json on HA.
   This file contains a refresh token. Keep both files outside Git and www.
   The uploader uses the Sheets scope and the configured workbook ID.

   For installations that permit a service account, with the Google Sheets API enabled for the service account's project, place
   its private service account JSON at /config/msb_show_sheet/msb-show-sheets.json on HA.
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
and 9 PM, plus After9PM, including the closing allowance. For legacy sheets the importer
recovers that last amount from DailyTotal minus the four period counts.
It rejects cumulative CSVs and inconsistent new totals. Sheet column S should equal the Car sheet's
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

## Pre-opening rehearsal on HA

1. Make a **separate copy** of the workbook. Grant the chosen uploader identity Editor access to that copy and retain the tab name `Park Data 2026`. In the copy only, set
   B3 and B4 to real dates November 24 and 25, 2026. Clear D3:D4 and G3:K4.
   Verify those dates occur only once and the rows are open.
2. **Before the first HA restart**, replace the package's `msb_show_sheet: {}`
   line with the configuration below, using the copy's ID (between /d/ and
   /edit in its URL). In the same package, change the MQTT trigger topic to
   `msb/rehearsal/CarCounter/Calendar/showSummary`. Leave this configuration in
   place for the entire test. The importer rejects the production workbook ID
   with a rehearsal file. The service account can be dedicated to the copy.

   ```yaml
   msb_show_sheet:
     rehearsal_workbook: "YOUR_COPY_ID"
   ```
3. Create an initially **header-only** /config/msb_show_sheet/msb-rehearsal-buckets.csv using
   the first line of rehearsal/initial.csv. Install the component and edited
   package, check configuration and restart HA. Startup should write zero rows.
4. Copy the entire rehearsal/initial.csv over /config/msb_show_sheet/msb-rehearsal-buckets.csv.
   Publish the payload below to the **rehearsal topic** with retain disabled.
   Verify the automation trace took the closing branch. In the copy, G3:K3
   should read **2, 3, 5, 7, 11** (28 cars) and D3 should read **30.8**.

   ```text
   2026-11-24,1,0,2,5,10,17,28,30.8
   ```
5. Replace the fixture with rehearsal/catch-up.csv and restart HA **without
   publishing another message**. The startup trace should show the setup
   trigger. G4:K4 should now read **13, 0, 17, 19, 23** (72 cars) and D4
   should stay blank. Run msb_show_sheet.sync again: expect zero writes.
6. When ready for production, restore the repository's original package and
   restart HA. This enables production writes from the real counter. The
   preseason fixture dates are absent from the live show schedule.
