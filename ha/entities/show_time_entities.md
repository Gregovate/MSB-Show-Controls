# Schedule controls and derived times

| HA entity | Operator meaning |
| --- | --- |
| `input_datetime.production_radio_on` | Radio, marquee and arches on time. Also starts the sign countdown on eligible show nights. |
| `input_datetime.msb_show_start_time` | Public opening and reference for counter timing offsets. |
| `input_datetime.msb_show_end_time` | Nominal public deadline before extension. |
| `input_number.show_end_extension_min` | Extra minutes for tonight. HA records the operating date in `input_text.msb_traffic_extension_date`. |
| `sensor.msb_effective_entry_closing_time` | Date-qualified closing timestamp consumed by signs and traffic windows. Its `public_start` attribute supplies the start timestamp. |
| `binary_sensor.msb_show_open` | Published public window constrained by show season and Force Close. |
| `input_datetime.production_radio_off`, `input_datetime.production_projector_off`, `input_datetime.production_projector_off_safety` | Independent nominal equipment deadlines. Each receives the dated extension. |
| `input_datetime.msb_signs_public_start_date` | First public sign opening. Keep separate from the firmware season-start helper. |
| `input_select.msb_signs_admission_state` | Automatic, Clearing queue or Closed. The separate weather switch controls the exclusive closure message. |

[Production automations](../automations.yaml) · [Sign package](../packages/signs.yaml) · [Traffic windows](../packages/traffic_analytics.yaml)
