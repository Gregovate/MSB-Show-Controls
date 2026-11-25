# Daily warm-up and show extensions

Install the warm-up update from the [HA install folder](../ha/README.md). The running 0.3.1 bridge supports this configuration. Back up the installed files first. If automations have been edited on park HA since the November 25 export, reconcile those edits with ha/automations.yaml before replacement.

1. Replace /config/packages/signs.yaml and /config/automations.yaml with their corresponding files. Check configuration before restarting HA.
2. Replace the raw Signs dashboard YAML with ha/dashboard/signs-dashboard.yaml.
3. Set Radio and countdown warm-up to 4:30 PM, show start to 5 PM and the usual public close to 9 PM Central. Check the radio and projector nominal OFF helpers and projector safety OFF helper on the Administrator dashboard. Each receives the same extra minutes on top of its own baseline.
4. On a scheduled evening with overlays enabled, Show Force Close off and admissions Automatic, slot 9 rotates GATES OPEN IN / 30 MINUTES on both signs during warm-up. Keep slot 9 on Both / Pre-show. The display rounds up through 1 MINUTE and switches to operating messages at opening. The projector keeps its own start time. Radio still operates the volunteer marquee and car-counter arches. The public start remains the counter schedule anchor.
5. Before the existing cutoff, set the single extension control at the top of Signs. Confirm the displayed closing time and extend LOR manually. Example: 9 PM plus 20 minutes advertises 9:20 PM. A 9:10 PM nominal equipment cutoff moves to 9:30 PM. Show Stop still shuts equipment off immediately. The park's separate projector safety OFF follows its own nominal time plus the extension.
6. The existing dated MQTT settings feed each counter its extension and existing offset. The HA show/normal bucket sorter follows the public-open sensor. At local midnight HA sets the extension helper to zero; startup clears a previous date's restored value if HA missed midnight. Use the normal evening schedule with equipment deadlines before midnight. No reset or count-correction action belongs in the warm-up or extension workflow.

The large opening-advertising preset was a setup action that rewrites advertising text. It has been removed from Control. The operational initializer appears only until initialization is complete.

Check the returned effective end and dated extension on both devices before treating the counter update as complete. [Car Counter](https://github.com/Gregovate/MSB-Car-Counter-2024/blob/2c0bf6c6a3da4240876ccf24b06696c883dae4ef/docs/Coordinated_Release_9.md) · [Gate Counter](https://github.com/Gregovate/MSB-Gate-Counter-2025/blob/370359f14cd5a69f82b44622c73b4a2a7c9be179/docs/Coordinated_Release_9.md).
