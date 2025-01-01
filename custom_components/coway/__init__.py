"""Coway Component."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .const import (
    COWAY_COORDINATOR,
    DOMAIN,
    LOGGER,
    PLATFORMS,
    POLLING_INTERVAL,
    SKIP_PASSWORD_CHANGE,
    UPDATE_LISTENER,
)
from .coordinator import CowayDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Coway from a config entry."""

    coordinator = CowayDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        COWAY_COORDINATOR: coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    update_listener = entry.add_update_listener(async_update_options)
    hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER] = update_listener

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Coway config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        update_listener = hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER]
        update_listener()
        del hass.data[DOMAIN][entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""

    if entry.version == 1:
        username = entry.data[CONF_USERNAME]
        password = entry.data[CONF_PASSWORD]

        LOGGER.debug(f'Migrating Coway config entry unique id to {username}')

        hass.config_entries.async_update_entry(
            entry,
            version=4,
            data={
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
            },
            options={
                SKIP_PASSWORD_CHANGE: False,
                POLLING_INTERVAL: 120
            },
            unique_id=username,
        )
    if entry.version == 2:
        LOGGER.debug('Migrating Coway config: disabling skipping password change and setting polling interval of 120.')

        hass.config_entries.async_update_entry(
            entry,
            version=4,
            options={
                SKIP_PASSWORD_CHANGE: False,
                POLLING_INTERVAL: 120
            },
        )
    if entry.version == 3:
        LOGGER.debug('Migrating Coway config and setting polling interval to 120 seconds.')

        hass.config_entries.async_update_entry(
            entry,
            version=4,
            options={
                SKIP_PASSWORD_CHANGE: entry.options[SKIP_PASSWORD_CHANGE],
                POLLING_INTERVAL: 120
            },
        )
        
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """ Update options. """
    
    await hass.config_entries.async_reload(entry.entry_id)
