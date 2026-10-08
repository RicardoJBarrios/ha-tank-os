"""Domain records and validation for ha-tank-os."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


class DomainValidationError(ValueError):
    """Raised when a domain record cannot be interpreted safely."""


class DependencyError(DomainValidationError):
    """Raised when removing a record would break an active relationship."""


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DomainValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    return _required_text(value, "value")


def _parse_datetime(value: str | None, field_name: str) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise DomainValidationError(f"{field_name} must be an ISO-8601 string")
    try:
        return datetime.fromisoformat(value)
    except ValueError as err:
        raise DomainValidationError(f"{field_name} must be an ISO-8601 string") from err


def _datetime_text(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


@dataclass(frozen=True, slots=True)
class Tank:
    """A managed aquarium with a product-owned identity."""

    tank_id: str
    name: str

    @classmethod
    def create(cls, name: str) -> Tank:
        return cls(_new_id("tank"), _required_text(name, "name"))

    def rename(self, name: str) -> Tank:
        return Tank(self.tank_id, _required_text(name, "name"))

    def as_dict(self) -> dict[str, str]:
        return {"tank_id": self.tank_id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tank:
        return cls(
            _required_text(data["tank_id"], "tank_id"),
            _required_text(data["name"], "name"),
        )


@dataclass(frozen=True, slots=True)
class DomainLocation:
    """A physical or logical place associated with a Tank."""

    location_id: str
    tank_id: str
    name: str

    @classmethod
    def create(cls, tank_id: str, name: str) -> DomainLocation:
        return cls(
            _new_id("location"),
            _required_text(tank_id, "tank_id"),
            _required_text(name, "name"),
        )

    def rename(self, name: str) -> DomainLocation:
        return DomainLocation(self.location_id, self.tank_id, _required_text(name, "name"))

    def as_dict(self) -> dict[str, str]:
        return {
            "location_id": self.location_id,
            "tank_id": self.tank_id,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DomainLocation:
        return cls(
            _required_text(data["location_id"], "location_id"),
            _required_text(data["tank_id"], "tank_id"),
            _required_text(data["name"], "name"),
        )


@dataclass(frozen=True, slots=True)
class MeasurementSession:
    """A partial or complete group of observations from one measurement session."""

    session_id: str
    tank_id: str
    sample_id: str | None = None

    @classmethod
    def create(cls, tank_id: str, sample_id: str | None = None) -> MeasurementSession:
        return cls(
            _new_id("session"), _required_text(tank_id, "tank_id"), _optional_text(sample_id)
        )

    def as_dict(self) -> dict[str, str | None]:
        return {
            "session_id": self.session_id,
            "tank_id": self.tank_id,
            "sample_id": self.sample_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MeasurementSession:
        return cls(
            _required_text(data["session_id"], "session_id"),
            _required_text(data["tank_id"], "tank_id"),
            _optional_text(data.get("sample_id")),
        )


@dataclass(frozen=True, slots=True)
class Observation:
    """An original attributed manual observation."""

    observation_id: str
    tank_id: str
    parameter: str
    reported_value: Any
    source: str
    unit: str | None = None
    qualifier: str | None = None
    measurement_time: datetime | None = None
    recording_time: datetime = field(default_factory=datetime.now)
    location_id: str | None = None
    sample_id: str | None = None
    method_id: str | None = None
    instrument_id: str | None = None
    session_id: str | None = None

    @classmethod
    def create(
        cls,
        *,
        tank_id: str,
        parameter: str,
        reported_value: Any,
        source: str,
        recording_time: datetime,
        unit: str | None = None,
        qualifier: str | None = None,
        measurement_time: str | None = None,
        location_id: str | None = None,
        sample_id: str | None = None,
        method_id: str | None = None,
        instrument_id: str | None = None,
        session_id: str | None = None,
    ) -> Observation:
        if reported_value is None or reported_value == "":
            raise DomainValidationError("reported_value must be interpretable")
        return cls(
            observation_id=_new_id("observation"),
            tank_id=_required_text(tank_id, "tank_id"),
            parameter=_required_text(parameter, "parameter"),
            reported_value=reported_value,
            source=_required_text(source, "source"),
            unit=_optional_text(unit),
            qualifier=_optional_text(qualifier),
            measurement_time=_parse_datetime(measurement_time, "measurement_time"),
            recording_time=recording_time,
            location_id=_optional_text(location_id),
            sample_id=_optional_text(sample_id),
            method_id=_optional_text(method_id),
            instrument_id=_optional_text(instrument_id),
            session_id=_optional_text(session_id),
        )

    def corrected(self, **changes: Any) -> Observation:
        values = self.as_dict()
        values.update(changes)
        values["measurement_time"] = _parse_datetime(
            values.get("measurement_time"), "measurement_time"
        )
        values["recording_time"] = _parse_datetime(values["recording_time"], "recording_time")
        values.pop("observation_id", None)
        return Observation(observation_id=self.observation_id, **values)

    def as_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "tank_id": self.tank_id,
            "parameter": self.parameter,
            "reported_value": self.reported_value,
            "source": self.source,
            "unit": self.unit,
            "qualifier": self.qualifier,
            "measurement_time": _datetime_text(self.measurement_time),
            "recording_time": _datetime_text(self.recording_time),
            "location_id": self.location_id,
            "sample_id": self.sample_id,
            "method_id": self.method_id,
            "instrument_id": self.instrument_id,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Observation:
        recording_time = _parse_datetime(data.get("recording_time"), "recording_time")
        if recording_time is None:
            raise DomainValidationError("recording_time is required")
        return cls.create(
            tank_id=data["tank_id"],
            parameter=data["parameter"],
            reported_value=data.get("reported_value"),
            source=data["source"],
            recording_time=recording_time,
            unit=data.get("unit"),
            qualifier=data.get("qualifier"),
            measurement_time=data.get("measurement_time"),
            location_id=data.get("location_id"),
            sample_id=data.get("sample_id"),
            method_id=data.get("method_id"),
            instrument_id=data.get("instrument_id"),
            session_id=data.get("session_id"),
        )._with_id(_required_text(data["observation_id"], "observation_id"))

    def _with_id(self, observation_id: str) -> Observation:
        return Observation(observation_id=observation_id, **self.as_dict_without_id())

    def as_dict_without_id(self) -> dict[str, Any]:
        values = self.as_dict()
        values.pop("observation_id", None)
        values["measurement_time"] = self.measurement_time
        values["recording_time"] = self.recording_time
        return values
