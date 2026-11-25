"""Pure sign scheduling rules. All operator settings arrive from HA."""



def rgb(value):
    """Accept comma-separated raw pixel levels, each in the range 0..255."""
    parts = [int(v.strip()) for v in value.split(",")]
    if len(parts) != 3 or any(v < 0 or v > 255 for v in parts):
        raise ValueError("Colors require three values from 0 to 255")
    return tuple(parts)


def context(config, now):
    """Use HA's resolved operating state; do not duplicate traffic/time formulas."""
    return dict(config["ha"])


def playlist(config, sign, now):
    """Select, resolve, and order the messages eligible for one sign."""
    ctx = context(config, now)
    if not ctx["allowed"]:
        return [], ctx
    if ctx["weather_closed"]:
        return [{"id": 900, "lines": ["CLOSED", "WEATHER"], "background": (12, 0, 0),
                 "text_color": (100, 100, 100), "seconds": 7}], ctx
    if ctx["admissions_closed"]:
        return [{"id": 901, "lines": ["ENTRY CLOSED", "THANK YOU"], "background": (12, 0, 0),
                 "text_color": (100, 100, 100), "seconds": 7}], ctx
    conditions = {
        "Always": True,
        "Pre-show": ctx["preshow"],
        "Gates open": ctx["admitting"] and config["gate_message_enabled"],
        "Public operation": ctx["admitting"],
        "Clearing queue": ctx["clearing_queue"],
        "Gates closed": not ctx["gates_open"],
        "Promotion active": ctx["promotion"],
        "Traffic available": ctx["gates_open"] and ctx["traffic_valid"],
    }
    result = []
    for message in sorted(config["messages"], key=lambda m: (m["order"], m["id"])):
        if message["target"] not in ("Both", sign) or not conditions[message["condition"]]:
            continue
        if message["id"] == 16 and ctx["clearing_queue"]:
            continue  # Replace the deadline announcement with queue-admission wording.
        lines = [message["line1"], message["line2"]]
        if any("{wait_minutes}" in line for line in lines) and sign != "HWY 42":
            continue
        # Missing telemetry hides the message instead of publishing an invented zero.
        if any("{"+key+"}" in line and ctx[key] is None
               for key in ("tonight", "season_total", "food_lbs", "wait_minutes") for line in lines):
            continue
        # The existing four-card editor remains authoritative. Only the date
        # announcement is automatic; no operator edits are needed at midnight.
        if message["id"] == 9 and ctx["preshow"]:
            lines = ctx["opening_announcement"]
        if message["id"] == 7:
            continue  # Retired duplicate announcement; slot identity stays intact.
        for key in ("closing_time", "traffic", "in_park", "show_total", "tonight", "season_total", "food_lbs", "wait_minutes"):
            lines = [line.replace("{" + key + "}", str(ctx[key])) for line in lines]
        if not any(line.strip() for line in lines):
            continue
        mode = message["color_mode"]
        color = message["background"]
        if mode == "Gates":
            color = config["colors"]["open" if ctx["gates_open"] else "closed"]
        elif mode == "Traffic":
            if not ctx["traffic_valid"]:
                continue
            color = config["colors"][ctx["traffic_key"]]
        result.append({
            "id": message["id"], "lines": lines,
            "background": rgb(color), "text_color": rgb(message["text_color"]),
            "seconds": message["seconds"] or config["screen_seconds"],
        })
    if ctx["preshow"] and ctx["opening_day"]:
        result.insert(next((i+1 for i,m in enumerate(result) if m["id"] == 9), len(result)), {"id": 90, "lines": ["GATES OPEN", ctx["opening_time"]],
                       "background": (0, 0, 12), "text_color": (100, 100, 100), "seconds": 7})
    return result, ctx


def validate(config):
    """Validate HA snapshots before allowing any sACN output."""
    assert config["schema"] == 3, "Install the matching HA signs package (schema 3)"
    assert type(config["enabled"]) is bool
    assert type(config["gate_message_enabled"]) is bool
    ctx = config["ha"]
    for key in ("allowed", "weather_closed", "admissions_closed", "clearing_queue",
                "admitting", "gates_open", "preshow", "opening_day", "promotion", "traffic_valid"):
        assert type(ctx[key]) is bool, key
    assert ctx["allowed"] is False or config["enabled"], "Master off must release output"
    for key in ("tonight", "season_total", "food_lbs", "wait_minutes"):
        value = ctx[key]
        assert value is None or (isinstance(value, str) and value.isdigit()), key
    for key in ("closing_time", "opening_time", "schedule_status", "traffic", "traffic_key", "in_park", "show_total"):
        assert isinstance(ctx[key], str), key
    assert len(ctx["opening_announcement"]) == 2
    assert all(isinstance(v, str) and len(v) <= 80 for v in ctx["opening_announcement"])
    assert 1 <= config["screen_seconds"] <= 60
    assert set(config["lor_seconds"]) == {"HWY 42", "Front Entrance"}
    assert all(5 <= value <= 900 for value in config["lor_seconds"].values())
    assert len(config["messages"]) <= 32
    assert len({m["id"] for m in config["messages"]}) == len(config["messages"])
    for m in config["messages"]:
        assert m["target"] in ("Disabled", "Both", "HWY 42", "Front Entrance")
        assert m["condition"] in ("Always", "Gates open", "Gates closed", "Promotion active", "Traffic available", "Pre-show", "Public operation", "Clearing queue")
        assert m["color_mode"] in ("Fixed", "Gates", "Traffic")
        assert 0 <= m["seconds"] <= 60
        assert 1 <= m["order"] <= 99
        assert all(isinstance(m[k], str) and len(m[k]) <= 80 for k in ("line1", "line2"))
        rgb(m["background"])
        rgb(m["text_color"])
    for value in config["colors"].values():
        rgb(value)
    return config
