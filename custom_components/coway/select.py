"""Select platform for Coway integration."""
from __future__ import annotations

import asyncio
from typing import Any

from cowayaio.exceptions import CowayError
from cowayaio.purifier_model import CowayPurifier

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COWAY_COORDINATOR,
    DOMAIN,
    IOCARE_LIGHT_MODES,
    IOCARE_LIGHT_MODES_EXTENDED,
    IOCARE_LIGHT_MODES_TO_HASS,
    IOCARE_PRE_FILTER_TO_HASS,
    IOCARE_PRE_FILTER_WASH_FREQUENCIES,
    IOCARE_SMART_SENSITIVITIES,
    IOCARE_SMART_SENSITIVITY_TO_HASS,
    IOCARE_TIMERS,
    IOCARE_TIMERS_TO_HASS,
)
from .coordinator import CowayDataUpdateCoordinator


HASS_TIMER_TO_IOCARE = {v: k for (k, v) in IOCARE_TIMERS_TO_HASS.items()}
HASS_PRE_FILTER_TO_IOCARE = {v: k for (k, v) in IOCARE_PRE_FILTER_TO_HASS.items()}
HASS_SMART_SENSITIVITY_TO_IOCARE = {v: k for (k, v) in IOCARE_SMART_SENSITIVITY_TO_HASS.items()}
HASS_LIGHT_MODE_TO_IOCARE = {v: k for (k, v) in IOCARE_LIGHT_MODES_TO_HASS.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Coway Select Entities."""

    coordinator: CowayDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][COWAY_COORDINATOR]

    selects = []

    for purifier_id, purifier_data in coordinator.data.purifiers.items():
            model = purifier_data.device_attr['model']
            # 250S/IconS purifiers have multiple light modes
            if model in ['Airmega 250S', 'Airmega IconS']:
                selects.append(Light(coordinator, purifier_id))
            # Filter endpoint is currently under development by Coway for 250S
            if purifier_data.pre_filter_change_frequency is not None:
                # UK (02FMG), Europe (02FMF, 02FWN) AP-1512HHS models don't have pre-filter
                if purifier_data.device_attr['code'] not in ['02FMG','02FMF', '02FWN']:
                    selects.append(PreFilterFrequency(coordinator, purifier_id))
            selects.extend((
                Timer(coordinator, purifier_id),
                SmartModeSensitivity(coordinator, purifier_id),
            ))

    async_add_entities(selects)

class Timer(CoordinatorEntity, SelectEntity):
    """Representation of purifier timer."""

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

        return self.purifier_data.device_attr['device_id'] + '_timer'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Current timer"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.current_option == "OFF":
            return 'mdi:timer-off'
        else:
            return 'mdi:timer'

    @property
    def current_option(self) -> str:
        """Returns currently active timer."""

        return IOCARE_TIMERS_TO_HASS.get(self.purifier_data.timer)

    @property
    def options(self) -> list:
        """Return list of all the available timers."""

        return IOCARE_TIMERS

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        if self.purifier_data.is_on:
            time = HASS_TIMER_TO_IOCARE.get(option)
            try:
                await self.coordinator.client.async_set_timer(
                    self.purifier_data.device_attr,
                    time
                )
            except CowayError as ex:
                raise HomeAssistantError(ex)
            self.purifier_data.timer = time
            self.purifier_data.timer_remaining = time
        else:
            raise HomeAssistantError(
                f'Setting a timer for {self.purifier_data.device_attr["name"]} '
                f'can only be done when the purifier is On.'
            )

        self.async_write_ha_state()
        await asyncio.sleep(3)
        await self.coordinator.async_request_refresh()


class PreFilterFrequency(CoordinatorEntity, SelectEntity):
    """Representation of pre-filter wash frequency."""

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

        return self.purifier_data.device_attr['device_id'] + '_pre_filter_frequency'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Pre-filter wash frequency"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:dishwasher'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def current_option(self) -> str:
        """Returns current wash frequency."""

        return IOCARE_PRE_FILTER_TO_HASS.get(self.purifier_data.pre_filter_change_frequency)

    @property
    def options(self) -> list:
        """Return list of all the available wash frequencies."""

        return IOCARE_PRE_FILTER_WASH_FREQUENCIES

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        if self.purifier_data.is_on:
            wash_frequency = HASS_PRE_FILTER_TO_IOCARE.get(option)
            try:
                await self.coordinator.client.async_change_prefilter_setting(
                    self.purifier_data.device_attr,
                    wash_frequency
                )
            except CowayError as ex:
                raise HomeAssistantError(ex)
            self.purifier_data.pre_filter_change_frequency = wash_frequency
        else:
            raise HomeAssistantError(
                f'Setting a pre-filter wash frequency for {self.purifier_data.device_attr["name"]} '
                f'can only be done when the purifier is On.'
            )

        self.async_write_ha_state()
        await asyncio.sleep(3)
        await self.coordinator.async_request_refresh()


class SmartModeSensitivity(CoordinatorEntity, SelectEntity):
    """Representation of smart mode sensitivity."""

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

        return self.purifier_data.device_attr['device_id'] + '_smart_mode_sensitivity'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Smart mode sensitivity"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:scale-bathroom'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def current_option(self) -> str:
        """Returns current smart mode sensitivity."""

        return IOCARE_SMART_SENSITIVITY_TO_HASS.get(self.purifier_data.smart_mode_sensitivity)

    @property
    def options(self) -> list:
        """Return list of all the available sensitivities."""

        return IOCARE_SMART_SENSITIVITIES

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        if self.purifier_data.is_on:
            sensitivity = HASS_SMART_SENSITIVITY_TO_IOCARE.get(option)
            try:
                await self.coordinator.client.async_set_smart_mode_sensitivity(
                    self.purifier_data.device_attr,
                    str(sensitivity)
                )
            except CowayError as ex:
                raise HomeAssistantError(ex)
            self.purifier_data.smart_mode_sensitivity = sensitivity
        else:
            raise HomeAssistantError(
                f'Setting smart mode sensitivity for {self.purifier_data.device_attr["name"]} '
                f'can only be done when the purifier is On.'
            )

        self.async_write_ha_state()
        await asyncio.sleep(3)
        await self.coordinator.async_request_refresh()


class Light(CoordinatorEntity, SelectEntity):
    """Representation of selecting light mode. Currently only used
       by 250S/IconS purifiers.
    """

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
        """Set icon."""

        return 'mdi:lightbulb'

    @property
    def current_option(self) -> str:
        """Returns current light mode."""

        return IOCARE_LIGHT_MODES_TO_HASS.get(str(self.purifier_data.light_mode))

    @property
    def options(self) -> list:
        """Return list of all the available light modes."""

        if self.purifier_data.device_attr['model'] == 'Airmega 250S':
            return IOCARE_LIGHT_MODES
        else:
            return IOCARE_LIGHT_MODES_EXTENDED

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        if self.purifier_data.is_on:
            mode = HASS_LIGHT_MODE_TO_IOCARE.get(option)
            try:
                await self.coordinator.client.async_set_light_mode(
                    self.purifier_data.device_attr,
                    mode
                )
            except CowayError as ex:
                raise HomeAssistantError(ex)
            self.purifier_data.light_mode = int(mode)
        else:
            raise HomeAssistantError(
                f'Setting light mode for {self.purifier_data.device_attr["name"]} '
                f'can only be done when the purifier is On.'
            )

        self.async_write_ha_state()
        await asyncio.sleep(3)
        await self.coordinator.async_request_refresh()
