# MSB Show Controls

System-level control, traffic analytics, and publishing for **Making Spirits Bright**.

This repo is the control plane that sits **on top of** the device and content repos.  
It does **not** contain firmware – it defines how everything fits together.

---

## Scope

MSB Show Controls covers:

- **Show setup & timing**
  - LOR show schedules (Preshow, Main Show, Show Closed, Cleanup)
  - Public open/close windows vs. operational/cleanup windows
  - How show times relate to traffic analytics and reset logic

- **Traffic system integration**
  - How CarCounter and GateCounter plug into Home Assistant
  - Traffic Reset System rules and safety constraints
  - Entity and automation definitions (documented snapshots)
  - How to recover from a bad night without trashing data

- **Website publishing & public status**
  - How “Open / Closed / Line is Long / Closed for Weather” is decided
  - How traffic counts and statuses *might* feed the website (future)
  - Any public JSON/API you decide to expose

- **Operational runbooks**
  - “What to do if CarCounter dies at 7:30 pm”
  - “What to do if GateCounter undercounts”
  - “How to extend show times in LOR and keep HA aligned”
  - Other incident and maintenance procedures

This repo is the **single source of truth** for how CarCounter, GateCounter, LOR, Home Assistant, and the website work together.

---

## Dependencies

This repo assumes the existence of:

- **Firmware repos**
  - `MSB-Car-Counter-20xx` – ESP32 firmware + SD logging for entrance counts
  - `MSB-Gate-Counter-20xx` – ESP32 firmware + SD logging for exit counts

- **Show control / sequencing**
  - Light-O-Rama (LOR) show computer with:
    - Preshow
    - Main Show
    - Show Closed
    - Cleanup / Post-show

- **Home Assistant**
  - MQTT broker integrated with CarCounter & GateCounter
  - Entities and automations for:
    - Traffic analytics
    - Show status and time windows
    - Operator dashboards / kiosks

- **(Optional) Website**
  - Public site allowed to consume a summarized “show status” signal
  - Future option for live stats, if desired

This repo **does not** replace any of those components – it documents and coordinates them.

---

## Repo Structure

Planned structure (will grow over time):

```text
MSB-Show-Controls/
  README.md

  docs/
    overview.md                # High-level system overview (future)
    traffic_reset_system.md    # Spec for traffic reset logic & safeties
    show_times_and_windows.md  # Mapping LOR shows ↔ HA windows (future)
    website_publishing.md      # How status gets published (future)
    operator_runbook.md        # Operational procedures (future)

  ha/
    entities/
      traffic_entities.md      # List & purpose of traffic-related entities
      show_time_entities.md    # Show-time / window entities (future)
    automations/
      traffic_automations.md   # Traffic / reset-related automations
      show_time_automations.md # Time-window automations (future)
    exports/
      automations.yaml         # HA UI export (snapshot, not hand-edited)
      template_sensors.yaml    # Template export (if you decide to store it)

  firmware-interface/
    car_counter_mqtt_api.md    # Topics & payloads expected from CarCounter
    gate_counter_mqtt_api.md   # Topics & payloads expected from GateCounter
    expected_topics.md         # Canonical list of topics used by HA

  design/
    traffic_flow_diagrams.md        # Logical flow of cars through park
    reset_flow_diagram.md           # When / how resets are allowed
    show_timing_state_machine.md    # How preshow/main/closed/cleanup interact
