"""Contract tests for the first ha-tank-os product slice."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import storage
from homeassistant.helpers.storage import Store

from custom_components.tank_os.application import (
    ApplicationService,
    AuthorizationError,
)
from custom_components.tank_os.domain import DependencyError, DomainValidationError
from custom_components.tank_os.persistence import CanonicalRepository, PersistenceError


async def _application(tmp_path: Path) -> tuple[HomeAssistant, ApplicationService]:
    hass = HomeAssistant(str(tmp_path))
    await hass.async_start()
    repository = CanonicalRepository(hass)
    application = ApplicationService(repository)
    await repository.async_load()
    return hass, application


@pytest.mark.asyncio
async def test_tanks_and_locations_have_stable_product_ids(tmp_path: Path) -> None:
    hass, application = await _application(tmp_path)
    try:
        first = await application.create_tank("user-1", "Veril")
        second = await application.create_tank("user-1", "Veril")
        location = await application.create_location("user-1", first["tank_id"], "Display")

        assert first["tank_id"] != second["tank_id"]
        assert location["location_id"].startswith("location_")
        assert location["tank_id"] == first["tank_id"]
        assert (await application.list_context(first["tank_id"]))["locations"] == [location]
    finally:
        await hass.async_stop()


@pytest.mark.asyncio
async def test_mutations_require_home_assistant_user_context(tmp_path: Path) -> None:
    hass, application = await _application(tmp_path)
    try:
        with pytest.raises(AuthorizationError):
            await application.create_tank(None, "Unauthorized")
        assert await application.list_tanks() == []
    finally:
        await hass.async_stop()


@pytest.mark.asyncio
async def test_partial_observations_preserve_provenance_and_history(
    tmp_path: Path,
) -> None:
    hass, application = await _application(tmp_path)
    try:
        tank = await application.create_tank("Veril", "user-1")
        session = await application.start_session("user-1", tank["tank_id"], "sample-1")
        first = await application.record_observation(
            "user-1",
            tank_id=tank["tank_id"],
            parameter="alkalinity",
            reported_value=7.2,
            unit="dKH",
            qualifier="<",
            measurement_time=None,
            method_id="salifert",
            instrument_id="kit-1",
            session_id=session["session_id"],
        )
        second = await application.record_observation(
            "user-1",
            tank_id=tank["tank_id"],
            parameter="calcium",
            reported_value=425,
            unit="mg/L",
            session_id=session["session_id"],
        )

        observations = await application.list_observations(tank["tank_id"])
        assert [item["observation_id"] for item in observations] == [
            first["observation_id"],
            second["observation_id"],
        ]
        assert first["source"] == "manual"
        assert first["qualifier"] == "<"
        assert first["measurement_time"] is None
        assert first["recording_time"] is not None
        assert second["session_id"] == session["session_id"]
    finally:
        await hass.async_stop()


@pytest.mark.asyncio
async def test_observation_correction_preserves_identity_and_delete_dependencies(
    tmp_path: Path,
) -> None:
    hass, application = await _application(tmp_path)
    try:
        tank = await application.create_tank("Veril", "user-1")
        location = await application.create_location("user-1", tank["tank_id"], "Display")
        observation = await application.record_observation(
            "user-1",
            tank_id=tank["tank_id"],
            parameter="pH",
            reported_value=8.1,
            location_id=location["location_id"],
        )
        corrected = await application.update_observation(
            "user-1", observation["observation_id"], {"reported_value": 8.2}
        )
        assert corrected["observation_id"] == observation["observation_id"]
        assert corrected["source"] == "manual"

        with pytest.raises(DependencyError):
            await application.delete_location("user-1", location["location_id"])
        await application.delete_observation("user-1", observation["observation_id"])
        await application.delete_location("user-1", location["location_id"])
        assert await application.list_observations(tank["tank_id"]) == []
    finally:
        await hass.async_stop()


@pytest.mark.asyncio
async def test_failed_atomic_save_does_not_replace_previous_canonical_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hass, application = await _application(tmp_path)
    try:
        await application.create_tank("Veril", "user-1")
        storage_path = tmp_path / ".storage" / "tank_os.data"
        previous = json.loads(storage_path.read_text())

        def fail_atomic_write(*args: object, **kwargs: object) -> None:
            raise storage.WriteError("simulated write failure")

        monkeypatch.setattr(storage, "write_utf8_file_atomic", fail_atomic_write)
        with pytest.raises(PersistenceError):
            await application.create_tank("Failed", "user-1")

        assert json.loads(storage_path.read_text()) == previous
    finally:
        await hass.async_stop()


@pytest.mark.asyncio
async def test_repository_reload_preserves_versioned_canonical_records(
    tmp_path: Path,
) -> None:
    hass, application = await _application(tmp_path)
    try:
        await application.create_tank("user-1", "Veril")
        reloaded = CanonicalRepository(hass)
        data = await reloaded.async_load()
        assert data["tanks"][0]["name"] == "Veril"
        storage_file = tmp_path / ".storage" / "tank_os.data"
        stored = json.loads(storage_file.read_text())
        assert stored["version"] == 1
        assert stored["minor_version"] == 1
    finally:
        await hass.async_stop()


@pytest.mark.asyncio
async def test_home_assistant_store_migration_rewrites_versioned_payload(
    tmp_path: Path,
) -> None:
    hass = HomeAssistant(str(tmp_path))
    await hass.async_start()
    try:
        storage_file = tmp_path / ".storage" / "tank_os.migration"
        storage_file.parent.mkdir()
        storage_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "minor_version": 1,
                    "key": "tank_os.migration",
                    "data": {"tanks": []},
                }
            )
        )

        store = Store(hass, 2, "tank_os.migration", atomic_writes=True)

        async def migrate(
            old_major: int, old_minor: int, old_data: dict[str, object]
        ) -> dict[str, object]:
            assert (old_major, old_minor) == (1, 1)
            return {**old_data, "locations": []}

        store._async_migrate_func = migrate
        assert await store.async_load() == {"tanks": [], "locations": []}
        rewritten = json.loads(storage_file.read_text())
        assert rewritten["version"] == 2
        assert rewritten["data"]["locations"] == []
    finally:
        await hass.async_stop()


@pytest.mark.asyncio
async def test_invalid_observation_is_rejected_without_persisting(tmp_path: Path) -> None:
    hass, application = await _application(tmp_path)
    try:
        tank = await application.create_tank("Veril", "user-1")
        with pytest.raises(DomainValidationError):
            await application.record_observation(
                "user-1",
                tank_id=tank["tank_id"],
                parameter="pH",
                reported_value="",
            )
        assert await application.list_observations(tank["tank_id"]) == []
    finally:
        await hass.async_stop()
