# MSB Signs 0.3.1 — HA owns the operating calculations

Install files are maintained together in [ha/](../ha/README.md). This directory contains the sign tests, payload generator and upgrade instructions.
Use this repository, not an older chat ZIP, for the package, grid, bridge and runbook.
Prepared source is not a claim that park HA or the physical signs have been updated.

- [Install and upgrade](UPGRADE.md)
- [Source contract, operating rules and experimental wait model](../docs/signs.md)
- [HA context template](tools/ha_context.jinja2)
- [Installable HA package](../ha/packages/signs.yaml)
- [Dashboard](../ha/dashboard/signs-dashboard.yaml)
- [Grid resource](../ha/www/msb-sign-message-grid.js)
- [sACN app](../ha/local_apps/msb_sign_bridge)

The bridge selects/renders messages and owns output timing only. HA owns public hours,
date-qualified extension, traffic classification and queue-wait calculation. No device
count reset or firmware changes are included. The legacy bridge traffic_from_rates
fallback and manual-wait input are removed. The new HA-only queue estimator is explicitly experimental and disabled until enabled.

## Tests

Use Python 3.12+ and Node 22+ in an isolated development environment:

    python -m pip install -r signs/requirements-test.txt
    python -m unittest discover -s signs/tests -v
    cd signs
    npm install
    npm test

The Python tests execute the installed package's Jinja against HA-compatible simulated
states; they do not contact HA or MQTT. The DOM tests use jsdom and simulated HA calls;
they do not establish native browser drag behavior. Rendering tests need DejaVu Sans
Bold installed on the test host; the app image installs Liberation Sans Bold.

Regenerate the embedded HA payload after editing the context template:

    python signs/tools/build_package.py

38 Python checks and the DOM grid suite passed for this release. Live acceptance is
listed in UPGRADE.md. The new Sign 2 estimator must be enabled and field-validated before relying on its public estimates.
