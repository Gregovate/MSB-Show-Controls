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

The Car Counter supplies entrance data and the Gate Counter supplies exit data. Both consume HA operating settings and report what they applied. Follow the [two-way MQTT interface](../firmware-interface/expected_topics.md#follow-a-transaction-across-repositories) or go directly to the firmware MQTT contracts: [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/0b7e9787bc6d475d17b4874b5c32096103d4c40e/docs/MQTT_Contract.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/0874ed3726824448c6ce334fe5765ac7c55a84f5/docs/MQTT_Contract.md).
