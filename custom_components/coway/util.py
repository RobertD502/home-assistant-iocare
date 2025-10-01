"""Utilities for Coway Integration"""
from __future__ import annotations

import async_timeout

from aiohttp import ClientSession
from cowayaio import CowayClient
from cowayaio.exceptions import AuthError, CowayError, PasswordExpired, ServerMaintenance, RateLimited

from homeassistant.core import HomeAssistant

from .const import LOGGER, COWAY_ERRORS, TIMEOUT


async def async_validate_api(hass: HomeAssistant, username: str, password: str, skip_password_change: bool, session: ClientSession) -> None:
    """Get data from API."""

    client = CowayClient(
        username,
        password,
        session=session,
        timeout=TIMEOUT,
    )
    client.skip_password_change = skip_password_change

    try:
        async with async_timeout.timeout(TIMEOUT):
            await client.login()
            coway_query = await client.async_get_purifiers()
    except ServerMaintenance as err:
        raise ServerMaintenance from err
    except RateLimited as err:
        raise RateLimited from err
    except AuthError as err:
        LOGGER.error(f'Could not authenticate on Coway servers: {err}')
        raise AuthError from err
    except PasswordExpired as err:
        LOGGER.error(
            f"Coway servers are requesting a password change as the password on "
            f"this account hasn't been changed for 60 days or more. Use the IoCare "
            f"app to change your password or use the skip password change option."
        )
        raise PasswordExpired from err
    except COWAY_ERRORS as err:
        LOGGER.error(f'Failed to get information from Coway servers: {err}')
        raise ConnectionError from err
    purifiers: list = coway_query
    if not purifiers:
        LOGGER.error("Could not retrieve any purifiers from Coway servers")
        raise NoPurifiersError


class NoPurifiersError(Exception):
    """No Purifiers from Coway API."""

class KnownServerMaintenance(Exception):
    """Known server maintenance encountered."""
