"""Sensor platform for FranklinWH SunSpec integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import FranklinWHCoordinator


@dataclass(frozen=True, kw_only=True)
class FranklinWHSensorEntityDescription(SensorEntityDescription):
    """Describe a FranklinWH sensor entity."""

    value_fn: callable[[dict[str, Any]], float | None] = None
    round_digits: int | None = 0
    conversion_factor: float = 1.0  # Multiply raw value by this factor


SENSOR_DESCRIPTIONS: tuple[FranklinWHSensorEntityDescription, ...] = (
    FranklinWHSensorEntityDescription(
        key="solar_power",
        translation_key="solar_power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        round_digits=2,
        conversion_factor=0.001,  # W to kW
    ),
    FranklinWHSensorEntityDescription(
        key="solar_total",
        translation_key="solar_total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        round_digits=0,
    ),
    FranklinWHSensorEntityDescription(
        key="battery_soc",
        translation_key="battery_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
        round_digits=1,
    ),
    FranklinWHSensorEntityDescription(
        key="battery_charge",
        translation_key="battery_charge",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging",
        round_digits=2,
        conversion_factor=0.001,  # W to kW
    ),
    FranklinWHSensorEntityDescription(
        key="battery_discharge",
        translation_key="battery_discharge",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-arrow-down",
        round_digits=2,
        conversion_factor=0.001,  # W to kW
    ),
    FranklinWHSensorEntityDescription(
        key="battery_health",
        translation_key="battery_health",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-heart",
        round_digits=1,
    ),
    FranklinWHSensorEntityDescription(
        key="grid_import",
        translation_key="grid_import",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-import",
        round_digits=2,
        conversion_factor=0.001,  # W to kW
    ),
    FranklinWHSensorEntityDescription(
        key="grid_export",
        translation_key="grid_export",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        round_digits=2,
        conversion_factor=0.001,  # W to kW
    ),
    FranklinWHSensorEntityDescription(
        key="grid_export_total",
        translation_key="grid_export_total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-export",
        round_digits=0,
    ),
    FranklinWHSensorEntityDescription(
        key="grid_import_total",
        translation_key="grid_import_total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-import",
        round_digits=0,
    ),
    FranklinWHSensorEntityDescription(
        key="home_load",
        translation_key="home_load",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
        round_digits=2,
        conversion_factor=0.001,  # W to kW
    ),
    FranklinWHSensorEntityDescription(
        key="excess_power",
        translation_key="excess_power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
        round_digits=2,
        conversion_factor=0.001,  # W to kW
    ),
    FranklinWHSensorEntityDescription(
        key="voltage",
        translation_key="voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        round_digits=1,
    ),
    FranklinWHSensorEntityDescription(
        key="frequency",
        translation_key="frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        round_digits=2,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FranklinWH sensors from a config entry."""
    coordinator: FranklinWHCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        FranklinWHSensor(coordinator, description, entry)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class FranklinWHSensor(CoordinatorEntity[FranklinWHCoordinator], SensorEntity):
    """Representation of a FranklinWH sensor."""

    entity_description: FranklinWHSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FranklinWHCoordinator,
        description: FranklinWHSensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="FranklinWH aGate X",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"http://{coordinator.host}",
        )

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None

        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None

        # Apply conversion factor (e.g., W to kW)
        value = value * self.entity_description.conversion_factor

        if self.entity_description.round_digits is not None:
            return round(value, self.entity_description.round_digits)
        return value
