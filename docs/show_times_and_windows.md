# Show traffic windows and hourly comparisons

Authority: MSB Show Controls. Operational requirements clarified by Greg on 2026-11-05.
This document governs entrance/exit comparison and scheduled show resets. It supersedes conflicting initial-skeleton assumptions in traffic_reset_system.md.

## Why the counters reset at different times

Public gates normally open at 5:00 PM. The route is approximately 1.1 miles and the speed limit is 5 mph. At a continuous 5 mph, travel takes 13 minutes 12 seconds; the first visitor entering at 5:00 PM would nominally reach the exit around 5:13 PM.

Operations volunteers park near the exit to open the gates and then leave through the Gate Counter. Their departures should not inflate the show's visitor exit total. The Gate Counter therefore deliberately resets its show daily count after opening, after those departures and before the expected first visitor exits. The entrance counter resets before visitor admission.

The HA administration screenshot supplied on November 4 shows entrance reset offset -1 minute (4:59 PM) and gate reset offset +10 minutes (5:10 PM), relative to a 5:00 PM opening. These are observed settings, not proof that both deployed devices honor them. Greg earlier described a 4:55 PM entrance reset; reconcile the intended entrance offset with HA before changing configuration. Do not substitute the theoretical 13-minute trip for the chosen gate reset offset.

## Congestion and occupancy

The 13-minute trip is a free-flow baseline, not a fixed travel time or a deadline for exits. On very busy nights traffic can slow substantially or stall. Greg reports occupancy reaching approximately 270 cars at once. This is an operational observation, not a configured capacity limit or an alarm threshold.

Greg has exact analysis from the 2025 season, previously reviewed with him. Those measured results must be linked and verified before quoting detailed travel-time distributions, throughput, or peak occupancy as independently established findings. Do not replace those measurements with this theoretical calculation.

Greg also reports practical entrance throughput of approximately **300 cars/hour** through the food collection area and Car Counter. This is about 5 cars/minute, or one car every 12 seconds on average; it is not a detector debounce setting or a guaranteed sustained rate.

For scale only: at a sustained 300 cars/hour and steady occupancy of 270 cars, Little's Law gives an average time in the park of approximately 54 minutes (270 / 300 hours). The reported maximum occupancy and approximate entrance capacity have not been shown to occur simultaneously under steady conditions. Therefore 54 minutes is an illustrative calculation, not a measured 2025 travel time. Actual congestion analysis must use time-aligned entry, exit and occupancy records.

## Interpreting hourly buckets

The objective is a reasonable comparison of visitor entry and exit volumes over the evening, not forced equality in each clock hour.

- Even in free flow, late-hour entries commonly exit in the following hour.
- During congestion, exits can lag entries by much longer; vehicles can remain in the park across several reporting boundaries.
- A positive cumulative entry-minus-exit balance can represent real park occupancy. Do not reset or adjust counts merely to make hourly buckets match.
- With aligned visitor-counting windows, occupancy change over an interval is entries minus exits. Absolute occupancy also requires a valid starting baseline and healthy counters.
- Compare the complete visitor cohort after its final exits, not merely at admission closing time. Investigate remaining differences using recorded events, resets and device health.
- Volunteer and other operational movements require explicit treatment; the delayed gate reset establishes the intended visitor baseline but does not repair missing detector events.

## Preserve both kinds of traffic data

All-day hourly traffic supports year-round park analysis, including off-season operation. Show visitor buckets support official nightly and year-to-year comparisons. Excluding volunteer departures from show metrics must not erase their legitimate all-day traffic records.

The official 2025 ShowSummary / ShowSummaryBuckets records remain authoritative, including prior operational corrections. Do not reconstruct or overwrite that season from raw logs. Recording paths follow the validated current calendar year; a stale show date must never redirect writes into the previous year's folder.

HA owns operational configuration, while firmware must retain validated settings and operate from the RTC without MQTT or Wi-Fi. Scheduled show resets and calendar rollovers must be distinct from reboot recovery: a restart must restore counts, not create another reset.

## Implementation gaps observed in modular-test.5 / .6

These findings describe source behavior, not completion of the design:

| Area | Observed behavior | Required reconciliation |
| --- | --- | --- |
| Entrance show reset | Uses showStartMin minus 1 minute | Match the agreed HA-controlled offset and persist it for offline use |
| Gate show reset | Hard-coded 17:08; nearby comment describes 17:10 | Use the agreed show-relative HA offset, with validated persisted fallback |
| Show daily reset | resetCountsForShow resets totalDailyCars and records the reset date; it does not clear hourlyCount | Define and verify separate show-window bucket treatment while preserving all-day hourly traffic |
| Hourly comparison | A daily counter reset alone does not remove earlier events from all-day hourly CSVs | Verify summary inputs and window boundaries before claiming volunteers are excluded from official hourly buckets |

Documentation of the +10-minute gate offset does not change the deployed 17:08 implementation. No device settings or timing were changed by this document.

## Acceptance evidence required

Use setup traffic and controlled events to verify volunteer exclusion, correct visitor totals, preservation of all-day hourly events, and no duplicate reset after reboot. Test hour-boundary travel and prolonged congestion without treating legitimate count differences as faults. Verify HA configuration and offline fallback produce the same agreed timing on both devices.

Record firmware versions, effective configuration, full dates, reset events, detector health and the resulting files. Keep historical official metrics unchanged.

