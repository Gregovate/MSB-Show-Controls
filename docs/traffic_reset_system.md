
---

### `docs/traffic_reset_system.md`

```markdown
# Traffic Reset System – Specification

Status: **Draft – Initial Skeleton**  
Owner: MSB Production / Traffic Systems  
Season: 2025+

---

## 1. Purpose

The Traffic Reset System defines **when and how** we are allowed to reset traffic-related counters and summaries for Making Spirits Bright.

Goals:

- Protect nightly totals from accidental or premature resets.
- Keep **CarCounter** and **GateCounter** logically consistent.
- Allow controlled recovery from a “bad night” without destroying raw data.
- Separate **device behavior** (firmware) from **system behavior** (Home Assistant + procedures).

This is about **system-level rules**, not firmware details.

---

## 2. Scope

The reset system covers:

- **Home Assistant entities** that track:
  - Cars entering (CarCounter)
  - Cars exiting (GateCounter)
  - Cars currently in the park
  - Nightly totals and derived statistics

- **Reset actions** such as:
  - Resetting HA-side totals / “Official Nightly Totals”
  - Resetting HA-side “cars currently in park” estimates
  - (Eventually) telling firmware when to roll to a new day, if needed

![Traffic Reset Flow](../images/design/reset_flow_v1.png)

Out of scope (documented elsewhere):

- Exact MQTT topic naming for CarCounter / GateCounter.
- How LOR show schedules are configured.
- Website presentation of the numbers.

---

## 3. Key Concepts

### 3.1 Raw Device Counts vs. Official Nightly Totals

- **Raw device logs** (SD card CSVs on each counter) are the **ground truth**:
  - Per-beam events
  - Time stamps
  - Raw enter/exit counts
- **Home Assistant counters** are **operational numbers**:
  - Used for dashboards and real-time decisions.
  - Can be adjusted via reset logic if there’s an incident.
- **Official nightly totals**:
  - What you present to the Steering Committee.
  - Should be derived from HA counters **plus** SD logs when needed.
  - Must remain traceable back to raw data.

Rule:  
**Never “fix” history by overwriting SD logs.** Fix at the HA/analytics layer and keep the raw data intact.

---

### 3.2 Show Windows vs. Reset Windows

We care about several time windows per night (exact times defined in `show_times_and_windows.md` later):

- **Public Show Window**  
  When guests are allowed in the park (e.g., 5:00 pm–9:00 pm main show, 9:00–9:30 “Show Closed” mode).

- **Analytics Window**  
  Subset of the operational time where:
  - Car traffic is considered “show traffic”.
  - Counts contribute to nightly totals.

- **Reset-Safe Window**  
  Time of day when it is **allowed** to reset HA counters:
  - Park is empty (or confirmed empty).
  - No more public traffic expected.
  - Typically **after** the show is completely done and cleanup is over.

---

### 3.3 One-Way Data Flow (for resets)

Principle:

- **Resets happen in Home Assistant**, not on the devices.
- CarCounter and GateCounter keep their own cumulative logs.
- HA layers logic on top of them.

Reason:  
Device firmware should be as dumb as possible about “special rules” and “oops recovery.” All that lives here.

---

## 4. Entities Involved (Inventory Stub)

> Full detail goes in `ha/entities/traffic_entities.md`.  
> This section only lists entities that are directly impacted by reset rules.

### 4.1 Core Counters (HA)

- `sensor.msb_car_counter_enter_cars`
  - Cumulative number of cars that **entered** tonight (from CarCounter).

- `sensor.msb_gate_counter_exit_cars`
  - Cumulative number of cars that **exited** tonight (from GateCounter).

- `sensor.msb_cars_in_park_estimate`
  - Derived value:
    - `enter_cars - exit_cars`
    - With guardrails to avoid negative values and obviously insane numbers.

- `sensor.msb_car_counter_show_total_cars`
  - “Official” nightly total view (for dashboards / reporting).

### 4.2 Reset Controls (HA)

These may not all exist yet; this is the target:

- `input_boolean.msb_allow_traffic_reset`
  - Manual “arm switch” – must be turned on by an operator before any reset can fire.

- `input_button.msb_reset_traffic_totals`
  - Single button to trigger a **controlled** reset of:
    - HA-side totals
    - “cars in park” estimate (if appropriate)

- `sensor.msb_reset_guard_conditions`
  - Template sensor summarizing whether conditions are safe:
    - Park empty
    - Outside analytics window
    - Both counters online
    - Etc.

- `sensor.msb_reset_last_time`
  - Records when the last reset occurred (for audit / sanity).

---

## 5. Reset Rules & Safety Constraints

This is the core of the system.

### 5.1 Hard Rules – When Reset Is **Forbidden**

The reset automation must **not** execute if **any** of the following are true:

1. **Inside Analytics Window**
   - If we are inside the “show traffic” window, **block resets**.
   - We do not reset while guests are still coming/going.

2. **Park Not Empty**
   - If the estimated cars in park is **> 0**, block resets.
   - If GateCounter is known to be offline or lying, treat state as **unknown** and escalate to manual recovery, not auto-reset.

3. **Device Offline**
   - If CarCounter **or** GateCounter is marked offline / unavailable:
     - Do **not** reset totals.
   - Reason: you don’t know if more events will arrive later.

4. **Reset Arm Switch Off**
   - If `input_boolean.msb_allow_traffic_reset` is **off**, ignore button presses.
   - This prevents random poking at the UI from wiping counts.

5. **Too Many Resets**
   - Optional: enforce **max one reset per night**.
   - If `sensor.msb_reset_last_time` is already set for tonight, block further resets unless an explicit override is added.

---

### 5.2 Soft Rules – Operator Checklist Before Reset

These live in the **runbook** but drive the design:

- Confirm:
  - Show is fully over (LOR in “Idle/Cleanup” state).
  - Park is visually empty via cameras / on-site report.
  - No pending known issues with counters (stuck beam, power drop, etc.).

If any of these are uncertain, **do not** use the automated reset; instead follow the **“Bad Night Recovery”** process.

---

## 6. Reset Flow (Happy Path)

This is the ideal, normal-night behavior.

1. **Show finishes**, cleanup done, park known empty.
2. System time moves into **Reset-Safe Window** (e.g., after 9:45 pm).
3. Operator:
   - Turns on `input_boolean.msb_allow_traffic_reset`.
   - Clicks `input_button.msb_reset_traffic_totals`.
4. Automation checks:
   - Time is inside Reset-Safe Window.
   - Analytics window is closed.
   - Park estimate == 0.
   - Counters online and healthy.
   - Reset hasn’t already happened tonight.
5. If **all checks pass**:
   - HA-side totals/derived counters are reset for **tomorrow’s show**.
   - `sensor.msb_reset_last_time` updated.
   - `input_boolean.msb_allow_traffic_reset` automatically turned **off**.
6. SD logs on devices are **not touched**.

Implementation details go in `ha/automations/traffic_automations.md`.

---

## 7. Bad Night Recovery (High-Level)

This section is just an outline – full step-by-step instructions will live in the operator runbook.

Scenarios:

- **CarCounter died mid-show**
  - Raw SD logs show only part of the night.
  - GateCounter may have full exit data.
  - HA totals are wrong / incomplete.

- **GateCounter undercounted significantly**
  - Entrance numbers are much higher than exit numbers.
  - Known beam issue or camera evidence of discrepancies.

Approach (high level):

1. **Do not** try to “fix” HA numbers by guessing.
2. Pull SD logs from both counters.
3. Reconstruct nightly totals offline:
   - Use CarCounter enter totals as primary.
   - Use GateCounter exits and beam logs for sanity checks.
4. Store reconstructed totals in:
   - A manual “Official Totals” sheet, and/or
   - A separate HA sensor/attribute marked as “corrected”.
5. Document the incident in the runbook + future postmortem.

The key point:  
**Bad nights are handled manually and documented, not auto-corrected in real time.**

---

## 8. Future Enhancements

These are intentionally out of scope for the first implementation, but worth documenting:

- **Scheduled Auto-Reset**
  - Automatically reset HA-side totals at a fixed time **only** if:
    - Park is empty.
    - Devices are healthy.
    - No alarms active.

- **HA ↔ Firmware Day Boundary Coordination**
  - Optional: send a “rollover” signal to devices when HA has committed to a new day.

- **Audit Log**
  - Dedicated log of:
    - When resets occurred.
    - Who triggered them (if HA user tracking is available).
    - Why (optional text field in runbook / external log).

---

## 9. Implementation References

When built, the following docs will contain the concrete implementation:

- `ha/entities/traffic_entities.md`
  - Detailed list of all sensors, inputs, and buttons in the reset system.

- `ha/automations/traffic_automations.md`
  - Actual automation YAML (or pseudo-YAML) implementing:
    - Reset guardrails
    - Button handling
    - State updates

- `docs/operator_runbook.md`
  - “How to safely reset nightly traffic totals”
  - “How to handle device failure or undercount incidents”
