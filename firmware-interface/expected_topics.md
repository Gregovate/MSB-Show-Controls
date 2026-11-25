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
