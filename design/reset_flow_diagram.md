# Counter schedule versus manual correction

```mermaid
flowchart TD
  A["Public opening helper"] --> B["HA sends each device its offset"]
  B --> C["Firmware schedules its reset"]
  D["Operator changes numeric override"] --> E{"Matching permission on and readings numeric?"}
  E -->|Yes| F["Send one non-retained correction"]
  E -->|No| G["Skip correction"]
```

Warm-up uses the radio ON helper. The midnight action clears the nightly extension. Neither action publishes a count correction. The separate season-start setting has implications for season totals. Review the [implemented automations](../ha/automations/traffic_automations.md) before acting on a discrepancy.
