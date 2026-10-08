"""Application commands and queries for the first ha-tank-os slice."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from .const import SOURCE_MANUAL
from .domain import (
    DependencyError,
    DomainLocation,
    DomainValidationError,
    MeasurementSession,
    Observation,
    Tank,
)
from .persistence import CanonicalRepository


class AuthorizationError(PermissionError):
    """Raised when a mutation has no Home Assistant user context."""


class ApplicationService:
    """Expose all canonical mutations and queries through one application service."""

    def __init__(self, repository: CanonicalRepository) -> None:
        self._repository = repository
        self._mutation_lock = asyncio.Lock()

    @asynccontextmanager
    async def _mutation(self) -> AsyncIterator[dict[str, Any]]:
        """Serialize read-modify-write operations as one application mutation."""
        async with self._mutation_lock:
            data = await self._repository.async_load()
            try:
                yield data
            except BaseException:
                raise
            else:
                await self._repository.async_save(data)

    @staticmethod
    def require_user(user_id: str | None) -> None:
        if not user_id:
            raise AuthorizationError("a Home Assistant user context is required")

    async def create_tank(self, user_id: str | None, name: str) -> dict[str, Any]:
        self.require_user(user_id)
        async with self._mutation() as data:
            tank = Tank.create(name)
            data["tanks"].append(tank.as_dict())
            return tank.as_dict()

    async def list_tanks(self) -> list[dict[str, Any]]:
        return list((await self._repository.async_load())["tanks"])

    async def update_tank(self, user_id: str | None, tank_id: str, name: str) -> dict[str, Any]:
        self.require_user(user_id)
        async with self._mutation() as data:
            for index, stored in enumerate(data["tanks"]):
                if stored["tank_id"] == tank_id:
                    tank = Tank.from_dict(stored).rename(name)
                    data["tanks"][index] = tank.as_dict()
                    return tank.as_dict()
            raise DomainValidationError(f"unknown tank: {tank_id}")

    async def delete_tank(self, user_id: str | None, tank_id: str) -> None:
        self.require_user(user_id)
        async with self._mutation() as data:
            if any(
                item["tank_id"] == tank_id
                for item in data["locations"] + data["observations"] + data["sessions"]
            ):
                raise DependencyError(f"tank has active dependent records: {tank_id}")
            original = len(data["tanks"])
            data["tanks"] = [item for item in data["tanks"] if item["tank_id"] != tank_id]
            if len(data["tanks"]) == original:
                raise DomainValidationError(f"unknown tank: {tank_id}")

    async def create_location(self, user_id: str | None, tank_id: str, name: str) -> dict[str, Any]:
        self.require_user(user_id)
        async with self._mutation() as data:
            self._require_tank(data, tank_id)
            location = DomainLocation.create(tank_id, name)
            data["locations"].append(location.as_dict())
            return location.as_dict()

    async def list_context(self, tank_id: str | None = None) -> dict[str, Any]:
        data = await self._repository.async_load()
        if tank_id is None:
            return {"tanks": data["tanks"], "locations": data["locations"]}
        self._require_tank(data, tank_id)
        return {
            "tanks": [item for item in data["tanks"] if item["tank_id"] == tank_id],
            "locations": [item for item in data["locations"] if item["tank_id"] == tank_id],
        }

    async def update_location(
        self, user_id: str | None, location_id: str, name: str
    ) -> dict[str, Any]:
        self.require_user(user_id)
        async with self._mutation() as data:
            for index, stored in enumerate(data["locations"]):
                if stored["location_id"] == location_id:
                    location = DomainLocation.from_dict(stored).rename(name)
                    data["locations"][index] = location.as_dict()
                    return location.as_dict()
            raise DomainValidationError(f"unknown location: {location_id}")

    async def delete_location(self, user_id: str | None, location_id: str) -> None:
        self.require_user(user_id)
        async with self._mutation() as data:
            if any(item.get("location_id") == location_id for item in data["observations"]):
                raise DependencyError(f"location has active observations: {location_id}")
            original = len(data["locations"])
            data["locations"] = [
                item for item in data["locations"] if item["location_id"] != location_id
            ]
            if len(data["locations"]) == original:
                raise DomainValidationError(f"unknown location: {location_id}")

    async def start_session(
        self, user_id: str | None, tank_id: str, sample_id: str | None = None
    ) -> dict[str, Any]:
        self.require_user(user_id)
        async with self._mutation() as data:
            self._require_tank(data, tank_id)
            session = MeasurementSession.create(tank_id, sample_id)
            data["sessions"].append(session.as_dict())
            return session.as_dict()

    async def record_observation(
        self,
        user_id: str | None,
        *,
        tank_id: str,
        parameter: str,
        reported_value: Any,
        unit: str | None = None,
        qualifier: str | None = None,
        measurement_time: str | None = None,
        location_id: str | None = None,
        sample_id: str | None = None,
        method_id: str | None = None,
        instrument_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        self.require_user(user_id)
        async with self._mutation() as data:
            self._require_tank(data, tank_id)
            if location_id is not None and not any(
                item["location_id"] == location_id and item["tank_id"] == tank_id
                for item in data["locations"]
            ):
                raise DomainValidationError(f"unknown location for tank: {location_id}")
            if session_id is not None and not any(
                item["session_id"] == session_id and item["tank_id"] == tank_id
                for item in data["sessions"]
            ):
                raise DomainValidationError(f"unknown session for tank: {session_id}")
            observation = Observation.create(
                tank_id=tank_id,
                parameter=parameter,
                reported_value=reported_value,
                source=SOURCE_MANUAL,
                recording_time=datetime.now(UTC),
                unit=unit,
                qualifier=qualifier,
                measurement_time=measurement_time,
                location_id=location_id,
                sample_id=sample_id,
                method_id=method_id,
                instrument_id=instrument_id,
                session_id=session_id,
            )
            data["observations"].append(observation.as_dict())
            return observation.as_dict()

    async def list_observations(
        self, tank_id: str, parameter: str | None = None
    ) -> list[dict[str, Any]]:
        data = await self._repository.async_load()
        self._require_tank(data, tank_id)
        observations = [item for item in data["observations"] if item["tank_id"] == tank_id]
        if parameter is not None:
            observations = [item for item in observations if item["parameter"] == parameter]
        return observations

    async def update_observation(
        self, user_id: str | None, observation_id: str, changes: dict[str, Any]
    ) -> dict[str, Any]:
        self.require_user(user_id)
        async with self._mutation() as data:
            for index, stored in enumerate(data["observations"]):
                if stored["observation_id"] == observation_id:
                    if "tank_id" in changes or "source" in changes:
                        raise DomainValidationError("tank_id and source cannot be changed")
                    observation = Observation.from_dict(stored).corrected(**changes)
                    data["observations"][index] = observation.as_dict()
                    return observation.as_dict()
            raise DomainValidationError(f"unknown observation: {observation_id}")

    async def delete_observation(self, user_id: str | None, observation_id: str) -> None:
        self.require_user(user_id)
        async with self._mutation() as data:
            original = len(data["observations"])
            data["observations"] = [
                item for item in data["observations"] if item["observation_id"] != observation_id
            ]
            if len(data["observations"]) == original:
                raise DomainValidationError(f"unknown observation: {observation_id}")

    @staticmethod
    def _require_tank(data: dict[str, Any], tank_id: str) -> None:
        if not any(item["tank_id"] == tank_id for item in data["tanks"]):
            raise DomainValidationError(f"unknown tank: {tank_id}")
