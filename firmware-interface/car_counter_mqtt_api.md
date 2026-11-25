# CarCounter MQTT operating contract

CarCounter records entrances. HA publishes the retained `msb/traffic/CarCounter/Config/operatingSettings` transaction using the following comma-separated field order.

| Positions | Values |
| --- | --- |
| 1–3 | Protocol version 1, public start minute, nominal end minute |
| 4–5 | Start/reset offset from `input_number.carcounter_start_offset_min`, end offset from `input_number.carcounter_end_offset_min` |
| 6–7 | Extension minutes for the current operating date, local issue date YYYYMMDD |
| 8–9 | `input_number.enter_stuck_timeout_s` converted from seconds to milliseconds, then `input_number.enter_cardetectms` in milliseconds |
| 10–12 | Season end YYYYMMDD, down date YYYYMMDD, current year |

The season-start date travels separately on `Config/showStartDate`. During an extension, check `State/extensionMinutes`, `State/countEndMinute` and `System/settingsHealth` under the device prefix. A retained HA request alone does not establish acceptance by the ESP32.

[HA settings publisher](../ha/automations.yaml) · [Firmware settings implementation](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/src/services/OperatingSettings.cpp) · [Diagnostic topics](expected_topics.md)

## Matching firmware documentation

| Question | Device reference |
| --- | --- |
| Which counts, hourly snapshots and health topics can HA consume? | [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/MQTT_Contract.md) |
| Which HA settings does this firmware consume and acknowledge? | [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/Coordinated_Release_9.md) |
| How are counts restored after a restart? | [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/Count_Persistence.md) |
