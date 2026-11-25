# Production equipment and extension automations

| Automation in park HA | Triggers and effects |
| --- | --- |
| Production - Broadcast Radio Schedule | At the radio ON helper, checks show season and Force Close, then energizes radio, volunteer marquee and car-counter arches. The dated extension moves the radio OFF deadline. Show Stop turns all three off. |
| Production - Car Counter Arches Follow Radio | Follows radio switch transitions. The arches can also be switched for off-show testing. |
| Production - Projector Schedule | Uses the projector ON helper with season and Force Close checks. Its own OFF helper plus the dated extension sets normal shutdown. Show Stop shuts it off. |
| Production - Projector Safety Off | A second OFF action checks the projector is on at its extended safety cutoff. Keep the safety helper later than normal shutdown. |
| MSB Traffic: Date the show extension | A numeric change to the extension helper stamps its date with local YYYYMMDD. |
| MSB Traffic: Clear prior night extension | Clears the helper at midnight and on startup when its stored date is stale. |
| Production - Radio Charger Schedule | Charger triggers are 8:45 PM, 1 AM, 4:15 PM and 4:30 PM. These are a separate equipment schedule. |

Example: a 20-minute extension makes a nominal 9 PM public close 9:20 PM, while a nominal 9:10 PM equipment cutoff moves to 9:30 PM. Enter the extension before the existing cutoff. Coordinate the LOR schedule on the show PC.

[Complete automation definitions](../automations.yaml) · [Schedule helpers](../entities/show_time_entities.md)
