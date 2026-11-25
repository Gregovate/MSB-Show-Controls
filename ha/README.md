# Park Home Assistant install files

Pull the current Show Controls branch on each computer before copying files. Run `git branch --show-current` and `git log -1 --oneline` to confirm both computers have the same revision.

| File or folder in this directory | Park HA destination |
| --- | --- |
| `automations.yaml` | `/config/automations.yaml` (complete park automation list) |
| `packages/signs.yaml` | `/config/packages/signs.yaml` |
| `packages/traffic_analytics.yaml` | `/config/packages/traffic_analytics.yaml` |
| `packages/sign2_queue_wait.yaml` | `/config/packages/sign2_queue_wait.yaml` |
| `dashboard/signs-dashboard.yaml` | Existing Signs dashboard → raw configuration editor |
| `www/msb-sign-message-grid.js` | `/config/www/msb-sign-message-grid.js` |
| `local_apps/msb_sign_bridge/` | Existing `/local_apps/msb_sign_bridge/` directory |

**Already running bridge 0.3.1?** Follow the [warm-up update](../docs/warmup-extension.md) for the three files that changed. **Upgrading an older bridge?** Follow the [bridge and HA upgrade](../signs/UPGRADE.md).

Copy only the listed files required for the update. Keep the other park HA packages in place. Make configuration edits here and commit them. If an operator changes automation definitions directly in HA, bring the revised definitions back into this repository before the next deployment. Dashboard helper values such as tonight’s extension are live settings in HA.

The Car Counter supplies entrance data and the Gate Counter supplies exit data. Both consume HA operating settings and report what they applied. Follow the [two-way MQTT interface](../firmware-interface/expected_topics.md#follow-a-transaction-across-repositories) or go directly to the firmware MQTT contracts: [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/2c0bf6c6a3da4240876ccf24b06696c883dae4ef/docs/MQTT_Contract.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/370359f14cd5a69f82b44622c73b4a2a7c9be179/docs/MQTT_Contract.md).
