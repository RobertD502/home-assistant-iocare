"""DataUpdateCoordinator for the Coway integration."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json

from cowayaio import CowayClient
from cowayaio.exceptions import (
    AuthError,
    CowayError,
    NoPlaces,
    NoPurifiers,
    PasswordExpired,
    ServerMaintenance,
    RateLimited
)
from cowayaio.purifier_model import PurifierData

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import as_local

from .const import (
    DOMAIN,
    LOGGER,
    MAINTENANCE_COOLDOWN,
    POLLING_INTERVAL,
    SKIP_PASSWORD_CHANGE,
    TIMEOUT
)
from .util import KnownServerMaintenance



class CowayDataUpdateCoordinator(DataUpdateCoordinator):
    """Coway Data Update Coordinator."""

    data: PurifierData

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Coway coordinator."""

        self.client = CowayClient(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            session=async_create_clientsession(hass),
            timeout=TIMEOUT,
        )
        self.entry = entry
        self.cooldown = entry.data[MAINTENANCE_COOLDOWN]
        self.client.skip_password_change = True
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options[POLLING_INTERVAL]),
        )

    async def _async_update_data(self) -> PurifierData:
        """Fetch data from Coway."""

        null_maint_data = {
            **self.entry.data,
            MAINTENANCE_COOLDOWN: None
        }
        nl = '\n'

        try:
            if self.client.server_maintenance:
                start_time = self.client.server_maintenance['start_date_time']
                end_time = self.client.server_maintenance['end_date_time']
                if start_time and end_time:
                    current_dt = datetime.now(timezone.utc)
                    if start_time.astimezone(timezone.utc) <= current_dt <= end_time.astimezone(timezone.utc):
                        raise KnownServerMaintenance(
                            f'Coway servers are currently undergoing planned maintenance. '
                            f'Polling will resume once the maintenance period is over.{nl}'
                            f'Maintenance Start Time: {as_local(start_time).strftime("%m/%d/%Y, %H:%M")}{nl}'
                            f'Maintenance End Time: {as_local(end_time).strftime("%m/%d/%Y, %H:%M")}{nl}'
                            f'Maintenance Info: {self.client.server_maintenance["description"]}'
                        )
                    else:
                        # Edge-case if maintenance goes beyond planned period
                        if self.cooldown:
                            if datetime.now(timezone.utc).timestamp() <= self.cooldown:
                                raise ServerMaintenance(
                                    f'Coway servers are currently undergoing planned maintenance. '
                                    f'Polling suspended. Will try polling again/checking if maintenance '
                                    f'has ended at {datetime.utcfromtimestamp(self.cooldown).strftime("%m/%d/%Y, %H:%M")}'
                                )
                            else:
                                self.hass.config_entries.async_update_entry(self.entry, data=null_maint_data)
                                self.cooldown = None
                                data = await self.client.async_get_purifiers_data()
                        else:
                            data = await self.client.async_get_purifiers_data()
                else:
                    data = await self.client.async_get_purifiers_data()
                    if self.cooldown:
                        self.hass.config_entries.async_update_entry(self.entry, data=null_maint_data)
                        self.cooldown = None
            # Logic if maintenance period is unknown during startup
            else:
                if self.cooldown:
                    if datetime.now(timezone.utc).timestamp() <= self.cooldown:
                        raise ServerMaintenance(
                            f'Coway servers are currently undergoing planned maintenance. '
                            f'Polling suspended. Will try polling again/checking if maintenance '
                            f'has ended at {datetime.utcfromtimestamp(self.cooldown).strftime("%m/%d/%Y, %H:%M")}'
                        )
                    else:
                        # Reset cooldown as an hour has passed.
                        # If server maintenance is experienced again,
                        # the cooldown key will get populated again
                        # during exception handling.
                        self.hass.config_entries.async_update_entry(self.entry, data=null_maint_data)
                        self.cooldown = None
                        data = await self.client.async_get_purifiers_data()
                else:
                    data = await self.client.async_get_purifiers_data()

        except RateLimited:
            raise ConfigEntryError(
                f"Failed to set up Coway integration for {self.client.username}: Your account is "
                f"likely rate-limited (blocked). Please wait 24 hours before attempting to use the integration again. "
                f"If, after 24 hours, you're unable to log in even with the mobile IoCare+ app, please contact "
                f"Coway for support."
            )
        except NoPlaces:
            raise ConfigEntryError(
                f'Failed to set up Coway integration for {self.client.username}: No Coway places '
                f'have been found to be associated with your IoCare+ account.'
            )
        except NoPurifiers:
            raise ConfigEntryError(
                f'No purifiers found to be associated with IoCare+ account. This integration requires/only '
                f'works with purifiers that are registered in the IoCare+ app (NOT the old IoCare app).'
            )
        except KnownServerMaintenance as error:
            raise UpdateFailed(error) from error
        except ServerMaintenance as error:
            if self.cooldown:
                raise UpdateFailed(error) from error
            else:
                # Update cooldown in order to not try polling again for another hour.
                # Stores new cooldown value when Coordinator object isn't destroyed
                # such as when the initial data fetch has already happened.
                self.cooldown = (datetime.now(timezone.utc) + timedelta(seconds=3600)).timestamp()
                delay_maint_data = {
                    **self.entry.data,
                    MAINTENANCE_COOLDOWN: self.cooldown
                }
                self.hass.config_entries.async_update_entry(self.entry, data=delay_maint_data)
                raise UpdateFailed(error) from error
        except AuthError as error:
            raise ConfigEntryAuthFailed from error
        except PasswordExpired as error:
            raise ConfigEntryAuthFailed(
                f"Coway servers are requesting a password change as the password on this account hasn't been changed for 60 days or more. "
                f"Either use the IoCare app to change your password or reauthenticate the integration with the skip password change option."
            )
        except CowayError as error:
            raise UpdateFailed(error) from error

        LOGGER.debug(f'Found the following Coway devices: {nl}{json.dumps(data, default=vars, indent=4)}')
        if not data.purifiers:
            raise UpdateFailed("No Purifiers found")

        return data
