# Park Home Assistant install files

Pull the main branch on each computer before copying files. Run `git branch --show-current` and `git log -1 --oneline` to confirm both computers have the same revision.

| File or folder in this directory | Park HA destination |
| --- | --- |
| `automations.yaml` | `/config/automations.yaml` (complete park automation list) |
| `packages/signs.yaml` | `/config/packages/signs.yaml` |
| `packages/traffic_analytics.yaml` | `/config/packages/traffic_analytics.yaml` |
| `packages/sign2_queue_wait.yaml` | `/config/packages/sign2_queue_wait.yaml` |
| `dashboard/park-captain-kiosk.yaml` | Park Captain kiosk dashboard raw configuration (Cars in park includes Gate diagnostic) |
| [`dashboard/show-administration.yaml`](dashboard/show-administration.yaml) | Existing Show Administration dashboard → raw configuration editor (complete dashboard) |
| [`dashboard/volunteer-trailer-office.yaml`](dashboard/volunteer-trailer-office.yaml) | Volunteer trailer office tablet, landscape → existing dashboard raw configuration editor |
| `dashboard/signs-dashboard.yaml` | Existing Signs dashboard → raw configuration editor |
| `www/msb-sign-message-grid.js` | `/config/www/msb-sign-message-grid.js` |
| `local_apps/msb_sign_bridge/` | Existing `/local_apps/msb_sign_bridge/` directory |

**Already running bridge 0.3.1?** Follow the [warm-up update](../docs/warmup-extension.md) for the three files that changed. **Upgrading an older bridge?** Follow the [bridge and HA upgrade](../signs/UPGRADE.md).

For the November 25 occupancy change, copy `packages/traffic_analytics.yaml` to `/config/packages/traffic_analytics.yaml`, check the configuration and reload template entities or restart HA. Verify a numeric Gate reading and an unavailable input in the captain dashboard.

For the weather-closure override, merge the `msb_reset_days_running` automation from `ha/automations.yaml` into the park’s `/config/automations.yaml` and reload automations. If a local automation already publishes this command, replace that entry to keep one publisher.

Copy only the listed files required for the update. Keep the other park HA packages in place. Make configuration edits here and commit them. If an operator changes automation definitions directly in HA, bring the revised definitions back into this repository before the next deployment. Dashboard helper values such as tonight’s extension are live settings in HA.

The Car Counter supplies entrance data and the Gate Counter supplies exit data. Both consume HA operating settings and report what they applied. Follow the [two-way MQTT interface](../firmware-interface/expected_topics.md#follow-a-transaction-across-repositories) or go directly to the firmware MQTT contracts: [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/main/docs/MQTT_Contract.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/main/docs/MQTT_Contract.md).

[Three-repository main baseline and opening-night checks](../docs/friday-system-check.md).

### Live matrix previews (bridge 0.3.2)

Copy the updated signs package, bridge app files and existing JavaScript resource to their destinations above. Check the HA configuration and restart HA. Rebuild/update the installed local bridge app and start version 0.3.2 with its existing options. Update the existing dashboard module URL to `/local/msb-sign-message-grid.js?v=8`, apply the two kiosk dashboards, and refresh both tablets.

During an HA overlay, Counts on the office tablet and Signs on the captain tablet show the two rendered 80 × 34 RGB frames. During a release they show “Light-O-Rama has control”. Confirm both signs during a normally scheduled rotation.
