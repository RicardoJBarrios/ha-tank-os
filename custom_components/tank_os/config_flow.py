"""Config flow for ha-tank-os."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import DOMAIN


class TankOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle installation of the ha-tank-os integration."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> TankOsOptionsFlow:
        """Create the options flow for source associations."""
        return TankOsOptionsFlow()

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> ConfigFlowResult:
        """Create the single integration repository configuration."""
        if user_input is not None:
            await self.async_set_unique_id("default")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="ha-tank-os", data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))


class TankOsOptionsFlow(config_entries.OptionsFlowWithReload):
    """Configure source entity associations without storing domain records."""

    _ASSOCIATIONS_KEY = "source_associations"

    def __init__(self) -> None:
        """Initialize transient edit state."""
        self._association_index: int | None = None

    def _associations(self) -> list[dict[str, str]]:
        """Return a validated copy of saved associations."""
        saved = self.config_entry.options.get(self._ASSOCIATIONS_KEY, [])
        if not isinstance(saved, list):
            return []
        return [
            {"entity_id": item["entity_id"], "target": item["target"]}
            for item in saved
            if isinstance(item, dict)
            and isinstance(item.get("entity_id"), str)
            and isinstance(item.get("target"), str)
        ]

    async def _targets(self) -> tuple[list[SelectOptionDict], dict[str, str]]:
        """Build stable target options and labels from canonical context."""
        application = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        if application is None:
            return [], {}

        context = await application.list_context()
        choices: list[SelectOptionDict] = []
        labels: dict[str, str] = {}
        for tank in context["tanks"]:
            value = f"tank:{tank['tank_id']}"
            label = tank["name"]
            choices.append({"value": value, "label": label})
            labels[value] = label
        for location in context["locations"]:
            value = f"location:{location['location_id']}"
            tank = next(
                (item for item in context["tanks"] if item["tank_id"] == location["tank_id"]),
                None,
            )
            prefix = f"{tank['name']} / " if tank else ""
            label = f"{prefix}{location['name']}"
            choices.append({"value": value, "label": label})
            labels[value] = label
        return choices, labels

    @staticmethod
    def _is_source_available(hass: HomeAssistant, entity_id: str) -> bool:
        """Check that Home Assistant currently has a state for the entity."""
        return hass.states.get(entity_id) is not None

    async def _association_choices(self) -> list[SelectOptionDict]:
        """Build edit/remove choices, preserving stale references visibly."""
        _, labels = await self._targets()
        choices: list[SelectOptionDict] = []
        for index, association in enumerate(self._associations()):
            target_label = labels.get(association["target"], association["target"])
            warning = (
                "⚠ "
                if (
                    association["target"] not in labels
                    or not self._is_source_available(self.hass, association["entity_id"])
                )
                else ""
            )
            choices.append(
                {
                    "value": str(index),
                    "label": f"{warning}{association['entity_id']} → {target_label}",
                }
            )
        return choices

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Show association actions."""
        menu_options = ["add", "finish"]
        if self._associations():
            menu_options[1:1] = ["edit", "remove"]
        return self.async_show_menu(step_id="init", menu_options=menu_options)

    async def async_step_finish(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Finish without changing options."""
        return self.async_create_entry(title="", data=dict(self.config_entry.options))

    async def async_step_add(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Add an entity-to-context association."""
        targets, _ = await self._targets()
        if not targets:
            return self.async_show_form(
                step_id="add",
                data_schema=vol.Schema({}),
                errors={"base": "no_targets"},
            )

        if user_input is not None:
            entity_id = user_input["entity_id"]
            target = user_input["target"]
            if not self._is_source_available(self.hass, entity_id):
                return self.async_show_form(
                    step_id="add",
                    data_schema=self._association_schema(targets),
                    errors={"base": "entity_not_found"},
                )
            if target not in {item["value"] for item in targets}:
                return self.async_show_form(
                    step_id="add",
                    data_schema=self._association_schema(targets),
                    errors={"base": "target_not_found"},
                )
            associations = self._associations()
            if any(
                item["entity_id"] == entity_id and item["target"] == target for item in associations
            ):
                return self.async_show_form(
                    step_id="add",
                    data_schema=self._association_schema(targets),
                    errors={"base": "already_associated"},
                )
            associations.append({"entity_id": entity_id, "target": target})
            return self._save_associations(associations)

        return self.async_show_form(step_id="add", data_schema=self._association_schema(targets))

    @staticmethod
    def _association_schema(targets: list[SelectOptionDict]) -> vol.Schema:
        """Build a native entity and aquarium-target selector form."""
        return vol.Schema(
            {
                vol.Required("entity_id"): EntitySelector(EntitySelectorConfig()),
                vol.Required("target"): SelectSelector(
                    SelectSelectorConfig(options=targets, mode=SelectSelectorMode.DROPDOWN)
                ),
            }
        )

    async def async_step_edit(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Choose an existing association to edit."""
        choices = await self._association_choices()
        if not choices:
            return self.async_show_form(
                step_id="edit", data_schema=vol.Schema({}), errors={"base": "no_associations"}
            )
        if user_input is None:
            return self.async_show_form(
                step_id="edit",
                data_schema=vol.Schema(
                    {
                        vol.Required("association_index"): SelectSelector(
                            SelectSelectorConfig(options=choices, mode=SelectSelectorMode.DROPDOWN)
                        )
                    }
                ),
            )
        self._association_index = int(user_input["association_index"])
        return await self.async_step_edit_entry()

    async def async_step_edit_entry(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update the source or target of an existing association."""
        associations = self._associations()
        if self._association_index is None or not 0 <= self._association_index < len(associations):
            return self.async_abort(reason="association_not_found")
        targets, _ = await self._targets()
        current = associations[self._association_index]
        target_values = {item["value"] for item in targets}
        if current["target"] not in target_values:
            targets = [*targets, {"value": current["target"], "label": f"⚠ {current['target']}"}]

        if user_input is not None:
            entity_id = user_input["entity_id"]
            if not self._is_source_available(self.hass, entity_id):
                return self.async_show_form(
                    step_id="edit_entry",
                    data_schema=self._association_schema(targets),
                    errors={"base": "entity_not_found"},
                )
            target = user_input["target"]
            if target not in target_values:
                return self.async_show_form(
                    step_id="edit_entry",
                    data_schema=self._association_schema(targets),
                    errors={"base": "target_not_found"},
                )
            if any(
                index != self._association_index
                and item["entity_id"] == entity_id
                and item["target"] == target
                for index, item in enumerate(associations)
            ):
                return self.async_show_form(
                    step_id="edit_entry",
                    data_schema=self._association_schema(targets),
                    errors={"base": "already_associated"},
                )
            associations[self._association_index] = {"entity_id": entity_id, "target": target}
            return self._save_associations(associations)

        schema = vol.Schema(
            {
                vol.Required("entity_id", default=current["entity_id"]): EntitySelector(
                    EntitySelectorConfig()
                ),
                vol.Required("target", default=current["target"]): SelectSelector(
                    SelectSelectorConfig(options=targets, mode=SelectSelectorMode.DROPDOWN)
                ),
            }
        )
        return self.async_show_form(step_id="edit_entry", data_schema=schema)

    async def async_step_remove(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Remove an existing association."""
        choices = await self._association_choices()
        if not choices:
            return self.async_show_form(
                step_id="remove", data_schema=vol.Schema({}), errors={"base": "no_associations"}
            )
        schema = vol.Schema(
            {
                vol.Required("association_index"): SelectSelector(
                    SelectSelectorConfig(options=choices, mode=SelectSelectorMode.DROPDOWN)
                )
            }
        )
        if user_input is None:
            return self.async_show_form(step_id="remove", data_schema=schema)
        index = int(user_input["association_index"])
        associations = self._associations()
        if not 0 <= index < len(associations):
            return self.async_abort(reason="association_not_found")
        associations.pop(index)
        return self._save_associations(associations)

    def _save_associations(self, associations: list[dict[str, str]]) -> ConfigFlowResult:
        """Persist only integration configuration, never canonical records."""
        options = dict(self.config_entry.options)
        options[self._ASSOCIATIONS_KEY] = associations
        return self.async_create_entry(title="", data=options)
