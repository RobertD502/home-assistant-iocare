"""Constants for Coway."""

import asyncio
import logging

from aiohttp.client_exceptions import ClientConnectionError
from cowayaio.constants import LightMode
from cowayaio.exceptions import AuthError, CowayError

from homeassistant.const import Platform
from homeassistant.util.percentage import ordered_list_item_to_percentage


LOGGER = logging.getLogger(__package__)

TIMEOUT = 20
DEFAULT_NAME = "Coway IoCare"
DOMAIN = "coway"

COWAY_COORDINATOR = "coway_coordinator"
POLLING_INTERVAL = "polling_interval"
SKIP_PASSWORD_CHANGE = "skip_password_change"
UPDATE_LISTENER = "update_listener"
MAINTENANCE_COOLDOWN = "maintenance_cooldown"

PLATFORMS = [
    Platform.FAN,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

COWAY_ERRORS = (
    asyncio.TimeoutError,
    ClientConnectionError,
    AuthError,
    CowayError,
)

IAQ_NAMED = {
    1: "Good",
    2: "Moderate",
    3: "Unhealthy",
    4: "Very Unhealthy"
}

IOCARE_FAN_OFF = 0
IOCARE_FAN_LOW = 1
IOCARE_FAN_MEDIUM = 2
IOCARE_FAN_HIGH = 3

IOCARE_TIMER_OFF = "0"
IOCARE_TIMER_1H = "60"
IOCARE_TIMER_2H = "120"
IOCARE_TIMER_4H = "240"
IOCARE_TIMER_8H = "480"

IOCARE_TIMERS = ["OFF", "1 Hour", "2 Hours", "4 Hours", "8 Hours"]
IOCARE_TIMERS_TO_HASS = {
    IOCARE_TIMER_OFF: "OFF",
    IOCARE_TIMER_1H: "1 Hour",
    IOCARE_TIMER_2H: "2 Hours",
    IOCARE_TIMER_4H: "4 Hours",
    IOCARE_TIMER_8H: "8 Hours"
}

IOCARE_PRE_FILTER_WASH_FREQUENCIES = ["2 Weeks", "3 Weeks", "4 Weeks"]
IOCARE_PRE_FILTER_TO_HASS = {
    2: "2 Weeks",
    3: "3 Weeks",
    4: "4 Weeks"
}

IOCARE_SMART_SENSITIVITIES = ["Sensitive", "Normal", "Insensitive"]
IOCARE_SMART_SENSITIVITY_TO_HASS = {
    1: "Sensitive",
    2: "Normal",
    3: "Insensitive"
}

PRESET_MODE_AUTO = "Auto"
PRESET_MODE_AUTO_ECO = "Auto (Eco)"
PRESET_MODE_NIGHT = "Night"
PRESET_MODE_ECO = "Eco"
PRESET_MODE_RAPID = "Rapid"

ORDERED_NAMED_FAN_SPEEDS = [IOCARE_FAN_LOW, IOCARE_FAN_MEDIUM, IOCARE_FAN_HIGH]
PRESET_MODES = [PRESET_MODE_AUTO, PRESET_MODE_NIGHT]
PRESET_MODES_WITH_ECO = [PRESET_MODE_AUTO, PRESET_MODE_AUTO_ECO, PRESET_MODE_NIGHT]
# Model AP-1512HHS uses Eco mode instead of Night mode
PRESET_MODES_AP = [PRESET_MODE_AUTO, PRESET_MODE_ECO]
PRESET_MODES_250 = [PRESET_MODE_AUTO, PRESET_MODE_NIGHT, PRESET_MODE_RAPID]
PRESET_MODES_250_WITH_ECO = [PRESET_MODE_AUTO, PRESET_MODE_AUTO_ECO, PRESET_MODE_NIGHT, PRESET_MODE_RAPID]

IOCARE_FAN_SPEED_TO_HASS = {
    IOCARE_FAN_OFF: 0,
    IOCARE_FAN_LOW: ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, IOCARE_FAN_LOW),
    IOCARE_FAN_MEDIUM: ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, IOCARE_FAN_MEDIUM),
    IOCARE_FAN_HIGH: ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, IOCARE_FAN_HIGH)
}

IOCARE_LIGHT_MODES = ["On", "Off", "AQI Off"]
IOCARE_LIGHT_MODES_EXTENDED = ["On", "Off", "AQI Off", "Half Off"]
IOCARE_LIGHT_MODES_TO_HASS = {
    LightMode.ON: "On",
    LightMode.AQI_OFF: "AQI Off",
    LightMode.OFF: "Off",
    LightMode.HALF_OFF: "Half Off"
}
