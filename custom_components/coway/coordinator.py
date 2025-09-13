"""DataUpdateCoordinator for the Coway integration."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json

from cowayaio import CowayClient
from cowayaio.exceptions import AuthError, CowayError, PasswordExpired
from cowayaio.purifier_model import PurifierData

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import as_local

from .const import DOMAIN, LOGGER, POLLING_INTERVAL, SKIP_PASSWORD_CHANGE, TIMEOUT


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
        self.client.skip_password_change = entry.options[SKIP_PASSWORD_CHANGE]
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options[POLLING_INTERVAL]),
        )

    async def _async_update_data(self) -> PurifierData:
        """Fetch data from Coway."""

        nl = '\n'
        try:
            if self.client.server_maintenance:
                start_time = self.client.server_maintenance['start_date_time']
                end_time = self.client.server_maintenance['end_date_time']
                if start_time and end_time:
                    current_dt = datetime.now(timezone.utc)
                    if start_time.astimezone(timezone.utc) <= current_dt <= end_time.astimezone(timezone.utc):
                        raise UpdateFailed(
                            f'Coway servers are currently undergoing planned maintenance. '
                            f'Polling will resume once the maintenance period is over.{nl}'
                            f'Maintenance Start Time: {as_local(start_time).strftime("%m/%d/%Y, %H:%M")}{nl}'
                            f'Maintenance End Time: {as_local(end_time).strftime("%m/%d/%Y, %H:%M")}{nl}'
                            f'Maintenance Info: {self.client.server_maintenance["description"]}'
                        )
                    else:
                        data = await self.client.async_get_purifiers_data()
                else:
                    data = await self.client.async_get_purifiers_data()
            data = await self.client.async_get_purifiers_data()
        except AuthError as error:
            raise ConfigEntryAuthFailed from error
        except PasswordExpired as error:
            raise ConfigEntryAuthFailed("Coway servers are requesting a password change as the password on this account hasn't been changed for 60 days or more. Either use the IoCare app to change your password or reauthenticate the integration with the skip password change option.")
        except CowayError as error:
            raise UpdateFailed(error) from error

        LOGGER.debug(f'Found the following Coway devices: {nl}{json.dumps(data, default=vars, indent=4)}')
        if not data.purifiers:
            raise UpdateFailed("No Purifiers found")

        return data
