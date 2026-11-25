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
