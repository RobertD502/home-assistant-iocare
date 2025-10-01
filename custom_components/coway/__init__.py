"""Coway Component."""
from __future__ import annotations


from datetime import datetime, timezone
import json
import os

from cowayaio.__version__ import __version__ as coway_aio_version

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .const import (
    COWAY_COORDINATOR,
    DOMAIN,
    LOGGER,
    MAINTENANCE_COOLDOWN,
    PLATFORMS,
    POLLING_INTERVAL,
    SKIP_PASSWORD_CHANGE,
    UPDATE_LISTENER,
)
from .coordinator import CowayDataUpdateCoordinator


curr_dir = os.path.dirname(__file__)
manifest_path = os.path.join(curr_dir, 'manifest.json')
with open(manifest_path, 'r') as file:
    json_file = json.load(file)
INTEGRATION_VERSION = json_file.get("version")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Coway from a config entry."""

    LOGGER.debug(
        f'Starting Coway integration {INTEGRATION_VERSION}/CowayAIO {coway_aio_version}'
    )

    null_maint_data = {
        **entry.data,
        MAINTENANCE_COOLDOWN: None
    }
    # Reset maintenance cooldown time during HA startups
    # if the time has expired
    if cooldown := entry.data[MAINTENANCE_COOLDOWN]:
        if datetime.now(timezone.utc).timestamp() > cooldown:
            hass.config_entries.async_update_entry(entry, data=null_maint_data)
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

        LOGGER.debug(
            f'Migrating Coway config entry unique id to {username}, disabling skipping password change, '
            f'setting polling interval of 120, and adding maintenance_cooldown key'
        )

        hass.config_entries.async_update_entry(
            entry,
            version=5,
            title=username,
            data={
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
                MAINTENANCE_COOLDOWN: None
            },
            options={
                SKIP_PASSWORD_CHANGE: False,
                POLLING_INTERVAL: 120
            },
            unique_id=username,
        )
    if entry.version == 2:
        LOGGER.debug(
            'Migrating Coway config: disabling skipping password change, setting polling '
            'interval of 120, and adding maintenance_cooldown key'
        )

        hass.config_entries.async_update_entry(
            entry,
            version=5,
            title=entry.data[CONF_USERNAME],
            data={
                CONF_USERNAME: entry.data[CONF_USERNAME],
                CONF_PASSWORD: entry.data[CONF_PASSWORD],
                MAINTENANCE_COOLDOWN: None
            },
            options={
                SKIP_PASSWORD_CHANGE: False,
                POLLING_INTERVAL: 120
            },
        )
    if entry.version == 3:
        LOGGER.debug(
            'Migrating Coway config: setting polling interval of '
            '120, and adding maintenance_cooldown key'
        )

        hass.config_entries.async_update_entry(
            entry,
            version=5,
            title=entry.data[CONF_USERNAME],
            data={
                CONF_USERNAME: entry.data[CONF_USERNAME],
                CONF_PASSWORD: entry.data[CONF_PASSWORD],
                MAINTENANCE_COOLDOWN: None
            },
            options={
                SKIP_PASSWORD_CHANGE: entry.options[SKIP_PASSWORD_CHANGE],
                POLLING_INTERVAL: 120
            },
        )

    if entry.version == 4:
        LOGGER.debug(
            'Migrating Coway config: adding maintenance_cooldown key'
        )

        hass.config_entries.async_update_entry(
            entry,
            version=5,
            title=entry.data[CONF_USERNAME],
            data={
                CONF_USERNAME: entry.data[CONF_USERNAME],
                CONF_PASSWORD: entry.data[CONF_PASSWORD],
                MAINTENANCE_COOLDOWN: None
            },
            options={
                SKIP_PASSWORD_CHANGE: entry.options[SKIP_PASSWORD_CHANGE],
                POLLING_INTERVAL: entry.options[POLLING_INTERVAL]
            },
        )
        
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """ Update options. """
    
    await hass.config_entries.async_reload(entry.entry_id)
