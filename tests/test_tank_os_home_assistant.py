"""Home Assistant surface tests for ha-tank-os."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

if sys.platform != "win32":
    from homeassistant.core import Context, HomeAssistant
    from homeassistant.data_entry_flow import InvalidData
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.tank_os import async_setup_entry, async_unload_entry
    from custom_components.tank_os.config_flow import TankOsConfigFlow
    from custom_components.tank_os.const import DOMAIN

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Home Assistant runtime requires POSIX; covered by Linux and macOS CI.",
)


@pytest.mark.asyncio
async def test_native_services_create_and_retrieve_context(tmp_path: Path) -> None:
    hass = HomeAssistant(str(tmp_path))
    await hass.async_start()
    entry = MockConfigEntry(domain=DOMAIN, title="ha-tank-os")
    try:
        assert await async_setup_entry(hass, entry)
        user_context = Context(user_id="user-1")

        created = await hass.services.async_call(
            DOMAIN,
            "create_tank",
            {"name": "Veril"},
            blocking=True,
            context=user_context,
            return_response=True,
        )
        tank = created["tank"]
        await hass.services.async_call(
            DOMAIN,
            "create_location",
            {"tank_id": tank["tank_id"], "name": "Display"},
            blocking=True,
            context=user_context,
        )
        context = await hass.services.async_call(
            DOMAIN,
            "list_context",
            {"tank_id": tank["tank_id"]},
            blocking=True,
            context=user_context,
            return_response=True,
        )
        session = await hass.services.async_call(
            DOMAIN,
            "start_measurement_session",
            {"tank_id": tank["tank_id"], "sample_id": "sample-1"},
            blocking=True,
            context=user_context,
            return_response=True,
        )
        await hass.services.async_call(
            DOMAIN,
            "record_observation",
            {
                "tank_id": tank["tank_id"],
                "parameter": "alkalinity",
                "reported_value": 7.2,
                "unit": "dKH",
                "qualifier": "<",
                "session_id": session["session"]["session_id"],
            },
            blocking=True,
            context=user_context,
        )
        observations = await hass.services.async_call(
            DOMAIN,
            "list_observations",
            {"tank_id": tank["tank_id"]},
            blocking=True,
            context=user_context,
            return_response=True,
        )

        assert context["context"]["tanks"][0]["tank_id"] == tank["tank_id"]
        assert context["context"]["locations"][0]["name"] == "Display"
        assert observations["observations"][0]["qualifier"] == "<"
    finally:
        await async_unload_entry(hass, entry)
        await hass.async_stop()


@pytest.mark.asyncio
async def test_config_flow_uses_native_home_assistant_form() -> None:
    result = await TankOsConfigFlow().async_step_user()
    assert result["type"] == "form"
    assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_native_mutation_rejects_missing_user_context(tmp_path: Path) -> None:
    hass = HomeAssistant(str(tmp_path))
    await hass.async_start()
    entry = MockConfigEntry(domain=DOMAIN, title="ha-tank-os")
    try:
        assert await async_setup_entry(hass, entry)
        with pytest.raises(PermissionError):
            await hass.services.async_call(
                DOMAIN,
                "create_tank",
                {"name": "Unauthorized"},
                blocking=True,
                return_response=True,
            )
    finally:
        await async_unload_entry(hass, entry)
        await hass.async_stop()


@pytest.mark.asyncio
async def test_source_association_options_flow_adds_tank_mapping(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="ha-tank-os")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    application = hass.data[DOMAIN][entry.entry_id]
    tank = await application.create_tank("user-1", "Veril")
    hass.states.async_set("sensor.display_temperature", "25.4")

    result = await hass.config_entries.options.async_init(
        entry.entry_id, context={"source": "user"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "add"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "entity_id": "sensor.display_temperature",
            "target": f"tank:{tank['tank_id']}",
        },
    )

    assert result["type"] == "create_entry"
    assert entry.options["source_associations"] == [
        {
            "entity_id": "sensor.display_temperature",
            "target": f"tank:{tank['tank_id']}",
        }
    ]
    hass.states.async_set("sensor.display_temperature", "25.5")
    await hass.async_block_till_done()
    assert await application.list_observations(tank["tank_id"]) == []
    assert entry.data == {}
    await hass.config_entries.async_reload(entry.entry_id)
    reloaded_application = hass.data[DOMAIN][entry.entry_id]
    assert await reloaded_application.list_tanks() == [tank]
    assert entry.options["source_associations"][0]["entity_id"] == "sensor.display_temperature"


@pytest.mark.asyncio
async def test_source_association_options_flow_updates_and_removes_mapping(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="ha-tank-os",
        options={"source_associations": [{"entity_id": "sensor.old", "target": "tank:tank-1"}]},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    application = hass.data[DOMAIN][entry.entry_id]
    tank = await application.create_tank("user-1", "Veril")
    location = await application.create_location("user-1", tank["tank_id"], "Display")
    hass.states.async_set("sensor.new", "25.1")

    result = await hass.config_entries.options.async_init(
        entry.entry_id, context={"source": "user"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "edit"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"association_index": "0"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "entity_id": "sensor.new",
            "target": f"location:{location['location_id']}",
        },
    )
    assert result["type"] == "create_entry"
    assert entry.options["source_associations"] == [
        {
            "entity_id": "sensor.new",
            "target": f"location:{location['location_id']}",
        }
    ]

    result = await hass.config_entries.options.async_init(
        entry.entry_id, context={"source": "user"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "remove"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"association_index": "0"}
    )
    assert result["type"] == "create_entry"
    assert entry.options["source_associations"] == []
    assert await application.list_context(tank["tank_id"]) == {
        "tanks": [tank],
        "locations": [location],
    }


@pytest.mark.asyncio
async def test_source_association_preserves_stale_references_for_review(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="ha-tank-os")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    tank = await hass.data[DOMAIN][entry.entry_id].create_tank("user-1", "Veril")
    hass.config_entries.async_update_entry(
        entry,
        options={
            "source_associations": [
                {"entity_id": "sensor.removed", "target": f"tank:{tank['tank_id']}"},
                {"entity_id": "sensor.available", "target": "tank:removed-tank"},
            ]
        },
    )
    hass.states.async_set("sensor.available", "25.0")
    result = await hass.config_entries.options.async_init(
        entry.entry_id, context={"source": "user"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "edit"}
    )

    assert result["type"] == "form"
    assert result["step_id"] == "edit"
    schema = result["data_schema"].schema
    association_selector = next(iter(schema.values()))
    labels = [item["label"] for item in association_selector.config["options"]]
    assert all(label.startswith("⚠ ") for label in labels)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"association_index": "1"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"entity_id": "sensor.available", "target": "tank:removed-tank"},
    )
    assert result["type"] == "form"
    assert result["errors"] == {"base": "target_not_found"}
    assert entry.options["source_associations"] == [
        {"entity_id": "sensor.removed", "target": f"tank:{tank['tank_id']}"},
        {"entity_id": "sensor.available", "target": "tank:removed-tank"},
    ]


@pytest.mark.asyncio
async def test_source_association_rejects_unknown_target(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="ha-tank-os")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.data[DOMAIN][entry.entry_id].create_tank("user-1", "Veril")
    hass.states.async_set("sensor.display_temperature", "25.4")

    result = await hass.config_entries.options.async_init(
        entry.entry_id, context={"source": "user"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "add"}
    )
    with pytest.raises(InvalidData, match="Schema validation failed"):
        await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                "entity_id": "sensor.display_temperature",
                "target": "tank:unknown",
            },
        )
    assert "source_associations" not in entry.options


def test_source_association_translations_have_matching_keys() -> None:
    component = Path(__file__).parents[1] / "custom_components" / "tank_os"
    source = json.loads((component / "strings.json").read_text(encoding="utf-8"))
    english = json.loads((component / "translations" / "en.json").read_text(encoding="utf-8"))
    spanish = json.loads((component / "translations" / "es.json").read_text(encoding="utf-8"))

    def keys(value: dict, prefix: str = "") -> set[str]:
        paths = set()
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            paths.add(path)
            if isinstance(child, dict):
                paths.update(keys(child, path))
        return paths

    assert source == english
    assert keys(english) == keys(spanish)
