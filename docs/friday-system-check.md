# Opening-night integration check · Friday, November 27, 2026

Use `main` on the laptop and show PC in all three repositories. The November 24 paired firmware source is Car .31 and Gate .24. Production testing of the reliability changes has been limited. Record actual installed versions, local times, observations and any gaps. Field result: pending.

At 11:26 AM Central on November 24, the devices reported Car `25.12.03.2-modular-test.31` and Gate `25.12.28.0-modular-test.24`. Both reported `productionSession=TEST`, the November 22 test calendar, journal and archive health OK, and zero dropped beam edges. Car reported one unassigned recovery event, Gate zero. This establishes the installed test baseline. Friday production acceptance is pending.

The test schedule closed Car at 6:10 PM and Gate at 6:25 PM. Recheck Friday’s actual HA settings against the production deadlines below.

| Stage (Central) | Evidence to compare |
| --- | --- |
| Before admission | Read each device’s reported firmware, local clock, production session, journal and archive health. Follow the device cutover procedure for READY and the verified baseline. A first real passage changes that baseline. Never reset counts to recreate the check. |
| Settings handshake | Compare HA’s opening, offsets, close and dated extension with each device’s applied State values. For 5–9 PM, zero extension and the documented offsets, Car reset/start/end are 1019/1020/1260. Gate reports 1030/1030/1285. |
| Warm-up and first arrivals | Confirm the 4:30 PM radio and countdown. Observe a real entrance after 5 PM and compare Car telemetry, HA entries and the dated occupancy balance. Observe a departure inside Gate’s delayed window and compare Gate and HA. |
| During operation | Compare camera observations with counts, recording health and HA trends. If an extension is actually needed, verify both devices’ applied deadlines, the sign wording and the separate LOR change. |
| After cutoff and Gate grace | Compare local-date entries, exits, hourly buckets, final balance and storage health with the devices’ hourly reports. Record missing evidence or unexplained differences explicitly. |

Car supplies dated official entries to Gate. Gate pairs them with same-date exits and can report unknown occupancy if its Car input is stale. The maintained HA analytics package marks missing Gate occupancy unavailable. A numeric zero or signed balance remains visible. Verify this on park HA after installing the package.

[Car operating contract](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/OPERATING_CONTRACT.md) · [Gate operating contract](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/main/docs/OPERATING_CONTRACT.md) · [Car cutover](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/Production_Cutover_20261124.md) · [Gate cutover](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/main/docs/Production_Cutover_20261124.md)

## Firmware Refactoring Analysis Part 2

Begin each session from the current remote main heads. Greg compiles locally and flashes the devices. Git publication, a reported install and field acceptance are separate milestones. The two existing firmware checkpoints carry this same branch handoff.

[Car thread checkpoint](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/Checkpoint_2026-11-24_Part_2.md) · [Gate thread checkpoint](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/main/docs/Checkpoint_2026-11-24_Part_2.md)

At the 4:59 PM reset, official occupancy stays unavailable. The captain kiosk can still show a fresh Gate check. Verify the first fresh Gate production reading after public opening, a real zero during operation, and unavailable again at the extended public close even while Gate records its grace period.

For an off-hours test, read the Gate check on the Cars in park card. A fresh value is Gate’s own computed balance and may be zero or negative. In TEST mode Gate uses its cached Car total. Observe a known entrance change with exits steady and confirm the corresponding change at Gate. A steady TEST balance alone verifies only Gate reporting to HA. With both counters on 26.11.27.2, Gate uses fresh same-date live entries for off-hours equipment checks. During the show and through the Gate recording cutoff it uses official entries and official exits. A qualified daytime passage increments the live daily count and its Cars/hour/HH MQTT bucket and exercises the Car arches. Official totals and event logs advance only during the device recording window. Use the diagnostic for equipment verification only.
