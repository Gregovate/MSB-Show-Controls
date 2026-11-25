# MQTT topics used by show controls

For counter topics below, replace `<device>` with exactly `CarCounter` or `GateCounter`. The prefix is `msb/traffic/<device>/`. Topic names are case sensitive.

| Suffix | Direction | Meaning |
| --- | --- | --- |
| `System/hello` | Device → HA | Triggers republication of that device’s settings. |
| `Config/operatingSettings` | HA → device | Retained QoS 1 schedule and tuning transaction. |
| `Config/showStartDate` | HA → device | Retained season-start configuration. A change can affect season records. |
| `State/resetMinute`, `State/countStartMinute`, `State/countEndMinute`, `State/extensionMinutes` | Device → operator | Reported reset, count window and applied extension. Minute-of-day 1260 means 9 PM. |
| `System/settingsHealth`, `System/countPersistence`, `System/hourlyExport`, `System/summaryExport`, `System/sd/health` | Device → HA | Settings acceptance and storage/export diagnostics. |
| `Config/countCorrection` | HA → device | Guarded daily or show-total correction. HA uses QoS 0 with retain off. |

Signs use the separate prefix `msb/signs/bridge/`. HA publishes `control` and can request `release`. The bridge publishes `availability` and `state`, which supply the dashboard’s online, freshness and activity readings.

[Car contract](car_counter_mqtt_api.md) · [Gate contract](gate_counter_mqtt_api.md) · [HA publishers](../ha/automations.yaml)

## Follow a transaction across repositories

| Direction | What crosses MQTT | Firmware documentation |
| --- | --- | --- |
| Counters → HA | Entrance and exit counts, hourly snapshots, availability and health feed traffic analytics and sign eligibility. | [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/0b7e9787bc6d475d17b4874b5c32096103d4c40e/docs/MQTT_Contract.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/0874ed3726824448c6ce334fe5765ac7c55a84f5/docs/MQTT_Contract.md) |
| HA → counters | HA publishes the operating schedule, per-device offsets, dated extension and detector settings. Each device validates the transaction. | [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/0b7e9787bc6d475d17b4874b5c32096103d4c40e/docs/Coordinated_Release_9.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/0874ed3726824448c6ce334fe5765ac7c55a84f5/docs/Coordinated_Release_9.md) |
| Counters → HA after a command | Read each device’s applied state and settings health to verify its effective window. A retained request alone cannot confirm acceptance. | [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/0b7e9787bc6d475d17b4874b5c32096103d4c40e/docs/Configuration_Ownership.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/0874ed3726824448c6ce334fe5765ac7c55a84f5/docs/Configuration_Ownership.md) |
| Device storage → recovery evidence | A count can reach MQTT before its SD checkpoint completes. Check persistence diagnostics when reconciling a reboot or outage. | [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/0b7e9787bc6d475d17b4874b5c32096103d4c40e/docs/Traffic_Reliability_20261122.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/0874ed3726824448c6ce334fe5765ac7c55a84f5/docs/Traffic_Reliability_20261122.md) |

Links identify the firmware documentation revisions used for this interface reference. For park acceptance, record the firmware version each device actually reports.

[Three-repository main baseline and opening-night checks](../docs/friday-system-check.md).
