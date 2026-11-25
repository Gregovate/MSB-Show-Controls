# Public schedule and admissions

```mermaid
stateDiagram-v2
  [*] --> Advertising
  Advertising --> Warmup: Scheduled radio start
  Warmup --> Public: Gates open
  Public --> Cutoff: Extended deadline
  Cutoff --> Clearing: Captain accepts remaining line
  Clearing --> Closed: Captain closes admission
  Public --> Closed: Captain closes admission
```

Cutoff ends the scheduled public window. The sign bridge displays explicit closure wording only on the corresponding admission or weather command. Weather closure takes priority while master overlays are enabled. Master overlays off releases both signs to LOR. See [admission controls](../docs/signs.md) for override priority.
