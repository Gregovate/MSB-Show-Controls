# MSB Show Controls

Home Assistant coordinates the Making Spirits Bright entrance and exit counters, show equipment and two roadside signs. The show PC runs the Light-O-Rama schedule. The maintained installation files live together under [ha/](ha/README.md).

| Task | Start here |
| --- | --- |
| Install or update park HA from either computer | [Install file map](ha/README.md) and [warm-up update](docs/warmup-extension.md) |
| Run a show night, extend admission or resolve a sign problem | [Park captain runbook](docs/operator_runbook.md) |
| Understand which clock controls which device | [System overview](docs/overview.md) and [show windows](docs/show_times_and_windows.md) |
| Diagnose counts or check an extension at the counter | [Traffic automations](ha/automations/traffic_automations.md) and [MQTT topics](firmware-interface/expected_topics.md) |
| Maintain the bridge or verify a change | [Sign operating contract](docs/signs.md) and [validation](signs/VALIDATION.md) |
| Determine what reaches the website | [Website publishing status](docs/website_publishing.md) |

Use the same Git branch and revision on the laptop and show PC. Check both with `git status --short --branch` and `git log -1 --oneline`. Pull committed updates with `git pull --ff-only`. Installation on park HA is a separate step.
