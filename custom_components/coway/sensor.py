""" Coway Airmega Purifier Air Quality Sensors"""

import logging
from homeassistant.helpers import entity_platform
from homeassistant.components.sensor import SensorEntity, STATE_CLASS_MEASUREMENT, SensorDeviceClass
from .const import DOMAIN
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
)
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Platform uses config entry setup."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Coway Air Quality sensors."""
    _LOGGER.info("Setting up config entry for the Coway Airmega sensor platform")

    iocare = hass.data[DOMAIN]

    aqi = []
    pm_25 = []
    pm_10 = []
    carbon_dioxide = []
    voc = []

    for air_measurements in iocare.devices():
        aqi.append(AirQualityIndex(air_measurements))
        pm_25.append(ParticulateMatter25(air_measurements))
        pm_10.append(ParticulateMatter10(air_measurements))
        carbon_dioxide.append(CarbonDioxide(air_measurements))
        voc.append(VolatileOrganicCompounds(air_measurements))

    async_add_entities(aqi)
    async_add_entities(pm_25)
    async_add_entities(pm_10)
    async_add_entities(carbon_dioxide)
    async_add_entities(voc)

class AirQualityIndex(SensorEntity):
    """Representation of a Coway Airmega Air Quality Index."""

    def __init__(self, device):
        self._device = device
        self._available = True

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device.name,
            "manufacturer": "Coway",
            "model": self._device.product_name_full,
        }

    @property
    def unique_id(self):
        """Return the ID of this purifier."""
        return self._device.device_id + '_aqi'

    @property
    def name(self):
        """Return the name of the purifier if any."""
        return self._device.name + '_aqi'

    @property
    def state(self) -> float:
        """Return AQI Measurement"""
        return round(float(self._device.quality["air_quality_index"]), 1)

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def unit_of_measurement(self):
        return "aqi"

    @property
    def icon(self):
        return 'mdi:air-filter'

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing aqi sensor state")
        self._device.refresh()

class ParticulateMatter25(SensorEntity):
    """Representation of a Coway Airmega Particulate Matter 2.5"""

    def __init__(self, device):
        self._device = device
        self._available = True

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device.name,
            "manufacturer": "Coway",
            "model": self._device.product_name_full,
        }

    @property
    def unique_id(self):
        """Return the ID of this purifier."""
        return self._device.device_id + '_particulate_matter_2_5'

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._device.name + '_particulate_matter_2_5'

    @property
    def state(self):
        """Return the particulate matter 2.5 level."""
        return self._device.quality["particulate_matter_2_5"]

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def unit_of_measurement(self):
        return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    @property
    def icon(self):
        return 'mdi:air-filter'

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing particulate matter 2.5 sensor state")
        self._device.refresh()

class ParticulateMatter10(SensorEntity):
    """Representation of a Coway Airmega Particulate Matter 1.0"""

    def __init__(self, device):
        self._device = device
        self._available = True

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device.name,
            "manufacturer": "Coway",
            "model": self._device.product_name_full,
        }

    @property
    def unique_id(self):
        """Return the ID of this purifier."""
        return self._device.device_id + '_particulate_matter_1_0'

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._device.name + '_particulate_matter_1_0'

    @property
    def state(self):
        """Return the particulate matter 1.0 level."""
        return self._device.quality["particulate_matter_10"]

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def unit_of_measurement(self):
        return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    @property
    def icon(self):
        return 'mdi:air-filter'

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing particulate matter 1.0 sensor state")
        self._device.refresh()

class CarbonDioxide(SensorEntity):
    """Representation of a Coway Airmega Carbon Dioxide Sensor"""

    def __init__(self, device):
        self._device = device
        self._available = True

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device.name,
            "manufacturer": "Coway",
            "model": self._device.product_name_full,
        }

    @property
    def unique_id(self):
        """Return the ID of this purifier."""
        return self._device.device_id + '_carbon_dioxide'

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._device.name + '_carbon_dioxide'

    @property
    def state(self):
        """Return the CO2 (carbon dioxide) level."""
        return self._device.quality["carbon_dioxide"]

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def unit_of_measurement(self):
        return CONCENTRATION_PARTS_PER_MILLION

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.CO2

    @property
    def icon(self):
        return 'mdi:molecule-co2'

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing Airmega Carbon Dioxide sensor state")
        self._device.refresh()

class VolatileOrganicCompounds(SensorEntity):
    """Representation of a Coway Airmega VOC Sensor"""

    def __init__(self, device):
        self._device = device
        self._available = True

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device.name,
            "manufacturer": "Coway",
            "model": self._device.product_name_full,
        }

    @property
    def unique_id(self):
        """Return the ID of this purifier."""
        return self._device.device_id + '_voc'

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._device.name + '_voc'

    @property
    def state(self):
        """Return the VOC (Volatile Organic Compounds) level."""
        return self._device.quality["volatile_organic_compounds"]

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def icon(self):
        return 'mdi:air-filter'

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing Airmega VOC sensor state")
        self._device.refresh()
