"""Sensor platform for Coway integration."""

from __future__ import annotations

from datetime import time
from typing import Any

from cowayaio.purifier_model import CowayPurifier

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import(
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    LIGHT_LUX,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COWAY_COORDINATOR, DOMAIN, IAQ_NAMED, LOGGER
from .coordinator import CowayDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Coway Sensor Entities."""

    coordinator: CowayDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][COWAY_COORDINATOR]

    sensors = []

    for purifier_id, purifier_data in coordinator.data.purifiers.items():
            if purifier_data.air_quality_index is not None:
                sensors.append(AirQualityIndex(coordinator, purifier_id))

            sensors.extend((
                PreFilter(coordinator, purifier_id),
                MAX2Filter(coordinator, purifier_id),
                TimerRemaining(coordinator, purifier_id),
            ))

            # PM type and Air Quality sensor availability depends on the purfier model
            product_name = purifier_data.device_attr['product_name']
            if purifier_data.particulate_matter_2_5 is not None and product_name != "AIRMEGA":
                sensors.append(ParticulateMatter25(coordinator, purifier_id))
            if purifier_data.particulate_matter_10 is not None:
                sensors.append(ParticulateMatter10(coordinator, purifier_id))
            if purifier_data.aq_grade is not None:
                sensors.append(IndoorAQ(coordinator, purifier_id))
            if purifier_data.lux_sensor is not None:
                sensors.append(Lux(coordinator, purifier_id))


    async_add_entities(sensors)


class AirQualityIndex(CoordinatorEntity, SensorEntity):
    """Representation of AQI as reported by purifier."""

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

        return self.purifier_data.device_attr['device_id'] + '_aqi'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "AQI"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return current AQI measurement."""

        return round(float(self.purifier_data.air_quality_index), 1)

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.AQI

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class type."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Set icon for entity."""

        return 'mdi:air-filter'

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False


class PreFilter(CoordinatorEntity, SensorEntity):
    """Representation of pre-filter percentage remaining."""

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

        return self.purifier_data.device_attr['device_id'] + '_pre_filter'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        # AP-1512HHS models in UK (02FMG), Europe (02FMF, 02FWN)
        if self.purifier_data.device_attr['code'] in ['02FMG', '02FMF', '02FWN']:
            return "Charcoal filter"
        else:
            return "Pre filter"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current pre-filter percentage."""

        # AP-1512HHS models in UK (02FMG), Europe (02FMF, 02FWN)
        if self.purifier_data.device_attr['code'] in ['02FMG', '02FMF', '02FWN']:
            return self.purifier_data.odor_filter_pct
        else:
            return self.purifier_data.pre_filter_pct

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""

        return PERCENTAGE

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class type."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Set icon for entity."""

        return 'mdi:air-filter'

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False


class MAX2Filter(CoordinatorEntity, SensorEntity):
    """Representation of MAX2 filter percentage remaining."""

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

        return self.purifier_data.device_attr['device_id'] + '_max_filter'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        # AP-1512HHS models in UK (02FMG), Europe (02FMF, 02FWN)
        if self.purifier_data.device_attr['code'] in ['02FMG', '02FMF', '02FWN']:
            return "HEPA filter"
        else:
            return "MAX2 filter"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current MAX2/HEPA filter percentage."""

        return self.purifier_data.max2_pct

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""

        return PERCENTAGE

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class type."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Set icon for entity."""

        return 'mdi:air-filter'

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False


class ParticulateMatter10(CoordinatorEntity, SensorEntity):
    """Representation of PM10 measurement."""

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

        return self.purifier_data.device_attr['device_id'] + '_particulate_matter_1_0'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Particulate matter 10"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current PM10 measurement."""
        return int(self.purifier_data.particulate_matter_10)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""

        return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.PM10

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class type."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Set icon for entity."""

        return 'mdi:air-filter'

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False

class ParticulateMatter25(CoordinatorEntity, SensorEntity):
    """Representation of PM2.5 measurement."""

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

        return self.purifier_data.device_attr['device_id'] + '_particulate_matter_2_5'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Particulate matter 2.5"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current PM2.5 measurement."""
        return int(self.purifier_data.particulate_matter_2_5)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""

        return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.PM25

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class type."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Set icon for entity."""

        return 'mdi:air-filter'

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False


class TimerRemaining(CoordinatorEntity, SensorEntity):
    """Representation of time left on timer."""

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

        return self.purifier_data.device_attr['device_id'] + '_timer_remaining'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Timer remaining"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self):
        """Return time remaining on timer."""

        total_time = round((float(self.purifier_data.timer_remaining) / 60), 2)
        hours, minutes = int(total_time), round(((total_time - int(total_time)) * 60))
        timer_remaining = time(hour = hours, minute = minutes)
        return timer_remaining.isoformat(timespec = "minutes")

    @property
    def icon(self):
        """Set icon for entity."""

        return 'mdi:timer'

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False


class IndoorAQ(CoordinatorEntity, SensorEntity):
    """Representation of named indoor air quality."""

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

        return self.purifier_data.device_attr['device_id'] + '_indoor_aq'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Indoor air quality"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self):
        """Return named air quality."""

        aq_grade = self.purifier_data.aq_grade
        if aq_grade:
            named_quality = IAQ_NAMED.get(aq_grade, "Unknown air quality")
            return named_quality
        else:
            return None

    @property
    def icon(self):
        """Set icon for entity."""

        return 'mdi:air-filter'

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False


class Lux(CoordinatorEntity, SensorEntity):
    """Representation of Lux sensor for Airmega 400S."""

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

        return self.purifier_data.device_attr['device_id'] + '_lux'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Lux"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current Lux measurement."""

        if self.purifier_data.device_attr['model'] == 'Airmega 400S':
            return self.purifier_data.lux_sensor
        else:
            # For 250S, 1022 is the value obtained while testing
            # in a dark environment
            return max(1022 - self.purifier_data.lux_sensor, 0)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""

        return LIGHT_LUX

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.ILLUMINANCE

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class type."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Set icon for entity."""

        return 'mdi:brightness-5'

    @property
    def available(self) -> bool:
        """Return true if purifier is connected to Coway servers."""

        if self.purifier_data.network_status:
            return True
        else:
            return False
