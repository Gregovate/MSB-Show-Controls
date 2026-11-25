# How the park show controls fit together

| Component | Operating responsibility |
| --- | --- |
| Home Assistant | Stores local schedule helpers, dates the nightly extension, classifies traffic and publishes sign controls. |
| CarCounter | Records arrivals at the food collection area. Its own firmware owns device counts, SD records and scheduled reset handling. |
| GateCounter | Records departures. Its separate start offset and end allowance accommodate the drive through the park. |
| Sign bridge | Consumes the HA control snapshot and renders overlays on Front Entrance and HWY 42. Releasing the overlay returns output to LOR. |
| Light-O-Rama | Runs the show sequences. The captain changes the LOR deadline independently when extending a night. |

For the regular 2026 schedule, warm-up starts at 4:30 PM Central, gates open at 5 PM and public entry ends at 9 PM plus the dated extension. November 27 is the first public opening. December 24 is the scheduled closure. The season ends December 31. Use the sign public start date when configuring pre-opening advertising. Changing the counter season date can affect season totals.

[Install files](../ha/README.md) · [Captain runbook](operator_runbook.md) · [Timing diagram](../design/show_timing_state_machine.md) · [Traffic flow](../design/traffic_flow_diagrams.md)
