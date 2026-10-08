# ha-tank-os First Run

The first product slice is a local Home Assistant integration. It stores
canonical Tank, Domain Location, measurement-session, and manual Observation
records in Home Assistant's local storage through the integration repository.

## Install the integration

1. Start Home Assistant with the repository's local test target when working
   on the integration:

   ```sh
   pnpm ha:up
   pnpm ha:wait
   ```

2. Add **ha-tank-os** from Home Assistant's integration configuration flow.
3. Use the native `tank_os` services from Home Assistant's Developer Tools or
   an automation. The integration does not require a custom dashboard for the
   first context and manual-observation workflow.

## First context workflow

Create a Tank and retain the returned product-owned `tank_id`:

```yaml
action: tank_os.create_tank
data:
  name: Veril
```

Create a Domain Location with that identifier:

```yaml
action: tank_os.create_location
data:
  tank_id: tank_<returned-id>
  name: Display
```

Retrieve the context with `tank_os.list_context`. Tank and Domain Location
identities are owned by ha-tank-os; Home Assistant entity IDs and labels are
not their canonical identity.

## First manual observation workflow

Record a result without overwriting earlier history:

```yaml
action: tank_os.record_observation
data:
  tank_id: tank_<returned-id>
  parameter: alkalinity
  reported_value: 7.2
  unit: dKH
  qualifier: "<"
  method_id: salifert
```

Use `tank_os.list_observations` to retrieve the original reported value,
qualifier, unit, source, recording time, and any known measurement time. Start
`tank_os.start_measurement_session` first when several partial results share a
sample or measurement session, then pass its `session_id` to each observation.

The first slice records manual observations only. It does not ingest every Home
Assistant sensor update, create a custom dashboard, estimate chemistry, or
actuate aquarium equipment. Unknown measurement times remain unknown; the
recording time is not substituted for them.

## Persistence and recovery boundary

The canonical record is stored by the integration repository using Home
Assistant's versioned, atomic `Store` primitive. The repository confirms a
write by rereading the saved payload. A persistence failure is reported as an
unsaved operation rather than silently replacing the prior canonical data.

Home Assistant backups may retain older copies of deleted records. Backup
rotation and recovery policy are outside this first slice.
