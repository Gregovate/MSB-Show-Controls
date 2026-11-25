# Verify a sign-control update

Run the Python and dashboard tests using the commands in the [developer guide](README.md). The Python suite renders the HA package with simulated local times and counter states. Cases include the opening-day transition, daily countdown, dated extensions, admission overrides, missing telemetry and analytics formula preservation. The JavaScript suite checks grid edits, order persistence, colors and recovery from a failed save.

| Park HA check | Expected observation |
| --- | --- |
| After applying YAML | HA configuration check passes. After restart the dashboard resolves the new entities. |
| Bridge health | Version 0.3.1, Connected and Controls Fresh on. Read the schedule state to explain an intentional release to LOR. |
| Warm-up on a scheduled show night | Both signs rotate the countdown alongside advertising. At gates-open time the public messages become eligible. |
| Extension entered before cutoff | The dashboard and sign deadline agree. Counter state reports the extension and effective end minute. Verify the LOR setting independently. |
| Production handoff | Both physical signs return to the LOR sequence between overlays. |

The automated tests simulate the software. The highway wait model requires separate field timing from HWY Sign 2 to CarCounter before public use. Record measured start/end times, lane configuration and queue conditions when evaluating the estimate.
