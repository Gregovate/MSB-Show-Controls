# How traffic measurements reach the signs

```mermaid
flowchart TD
  A["CarCounter entries"] --> C["HA traffic analytics"]
  B["GateCounter exits"] --> C
  C --> D["Traffic status and occupancy"]
  D --> E["HA sign control snapshot"]
  D --> F["Experimental Sign 2 estimate"]
  F --> E
  E --> G["Sign bridge"]
  G --> H["HWY 42"]
  G --> I["Front Entrance"]
```

HWY 42 alone can display the Sign 2 wait estimate. The estimator requires valid inputs and an enabled model. The counters observe arrivals and departures at fixed points. They cannot tell the captain how far the line extends up the highway. Consult both camera views and the [estimator assumptions](../docs/signs.md).
