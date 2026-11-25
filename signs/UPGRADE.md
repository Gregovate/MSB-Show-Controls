# Upgrade installed 0.2.2 to HA-owned signs 0.3.1

Do not install the superseded chat 0.3.0 manual-wait package. This release is maintained
in Show Controls signs/. It is source-tested, not live park acceptance.

1. Back up the active signs package, app, dashboard and www resource outside active
   directories. Turn Sign Overlays Enabled OFF and stop MSB Sign Bridge.
2. Copy the four files in ha/local_apps/msb_sign_bridge into the existing HA local
   app directory. Preserve app options, MQTT credentials and lighting interface IP.
3. Replace config/packages/signs.yaml with ha/packages/signs.yaml.
   Keep one signs package only. Also replace config/packages/traffic_analytics.yaml with
   ha/packages/traffic_analytics.yaml and add ha/packages/sign2_queue_wait.yaml there.
   These filenames must each exist only once under packages. Do not replace configuration.yaml.
4. Run HA Check configuration. Restart HA only if it passes.
5. Replace config/www/msb-sign-message-grid.js with ha/www/msb-sign-message-grid.js.
   Edit the existing resource URL to /local/msb-sign-message-grid.js?v=7, type Module.
6. Replace the Signs dashboard raw YAML with ha/dashboard/signs-dashboard.yaml and
   Ctrl+F5. Confirm Advertising grid, Message grid and Colors load.
7. If the initializer is visible, press Add operational messages once. It initializes slots 12–17 and retires slot 4;
   existing other slot edits/orders stay intact. A guard prevents later accidental reloads.
   The initializer disappears after setup.
8. Check HA's existing start/end time and extension controls. End time must be the intended
   public cutoff (normally 9 PM); a stale 6 PM test time remains 6 PM until you change it.
   Sign opening date remains Nov 27 independently; no counter season date is written.
9. Update/rebuild the local bridge app to 0.3.1, then start it. Copying source alone does
   not rebuild a running app. Confirm reported version 0.3.1, Connected, Controls Fresh
   and no error, then enable overlays. Old schema-2 snapshots are deliberately rejected.
10. During a sign window, physically check both signs. Wednesday must advertise even if
    the counter's season start is temporarily earlier; Thursday/Friday change automatically.

## HA sources

Tonight/season counts use the established entities directly. No source entry is needed.
Traffic uses sensor.msb_traffic_status without a bridge formula or raw-rate fallback.
The updated analytics package makes public/analytics windows honor the existing extension,
while preserving every original traffic calculation. Signs and analytics use the same
sensor.msb_effective_entry_closing_time.
Weather and explicit admission controls are on the first dashboard tab. Weather is a
real public closure command, not a harmless visual test; do not enable on live signs just
for inspection. Missing/invalid/offline live count/traffic inputs suppress those messages.

Sign 2 queue wait is calculated in the new HA sign2_queue_wait package, not entered by
hand. Add operational messages once also initializes its model parameters once. The
source is sensor.msb_sign2_queue_wait_minutes and slot 14 is Highway-only. Enable the
experimental estimator on Control to publish its results. It starts OFF because its
26.4 ft vehicle pitch and full-segment two-lane assumption are planning approximations,
not measured 2025 calibration. See docs/signs.md for the exact formula and limitations.
Run actual Sign-2-to-entry timing checks before relying on the public number. Counter
outages, stalled loaded traffic or missing inputs suppress the message. No bridge-side
fallback or in-park travel-time substitution exists.
Optional food requires its valid source and enabling slot 17.

## Extensions / admissions

Use the existing show_end_extension_min workflow, which also qualifies the extension
with msb_traffic_extension_date. The sign deadline changes on the next HA snapshot.
Confirm the date is today's show date if a saved extension does not apply. Last night's
extension expires. Coordinate LOR separately using the existing operational procedure.

Automatic never announces Closed simply because the time passes. Select Clearing queue
while accepting the remaining line; it displays ALREADY IN LINE? / YOU MAY ENTER.
Choose Closed only when admissions actually stop. Show Force Close suppresses regular
signs/advertising; Weather closure still overrides with red while master overlays are on.

## Validation / rollback

37 Python tests execute real package Jinja, validate schema 3 and test output behavior.
DOM tests cover grid events/persistence/rollback and palette retention. Run commands in
README.md. Native browser gestures, current HA registry/config validity and physical
outputs still need installation checks. No device firmware or count data is modified.

Rollback: disable overlays and stop bridge; restore backed-up matching package, app,
dashboard and JavaScript, check HA configuration and rebuild the old app. A mixed schema
version must not be left running. All counter season dates and recorded totals remain intact.

For the subsequent daily warm-up and extension update, follow [Daily warm-up and show extensions](../docs/warmup-extension.md).
