"""Data update coordinator for FranklinWH SunSpec integration."""

from datetime import timedelta
import logging
from typing import Any

import sunspec2.modbus.client as sunspec_client

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class FranklinWHCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data fetching from FranklinWH device."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        slave_id: int,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.host = host
        self.port = port
        self.slave_id = slave_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    def _fetch_data(self) -> dict[str, Any]:
        """Fetch data synchronously (runs in executor)."""
        device = sunspec_client.SunSpecModbusClientDeviceTCP(
            slave_id=self.slave_id,
            ipaddr=self.host,
            ipport=self.port,
        )

        try:
            device.scan()

            # Model 502: Solar Module
            m502 = device.models[502][0]
            m502.read()
            w_sf_502 = m502.points["W_SF"].value or 0
            wh_sf_502 = m502.points["Wh_SF"].value or 0
            solar_power = (m502.points["OutPw"].value or 0) * (10 ** w_sf_502)
            solar_total = (m502.points["OutWh"].value or 0) * (10 ** wh_sf_502)

            # Model 701: DER AC Measurement
            m701 = device.models[701][0]
            m701.read()
            w_sf = m701.points["W_SF"].value or 0
            v_sf = m701.points["V_SF"].value or 0
            hz_sf = m701.points["Hz_SF"].value or 0
            totwh_sf = m701.points["TotWh_SF"].value or 0

            grid_power = (m701.points["W"].value or 0) * (10 ** w_sf)
            voltage = (m701.points["LLV"].value or 0) * (10 ** v_sf)
            frequency = (m701.points["Hz"].value or 0) * (10 ** hz_sf)
            grid_export_total = (m701.points["TotWhInj"].value or 0) * (10 ** totwh_sf)
            grid_import_total = (m701.points["TotWhAbs"].value or 0) * (10 ** totwh_sf)

            # Model 713: DER Storage Capacity
            m713 = device.models[713][0]
            m713.read()
            wh_sf_713 = m713.points["WH_SF"].value or 0
            pct_sf = m713.points["Pct_SF"].value or 0

            battery_soc = (m713.points["SoC"].value or 0) * (10 ** pct_sf)
            battery_capacity = (m713.points["WHRtg"].value or 0) * (10 ** wh_sf_713)
            battery_health = (m713.points["SoH"].value or 0) * (10 ** pct_sf)

            # Model 714: DER DC Measurement
            m714 = device.models[714][0]
            m714.read()
            dcw_sf = m714.points["DCW_SF"].value or 0
            battery_power = (m714.points["DCW"].value or 0) * (10 ** dcw_sf)

            # Split battery power into charge/discharge (both positive values)
            # battery_power: positive = discharging, negative = charging
            battery_charge = max(0, -battery_power)
            battery_discharge = max(0, battery_power)

            # Split grid power into import/export (both positive values)
            # grid_power: positive = exporting, negative = importing
            grid_import = max(0, -grid_power)
            grid_export = max(0, grid_power)

            # Calculate derived values
            # home_load = solar_power + battery_dc_power - grid_power
            # Where positive grid_power = export, negative = import
            # And positive battery_power = discharge, negative = charge
            home_load = solar_power + battery_power - grid_power
            excess_power = max(0, solar_power - home_load)

            return {
                "solar_power": solar_power,
                "solar_total": solar_total,
                "battery_soc": battery_soc,
                "battery_charge": battery_charge,
                "battery_discharge": battery_discharge,
                "battery_health": battery_health,
                "battery_capacity": battery_capacity,
                "grid_import": grid_import,
                "grid_export": grid_export,
                "grid_export_total": grid_export_total,
                "grid_import_total": grid_import_total,
                "home_load": home_load,
                "excess_power": excess_power,
                "voltage": voltage,
                "frequency": frequency,
            }

        finally:
            device.close()


async def validate_connection(
    hass: HomeAssistant, host: str, port: int, slave_id: int
) -> bool:
    """Validate that we can connect to the device."""

    def _test_connection() -> bool:
        device = sunspec_client.SunSpecModbusClientDeviceTCP(
            slave_id=slave_id,
            ipaddr=host,
            ipport=port,
        )
        try:
            device.scan()
            # Check that required models exist
            required_models = [502, 701, 713, 714]
            for model_id in required_models:
                if model_id not in device.models:
                    raise ValueError(f"Required SunSpec model {model_id} not found")
            return True
        finally:
            device.close()

    return await hass.async_add_executor_job(_test_connection)
