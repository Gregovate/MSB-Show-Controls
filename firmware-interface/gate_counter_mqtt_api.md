# GateCounter MQTT operating contract

GateCounter records departures. HA publishes the retained `msb/traffic/GateCounter/Config/operatingSettings` transaction using the following comma-separated field order.

| Positions | Values |
| --- | --- |
| 1–3 | Protocol version 1, public start minute, nominal end minute |
| 4–5 | Start/reset offset from `input_number.gatecounter_start_offset_min`, end offset from `input_number.gatecounter_show_end_offset_min` |
| 6–7 | Extension minutes for the current operating date, local issue date YYYYMMDD |
| 8–9 | `input_number.gate_stuck_timeout_s` converted from seconds to milliseconds, then `input_number.exit_cardetectms` in milliseconds |
| 10–12 | Season end YYYYMMDD, down date YYYYMMDD, current year |

The season-start date travels separately on `Config/showStartDate`. During an extension, check `State/extensionMinutes`, `State/countEndMinute` and `System/settingsHealth` under the device prefix. A retained HA request alone does not establish acceptance by the ESP32.

[HA settings publisher](../ha/automations.yaml) · [Firmware settings implementation](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/refactor/shared-firmware/src/services/OperatingSettings.cpp) · [Diagnostic topics](expected_topics.md)
