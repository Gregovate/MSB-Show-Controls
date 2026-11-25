# Signs: source contract and durable handoff

Owner: MSB Show Controls. Corrected 2026-11-24, Central Time. Source release 0.3.1.

## Ownership

Car firmware counts entry events; Gate firmware counts exits and publishes occupancy.
Home Assistant owns operational calculations. The sign bridge must not reimplement
traffic bands, invent an estimated wait, or maintain an independent closing time.
It renders HA's resolved schema-3 snapshot, expires stale snapshots and releases sACN
when settings are stale, invalid or disabled. Counts and historical records are read-only.

Reviewed sources:
- Car/Gate docs/MQTT_Contract.md and docs/Coordinated_Release_9.md on their
  engineering/ota-safe-journal-20261123 branches.
- Gate System_Documentation/Engineering/MQTT_HA_Contract.md on
  docs/traffic-counter-assessment.
- traffic_analytics.yaml supplied in this conversation on Nov 24, 2026, reviewed completely.
  The earlier Library copy agrees on the relevant formulas. The supplied file is now
  maintained at ha/packages/traffic_analytics.yaml with only the operating windows changed.
- Show Controls docs/show_times_and_windows.md. Older placeholder exports and the
  initial reset skeleton do not supersede implemented firmware/HA contracts.

## Exact inputs

| Purpose | Source |
|---|---|
| Tonight entry total | sensor.msb_car_counter_enter_cars |
| Cumulative season entry total | sensor.msb_car_counter_show_total_cars |
| Existing calculated traffic status | sensor.msb_traffic_status |
| Existing traffic detail | sensor.msb_traffic_status_snapshot, upstream HA context |
| Published in-park count | sensor.msb_gate_counter_in_park_cars |
| Nominal public hours | input_datetime.msb_show_start_time / msb_show_end_time |
| Extension minutes | input_number.show_end_extension_min |
| Extension date | input_text.msb_traffic_extension_date, YYYYMMDD |
| Sign advertising opening date | input_datetime.msb_signs_public_start_date |
| End/down dates | input_datetime.msb_show_end_date / msb_show_down_date |
| Counter online guards | binary_sensor.msb_car_counter_online / msb_gate_counter_online |
| Queue wait | sensor.msb_sign2_queue_wait_minutes, calculated in ha/packages/sign2_queue_wait.yaml |
| Optional food pounds | HA sensor named by input_text.msb_signs_food_entity |

Sign opening date stays separate from input_datetime.msb_show_start_date because Greg
must not reset counter season totals while finishing pre-show sign testing. No sign
script writes the counter season date. Sign end/start TIMES use the existing HA controls;
the duplicate sign-only time helpers from the uninstalled 0.3.0 proposal are retired.

sensor.msb_effective_entry_closing_time computes the shared effective closing instant from nominal end plus extension ONLY when
extension_date matches that operating day. Last night's extension must not carry forward.
Overnight windows and previous-day extensions are handled in the HA template. Public
admission cutoff is not the firmware's later official-counting cutoff or LOR playback stop.
Changing an extension does not reset any counts. LOR extensions remain a separately
coordinated operational action; this app does not change LOR's schedule.

## Highway Sign 2 and the new experimental HA estimator

Distances measured from bridge, feet:

| Point | Distance |
|---|---:|
| Bridge | 0 |
| 15-minute sign | 797 |
| Highway Sign 2 visibility edge | 1445 |
| Highway Sign 2 | 1791 |
| Sign 1 visibility boundary | 1890 |
| Sign 1 midpoint | 2021 |
| Drive end | 2060 |
| Gate leaves | 2165 |
| Car counter | 2598 |

Sign 2 to Car Counter = 807 ft. The requested wait applies to a guest at highway Sign 2,
not the queue tail or time already inside the park. Slot 14 is enforced to HWY 42 even
if its grid target is accidentally changed to Both. No new controller/universe is added.

The supplied package has sensor.msb_travel_time_estimate_min, calculated from
in-park occupancy / exit rate with low-load and bounded fallback rules. That is an
IN-PARK TRAVEL estimate. It is NOT the Sign-2-to-entry queue wait. Greg confirmed the
queue estimator had not been built yet. This release adds that missing HA model in
ha/packages/sign2_queue_wait.yaml; it does not rename the in-park estimate.

### Model and limits

This is an experimental planning estimate, not measured queue tracking. It is OFF until
Enable experimental HA Sign 2 wait estimate is enabled. Initialize the two planning
parameters once with the operational-message action; later calibration values restore
across restarts rather than resetting to defaults.

- Vehicle pitch initially 26.4 ft (the earlier approximate 100 vehicles per half-mile),
  not a 2025 measured queue-spacing calibration.
- Free-flow speed initially 5 mph, giving 807/(5*88) = 1.83 minutes, rounded to 2.
- Equivalent queued vehicles = ceil(807 * lanes / pitch): 31 in one lane, 62 in two.
  lane_2_open supplies lane state. Two lanes across the full segment is an upper-biased
  capacity assumption because the actual split location was not supplied. This is
  deliberately documented rather than claimed as surveyed two-lane geometry.
- Existing five-minute HA derivative entry/exit rates supply throughput. With at least
  120 cars in park and net growth, use the lower entry/exit rate to reflect downstream
  congestion; otherwise use entry rate. Thus entries alone are not the congestion signal.
- HA traffic status light with in-park load under 80 returns the 2-minute free-flow value;
  other valid states use ceil(max(free-flow time, equivalent queued vehicles/service rate)).
- Missing/offline inputs, missing lane state, no measured entry flow, closed hours, or
  a loaded park with no departure flow suppress the result. No arbitrary finite wait
  is fabricated for a stalled loaded park.

At 5 cars/min in moderate traffic this model gives 7 minutes for one lane or 13 for two.
At 150 cars in park, 5 entries/min and 2 exits/min, the one-lane result is 16 minutes.
These are TEST SCENARIOS, not observed wait measurements. Counts cannot establish
whether the queue actually reaches Sign 2 or fills the whole segment. The model assumes
that segment is queued in non-light conditions. Light arrivals or a localized food-area
blockage can violate that assumption. Validate actual Sign-2-to-entry elapsed times
before treating the output as calibrated public advice. Adjust planning parameters only
from field evidence; do not modify official history to fit the model.

### Extension correction to supplied analytics

The uploaded msb_show_open and analytics-window templates used nominal closing time
without show_end_extension_min. They now consume one HA effective-closing sensor,
including its public_start attribute. Existing season guard, analytics start/tail
cushions and each sensor identity are preserved. Every pre-existing traffic sensor's
complete definition is checked against a hash of the supplied version; no congestion
threshold, travel-time formula, lane advisory or count formula was changed. The bridge
reads that same HA effective-closing sensor rather than calculating another deadline.

Historical reference: Car docs/Traffic_Reliability_20261122.md links 2025 EnterLog.csv
SHA256 78573bcf3e0843f4b97779636742b294e262f6c9341a8985d723eaa134fbe489,
19,626 accepted events Dec 5–31, and documents timestamp/interval limitations. Those
records are not proof of a calibrated highway queue wait. Preserve official 2025 summaries.

## Controller/output mapping

| Sign | Controller | Universes |
|---|---|---|
| Front Entrance | 10.10.5.20 | 340–355 |
| HWY 42 | 10.10.5.21 | 357–372 |

HA lighting interface bind address is an app option (previously 10.10.5.4). Matrix is
80x34, 2720 pixels, 16 outputs x170, GRB, with existing tested top-half reversal.
Overlay priority remains 150. MQTT base is msb/signs/bridge. Preserve local credentials.

## Message/state rules

| Slot | Purpose | Gate/availability |
|---|---|---|
| 1–3 | Old Run/Walk promotion | Existing expiry and enable state |
| 4 | Retired duplicate gate-hours message | Disabled by one-time operations action |
| 5 | TRAFFIC / HA status | Public hours, valid HA result and counters online |
| 6 | THANK YOU / FOR VISITING | Existing operator assignment |
| 7 | Retired duplicate opening announcement | Suppressed; identity retained |
| 8–11 | Advertising | Date-specific announcement in slot 9 |
| 12 | TRAFFIC TONIGHT / x CARS | Public operation and valid Car count |
| 13 | TRAFFIC SEASON / y CARS | Public operation and valid Car season count |
| 14 | EST WAIT TIME / x MIN | Highway ONLY, verified HA queue source |
| 15 | ALREADY IN LINE? / YOU MAY ENTER | Explicit Clearing queue selection |
| 16 | ENTRY CLOSES / effective end | Public operation; hidden when Clearing queue |
| 17 | FOOD COLLECTED / x LBS | Optional valid HA source; disabled by default |

Automatic follows sign opening date and HA operating hours. Reaching cutoff NEVER
creates a CLOSED announcement. Clearing queue continues acceptance wording while
remaining guests enter; Closed is an explicit captain choice for ENTRY CLOSED / THANK YOU.
No physical gate-position inference or commands are introduced. Admission state returns
to Automatic on HA restart; weather closure persists and must be deliberately cleared.

Weather switch takes priority over all normal rotations on BOTH signs: CLOSED / WEATHER,
red background. It bypasses Show Force Close and ad hours, but master overlays OFF or
stopping the bridge always releases to LOR. Weather/explicit closure interrupt an active
LOR interval on the next fresh HA snapshot. They do not rotate normal messages in between.

Thursday Nov 26: OPEN TOMORROW / actual HA opening time. Friday Nov 27 before opening:
OPEN TONIGHT followed by GATES OPEN / actual opening time. Advertising windows remain
editable. The bridge does not assume 5 PM after HA's time is changed.

## UI and testing handoff

Both Advertising and Message tabs use the shared custom grid. Advertising exposes slots
8–11 only; reorder on the full grid. Drag/pointer, arrows and keyboard movement preserve
stable slot IDs while writing consecutive order values. RGB previews boost display
brightness without changing raw pixel values. Colors tab edits the existing six palette
helpers. No HACS dependencies are required for these custom cards.

Browser resource: /local/msb-sign-message-grid.js?v=7, JavaScript Module. The resource
must be registered; accessible JavaScript bytes alone do not load a custom card.
Full source, package regeneration and tests are in signs/. Restore that source rather
than an old chat ZIP. See signs/UPGRADE.md for coordinated installation/rollback.

Trace the entry, exit and hourly data behind HA traffic displays in the firmware MQTT contracts. [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/0b7e9787bc6d475d17b4874b5c32096103d4c40e/docs/MQTT_Contract.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/0874ed3726824448c6ce334fe5765ac7c55a84f5/docs/MQTT_Contract.md).
