"""Switch platform for Coway integration."""
from __future__ import annotations

import asyncio
from typing import Any

from cowayaio.exceptions import CowayError
from cowayaio.purifier_model import CowayPurifier

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COWAY_COORDINATOR, DOMAIN
from .coordinator import CowayDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Coway Switch Entities."""

    coordinator: CowayDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][COWAY_COORDINATOR]

    switches = []

    for purifier_id, purifier_data in coordinator.data.purifiers.items():
        model = purifier_data.device_attr['model']
        if model not in ['Airmega 250S', 'Airmega IconS']:
            switches.append(PurifierLight(coordinator, purifier_id))
        if model == 'Airmega 250S':
            switches.append(ButtonLock(coordinator, purifier_id))

    async_add_entities(switches)


class PurifierLight(CoordinatorEntity, SwitchEntity):
    """Representation of purifier light switch."""

    def __init__(self, coordinator, purifier_id):
        super().__init__(coordinator)
        self.purifier_id = purifier_id

    @property
    def purifier_data(self) -> CowayPurifier:
        """Handle coordinator purifier data."""

        return self.coordinator.data.purifiers[self.purifier_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.purifier_data.device_attr['device_id'])},
            "name": self.purifier_data.device_attr['name'],
            "manufacturer": "Coway",
            "model": self.purifier_data.device_attr['model'],
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return self.purifier_data.device_attr['device_id'] + '_light'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Light"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set purifier switch icon to lightbulb."""

        if self.is_on:
            return 'mdi:led-on'
        elif self.purifier_data.is_on:
            return 'mdi:led-off'
        else:
            return 'mdi:led-variant-off'

    @property
    def is_on(self) -> bool:
        """Return true if light AND purifier are on."""

        if self.purifier_data.is_on and self.purifier_data.light_on:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""

        if self.purifier_data.is_on:
            try:
                await self.coordinator.client.async_set_light(
                    self.purifier_data.device_attr,
                    True
                )
            except CowayError as ex:
                raise HomeAssistantError(ex)
            self.purifier_data.light_on = True
        else:
            raise HomeAssistantError(
                f'{self.purifier_data.device_attr["name"]} '
                f'light can only be controlled when the purifier is On.'
            )

        self.async_write_ha_state()
        await asyncio.sleep(3)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""

        if self.purifier_data.is_on:
            try:
                await self.coordinator.client.async_set_light(
                    self.purifier_data.device_attr,
                    False
                )
            except CowayError as ex:
                raise HomeAssistantError(ex)
            self.purifier_data.light_on = False
        else:
            raise HomeAssistantError(
                f'{self.purifier_data.device_attr["name"]} '
                f'light can only be controlled when the purifier is On.'
            )

        self.async_write_ha_state()
        await asyncio.sleep(3)
        await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False


class ButtonLock(CoordinatorEntity, SwitchEntity):
    """Representation of 250S button lock switch."""

    def __init__(self, coordinator, purifier_id):
        super().__init__(coordinator)
        self.purifier_id = purifier_id

    @property
    def purifier_data(self) -> CowayPurifier:
        """Handle coordinator purifier data."""

        return self.coordinator.data.purifiers[self.purifier_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.purifier_data.device_attr['device_id'])},
            "name": self.purifier_data.device_attr['name'],
            "manufacturer": "Coway",
            "model": self.purifier_data.device_attr['model'],
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return self.purifier_data.device_attr['device_id'] + '_button_lock'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Button lock"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set purifier switch icon to button."""

        if self.is_on:
            return 'mdi:lock'
        else:
            return 'mdi:lock-off'

    @property
    def is_on(self) -> bool:
        """Return true if lock AND purifier are on."""

        if self.purifier_data.is_on and self.purifier_data.button_lock == 1:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""

        if self.purifier_data.is_on:
            try:
                await self.coordinator.client.async_set_button_lock(
                    self.purifier_data.device_attr,
                    '1'
                )
            except CowayError as ex:
                raise HomeAssistantError(ex)
            self.purifier_data.button_lock = 1
        else:
            raise HomeAssistantError(
                f'{self.purifier_data.device_attr["name"]} '
                f'button lock can only be controlled when the purifier is On.'
            )

        self.async_write_ha_state()
        await asyncio.sleep(3)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""

        if self.purifier_data.is_on:
            try:
                await self.coordinator.client.async_set_button_lock(
                    self.purifier_data.device_attr,
                    '0'
                )
            except CowayError as ex:
                raise HomeAssistantError(ex)
            self.purifier_data.button_lock = 0
        else:
            raise HomeAssistantError(
                f'{self.purifier_data.device_attr["name"]} '
                f'button lock can only be controlled when the purifier is On.'
            )

        self.async_write_ha_state()
        await asyncio.sleep(3)
        await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False
