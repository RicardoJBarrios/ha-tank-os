"""Home Assistant integration entry point for ha-tank-os."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, cast

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    EntityServiceResponse,
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.helpers import config_validation as cv

from .application import ApplicationService
from .const import (
    DOMAIN,
    SERVICE_CREATE_LOCATION,
    SERVICE_CREATE_TANK,
    SERVICE_DELETE_LOCATION,
    SERVICE_DELETE_OBSERVATION,
    SERVICE_DELETE_TANK,
    SERVICE_LIST_CONTEXT,
    SERVICE_LIST_OBSERVATIONS,
    SERVICE_LIST_TANKS,
    SERVICE_RECORD_OBSERVATION,
    SERVICE_START_SESSION,
    SERVICE_UPDATE_LOCATION,
    SERVICE_UPDATE_OBSERVATION,
    SERVICE_UPDATE_TANK,
)
from .persistence import CanonicalRepository

PLATFORMS: list[str] = []
RUNTIME_KEY = "runtime"
SERVICE_NAMES = (
    SERVICE_CREATE_TANK,
    SERVICE_LIST_TANKS,
    SERVICE_UPDATE_TANK,
    SERVICE_DELETE_TANK,
    SERVICE_CREATE_LOCATION,
    SERVICE_LIST_CONTEXT,
    SERVICE_UPDATE_LOCATION,
    SERVICE_DELETE_LOCATION,
    SERVICE_START_SESSION,
    SERVICE_RECORD_OBSERVATION,
    SERVICE_LIST_OBSERVATIONS,
    SERVICE_UPDATE_OBSERVATION,
    SERVICE_DELETE_OBSERVATION,
)

CONF_TANK_ID = vol.Required("tank_id")
CONF_NAME = vol.Required("name")
CONF_LOCATION_ID = vol.Required("location_id")
CONF_OBSERVATION_ID = vol.Required("observation_id")


def _name_schema() -> vol.Schema:
    return vol.Schema({CONF_NAME: cv.string})


def _register_service(
    hass: HomeAssistant,
    name: str,
    handler: Callable[[ServiceCall], Awaitable[Any]],
    schema: vol.Schema,
) -> None:
    service_handler = cast(
        Callable[
            [ServiceCall],
            Coroutine[Any, Any, ServiceResponse | EntityServiceResponse],
        ],
        handler,
    )
    hass.services.async_register(
        DOMAIN,
        name,
        service_handler,
        schema=schema,
        supports_response=SupportsResponse.OPTIONAL,
    )


def _user_id(call: ServiceCall) -> str | None:
    return call.context.user_id


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the domain; records are initialized by the config entry."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the canonical repository and native services."""
    repository = CanonicalRepository(hass)
    await repository.async_load()
    application = ApplicationService(repository)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = application

    def app(call: ServiceCall) -> ApplicationService:
        return hass.data[DOMAIN][entry.entry_id]

    async def create_tank(call: ServiceCall) -> dict[str, Any]:
        return {"tank": await app(call).create_tank(_user_id(call), call.data["name"])}

    async def list_tanks(call: ServiceCall) -> dict[str, Any]:
        return {"tanks": await app(call).list_tanks()}

    async def update_tank(call: ServiceCall) -> dict[str, Any]:
        return {
            "tank": await app(call).update_tank(
                _user_id(call), call.data["tank_id"], call.data["name"]
            )
        }

    async def delete_tank(call: ServiceCall) -> None:
        await app(call).delete_tank(_user_id(call), call.data["tank_id"])
        return None

    async def create_location(call: ServiceCall) -> dict[str, Any]:
        return {
            "location": await app(call).create_location(
                _user_id(call), call.data["tank_id"], call.data["name"]
            )
        }

    async def list_context(call: ServiceCall) -> dict[str, Any]:
        return {"context": await app(call).list_context(call.data.get("tank_id"))}

    async def update_location(call: ServiceCall) -> dict[str, Any]:
        return {
            "location": await app(call).update_location(
                _user_id(call), call.data["location_id"], call.data["name"]
            )
        }

    async def delete_location(call: ServiceCall) -> None:
        await app(call).delete_location(_user_id(call), call.data["location_id"])
        return None

    async def start_session(call: ServiceCall) -> dict[str, Any]:
        return {
            "session": await app(call).start_session(
                _user_id(call), call.data["tank_id"], call.data.get("sample_id")
            )
        }

    async def record_observation(call: ServiceCall) -> dict[str, Any]:
        data = dict(call.data)
        data.pop("tank_id")
        data.pop("parameter")
        data.pop("reported_value")
        return {
            "observation": await app(call).record_observation(
                _user_id(call),
                tank_id=call.data["tank_id"],
                parameter=call.data["parameter"],
                reported_value=call.data["reported_value"],
                **data,
            )
        }

    async def list_observations(call: ServiceCall) -> dict[str, Any]:
        return {
            "observations": await app(call).list_observations(
                call.data["tank_id"], call.data.get("parameter")
            )
        }

    async def update_observation(call: ServiceCall) -> dict[str, Any]:
        data = dict(call.data)
        observation_id = data.pop("observation_id")
        return {
            "observation": await app(call).update_observation(_user_id(call), observation_id, data)
        }

    async def delete_observation(call: ServiceCall) -> None:
        await app(call).delete_observation(_user_id(call), call.data["observation_id"])
        return None

    _register_service(hass, SERVICE_CREATE_TANK, create_tank, _name_schema())
    _register_service(hass, SERVICE_LIST_TANKS, list_tanks, vol.Schema({}))
    _register_service(
        hass,
        SERVICE_UPDATE_TANK,
        update_tank,
        vol.Schema({CONF_TANK_ID: cv.string, CONF_NAME: cv.string}),
    )
    _register_service(
        hass,
        SERVICE_DELETE_TANK,
        delete_tank,
        vol.Schema({CONF_TANK_ID: cv.string}),
    )
    _register_service(
        hass,
        SERVICE_CREATE_LOCATION,
        create_location,
        vol.Schema({CONF_TANK_ID: cv.string, CONF_NAME: cv.string}),
    )
    _register_service(
        hass,
        SERVICE_LIST_CONTEXT,
        list_context,
        vol.Schema({vol.Optional("tank_id"): cv.string}),
    )
    _register_service(
        hass,
        SERVICE_UPDATE_LOCATION,
        update_location,
        vol.Schema({CONF_LOCATION_ID: cv.string, CONF_NAME: cv.string}),
    )
    _register_service(
        hass,
        SERVICE_DELETE_LOCATION,
        delete_location,
        vol.Schema({CONF_LOCATION_ID: cv.string}),
    )
    _register_service(
        hass,
        SERVICE_START_SESSION,
        start_session,
        vol.Schema(
            {
                CONF_TANK_ID: cv.string,
                vol.Optional("sample_id"): cv.string,
            }
        ),
    )
    _register_service(
        hass,
        SERVICE_RECORD_OBSERVATION,
        record_observation,
        vol.Schema(
            {
                CONF_TANK_ID: cv.string,
                vol.Required("parameter"): cv.string,
                vol.Required("reported_value"): vol.Any(cv.string, vol.Coerce(float)),
                vol.Optional("unit"): cv.string,
                vol.Optional("qualifier"): cv.string,
                vol.Optional("measurement_time"): cv.string,
                vol.Optional("location_id"): cv.string,
                vol.Optional("sample_id"): cv.string,
                vol.Optional("method_id"): cv.string,
                vol.Optional("instrument_id"): cv.string,
                vol.Optional("session_id"): cv.string,
            }
        ),
    )
    _register_service(
        hass,
        SERVICE_LIST_OBSERVATIONS,
        list_observations,
        vol.Schema(
            {
                CONF_TANK_ID: cv.string,
                vol.Optional("parameter"): cv.string,
            }
        ),
    )
    _register_service(
        hass,
        SERVICE_UPDATE_OBSERVATION,
        update_observation,
        vol.Schema(
            {
                CONF_OBSERVATION_ID: cv.string,
                vol.Optional("parameter"): cv.string,
                vol.Optional("reported_value"): vol.Any(cv.string, vol.Coerce(float)),
                vol.Optional("unit"): vol.Any(cv.string, None),
                vol.Optional("qualifier"): vol.Any(cv.string, None),
                vol.Optional("measurement_time"): vol.Any(cv.string, None),
                vol.Optional("location_id"): vol.Any(cv.string, None),
                vol.Optional("sample_id"): vol.Any(cv.string, None),
                vol.Optional("method_id"): vol.Any(cv.string, None),
                vol.Optional("instrument_id"): vol.Any(cv.string, None),
                vol.Optional("session_id"): vol.Any(cv.string, None),
            }
        ),
    )
    _register_service(
        hass,
        SERVICE_DELETE_OBSERVATION,
        delete_observation,
        vol.Schema({CONF_OBSERVATION_ID: cv.string}),
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration services when its entry is removed."""
    runtime = hass.data.get(DOMAIN, {})
    runtime.pop(entry.entry_id, None)
    if not runtime:
        for service_name in SERVICE_NAMES:
            hass.services.async_remove(DOMAIN, service_name)
        hass.data.pop(DOMAIN, None)
    return True
