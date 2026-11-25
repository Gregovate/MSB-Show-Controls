# Counter settings, buckets and corrections

**Settings distribution.** Apply CarCounter settings and Apply GateCounter settings publish validated settings at HA startup, on relevant helper changes, device hello and every five minutes. Each device receives its own offsets and detector timing. A dated extension changes the end of its operating window. Confirm the returned device state and settings health after an edit.

**HA buckets.** Sort traffic into show/normal buckets computes the positive difference between numeric old and new readings from `sensor.enter_cars`. It adds that difference to the show or normal helper according to `binary_sensor.msb_show_open`. Counter decreases contribute zero. These helpers are separate from firmware hourly exports.

**Manual corrections.** The four Reset Enter/Exit Daily/Show Total automations watch numeric override helpers. The checked-in actions publish a non-retained correction when the matching permission helper is on and both old and new values are numeric. Check the matching device, daily versus season scope and supporting evidence before touching an override. The live YAML does not implement a separate confirmation button.

**Storage warnings.** HA subscribes to count persistence, hourly export, summary export, settings health and SD health for each device. Use the warning topic and payload to distinguish recording problems from an offline device.

[Automation source](../automations.yaml) · [Reset decisions](../../design/reset_flow_diagram.md) · [Topic reference](../../firmware-interface/expected_topics.md)

For the receiving side of the HA settings publishers and correction messages, see the coordinated device contracts. [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/0b7e9787bc6d475d17b4874b5c32096103d4c40e/docs/Coordinated_Release_9.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/0874ed3726824448c6ce334fe5765ac7c55a84f5/docs/Coordinated_Release_9.md).
