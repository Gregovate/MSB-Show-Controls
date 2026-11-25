# Traffic measurements and their uses

| Entity | Measurement or use |
| --- | --- |
| `sensor.msb_car_counter_enter_cars` | Tonight’s entries and input for the five-minute entry derivative. |
| `sensor.msb_car_counter_show_total_cars` | Season entries displayed in operational sign slot 13. |
| `sensor.msb_gate_counter_exit_cars` | Exit count used by the five-minute exit derivative. |
| `sensor.msb_in_park_cars_canonical` | Occupancy used in HA analytics and the experimental queue model. |
| `sensor.msb_gate_counter_in_park_cars` | Gate-published occupancy for comparison. |
| `sensor.msb_enter_rate_cars_s`, `sensor.msb_exit_rate_cars_s` | Five-minute rates in cars per second. Read with occupancy and camera observations. |
| `sensor.msb_traffic_status` | HA classification used by the sign bridge. |
| `sensor.msb_travel_time_estimate_min` | Estimated travel inside the park. |
| `sensor.msb_sign2_queue_wait_minutes` | Experimental estimate from HWY Sign 2 to CarCounter. Keep disabled until field calibration. |

The HA show/normal bucket sorter in the exported automations monitors `sensor.enter_cars`. That entity ID differs from the canonical sign count source. Verify its live mapping when diagnosing a bucket discrepancy.

[Traffic analytics](../packages/traffic_analytics.yaml) · [Wait estimator](../packages/sign2_queue_wait.yaml)

For the MQTT readings behind these HA entities, consult both device contracts. [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/MQTT_Contract.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/main/docs/MQTT_Contract.md).

To diagnose an unavailable occupancy during public hours, check `sensor.msb_gate_occupancy_session`, `sensor.msb_gate_occupancy_sample_time`, `sensor.msb_gate_occupancy_raw`, and `binary_sensor.msb_gate_counter_online`. The sample time is the Gate RTC time from a heartbeat with integer occupancy. HA checks the sender timestamp so an old retained message cannot become current on reconnect. The freshness limit is 120 seconds with five seconds of forward clock tolerance. An unchanged fresh count can remain valid, including zero or a negative diagnostic balance. After public close, inspect raw counters for equipment health and late exits.
