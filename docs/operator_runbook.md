# Park captain show-night runbook

| When | What to check or do |
| --- | --- |
| Before warm-up | Confirm the local date, radio ON time, gates-open time, nominal close and tonight’s extension. A 6 PM close from testing needs correction for a normal 9 PM night. Check Force Close and weather closure against the actual park decision. |
| At 4:30 PM | On a scheduled night, verify radio, marquee and car-counter arches. With overlays enabled and slot 9 set to Both / Pre-show, look for GATES OPEN IN on both signs. Traffic resets follow the public opening anchor and configured counter offsets. |
| At 5 PM | Check public-open state, fresh bridge controls and operational rotation. Compare entrances and exits against the camera views. Departures naturally lag arrivals. |
| Before extending | Use both highway camera views and in-park occupancy. Enter the extra minutes before cutoff, check the displayed entry deadline and adjust LOR separately. Confirm both counters report the extension and their effective end minutes. |
| Clearing the line | Select Clearing queue while guests already in line may enter. The signs show ALREADY IN LINE? / YOU MAY ENTER. Select Closed when admission actually stops. |
| Weather closure | The weather switch commands both signs to show CLOSED / WEATHER while master overlays are enabled. Clear it deliberately when the weather closure ends. |
| End of night | Verify radio and projector shutoffs against their individual extended times. At local midnight the extension clears. Keep the counter records for reconciliation. |

**If both signs are blank or showing LOR**, read Sign Schedule, Bridge Online, Controls Fresh, Sign Bridge Error and each sign’s activity. A connected bridge can legitimately release both signs during Force Close or outside eligible hours. Verify the intended admission decision before changing Force Close.

**If a counter fails**, record the local time, last credible total, device identity and storage warning. Check heartbeat and the device’s persistence/export health. Use the cameras for traffic decisions while diagnosing. A stale total or unavailable highway wait estimate is insufficient evidence for a count correction. Preserve SD logs and reconcile actual arrivals or departures before considering a manual correction.

[Extension procedure](warmup-extension.md) · [Counter diagnostics](../firmware-interface/expected_topics.md) · [Sign behavior](signs.md)

When verifying an extension, use the device acceptance procedure for each counter. [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/Coordinated_Release_9.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/main/docs/Coordinated_Release_9.md).

[Three-repository main baseline and opening-night checks](friday-system-check.md).
