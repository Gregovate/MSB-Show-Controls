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

The return path carries HA operating settings to each device, followed by firmware State and System reports. See the MQTT contracts. [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/2c0bf6c6a3da4240876ccf24b06696c883dae4ef/docs/MQTT_Contract.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/370359f14cd5a69f82b44622c73b4a2a7c9be179/docs/MQTT_Contract.md).
