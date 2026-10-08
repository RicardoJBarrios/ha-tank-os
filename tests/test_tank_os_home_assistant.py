"""Home Assistant surface tests for ha-tank-os."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

if sys.platform != "win32":
    from homeassistant.core import Context, HomeAssistant
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
