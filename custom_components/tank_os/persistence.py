"""Canonical persistence adapter built on Home Assistant's atomic Store."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_MINOR_VERSION, STORAGE_VERSION


class PersistenceError(RuntimeError):
    """Raised when canonical data cannot be confirmed on disk."""


class TankOsStore(Store[dict[str, Any]]):
    """Versioned Home Assistant storage for canonical domain records."""

    async def _async_migrate_func(
        self,
        old_major_version: int,
        old_minor_version: int,
        old_data: dict[str, Any],
    ) -> dict[str, Any]:
        if old_major_version == STORAGE_VERSION and old_minor_version <= STORAGE_MINOR_VERSION:
            return old_data
        raise NotImplementedError(
            f"No migration exists for storage version {old_major_version}.{old_minor_version}"
        )


class CanonicalRepository:
    """Serialize canonical records through one transactional application boundary."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = TankOsStore(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
            atomic_writes=True,
            minor_version=STORAGE_MINOR_VERSION,
        )
        self._lock = asyncio.Lock()
        self._data: dict[str, Any] | None = None

    async def async_load(self) -> dict[str, Any]:
        async with self._lock:
            if self._data is None:
                self._data = await self._store.async_load() or self._empty_data()
            return self._copy(self._data)

    async def async_save(self, data: dict[str, Any]) -> None:
        async with self._lock:
            candidate = self._copy(data)
            await self._store.async_save(candidate)
            persisted = await self._store.async_load()
            if persisted != candidate:
                raise PersistenceError("canonical data could not be confirmed after save")
            self._data = persisted

    @staticmethod
    def _empty_data() -> dict[str, Any]:
        return {"tanks": [], "locations": [], "sessions": [], "observations": []}

    @staticmethod
    def _copy(data: dict[str, Any]) -> dict[str, Any]:
        return {
            "tanks": list(data.get("tanks", [])),
            "locations": list(data.get("locations", [])),
            "sessions": list(data.get("sessions", [])),
            "observations": list(data.get("observations", [])),
        }
