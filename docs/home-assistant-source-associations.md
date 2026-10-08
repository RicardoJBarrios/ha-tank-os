# Home Assistant Source Associations

TankOS source associations connect an existing Home Assistant entity to a Tank
or Domain Location. The association is stored in the integration's Home
Assistant Config Entry options; it does not turn the entity ID into a TankOS
identity or create a canonical aquarium observation.

## Add or change an association

1. In Home Assistant, open **Settings > Devices & services > Integrations** and
   select **ha-tank-os**.
2. Open the integration's options/configuration flow.
3. Add an association by selecting a Home Assistant entity and an existing
   Tank or Domain Location. Use the edit or remove action to change an existing
   association.
4. If an entity or target is no longer available, its saved association is
   shown with a warning. Select a replacement explicitly or remove the
   association; TankOS does not infer replacements from names.

## Review continuous entity history

Use Home Assistant's native [History dashboard](https://www.home-assistant.io/dashboards/history/)
and select the associated entity. TankOS leaves continuous entity history in
Home Assistant Recorder and History: it does not copy each state update into
canonical TankOS Observations or change Recorder settings.

History availability follows the Home Assistant Recorder configuration. An
entity may be excluded from recording, and retained history may later be
purged. An association does not guarantee that history exists or will remain
available. See the [Recorder integration documentation](https://www.home-assistant.io/integrations/recorder/)
for the applicable inclusion and retention behavior.

Manual TankOS observations remain separate canonical records with their own
measurement context and provenance. This association slice does not generate
automatic association suggestions, associate entities with equipment, import
telemetry into canonical records, or control devices.
