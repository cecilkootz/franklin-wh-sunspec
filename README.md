# FranklinWH SunSpec Integration for Home Assistant

A Home Assistant custom integration for FranklinWH energy systems (aGate X) using the SunSpec Modbus protocol.

## Features

- Real-time monitoring of solar production, battery status, and grid power
- Automatic polling with configurable update interval
- Energy dashboard compatible sensors
- Local polling (no cloud dependency)

## Sensors

This integration provides 12 sensors organized into four categories.

### Solar Sensors

| Sensor | Unit | Description |
|--------|------|-------------|
| **Solar Power** | W | Current real-time power output from your solar panels. This value is always positive and represents how much electricity your solar system is generating right now. |
| **Solar Energy Total** | Wh | Lifetime cumulative energy produced by your solar system since installation. This is a monotonically increasing value useful for tracking total production and calculating daily/monthly statistics with utility meters. |

### Battery Sensors

| Sensor | Unit | Description |
|--------|------|-------------|
| **Battery State of Charge** | % | Current charge level of your battery system (0-100%). Indicates how much stored energy is available for use. |
| **Battery Power** | W | Current power flow to/from the battery. **Positive values** indicate the battery is discharging (providing power to your home). **Negative values** indicate the battery is charging (storing excess energy). |
| **Battery Health** | % | State of health (SoH) of your battery system. Represents the battery's current maximum capacity compared to its original capacity. A value of 100% means the battery is performing at its rated capacity. |

### Grid Sensors

| Sensor | Unit | Description |
|--------|------|-------------|
| **Grid Power** | W | Current power flow between your home and the utility grid. **Positive values** indicate you are exporting power to the grid (selling). **Negative values** indicate you are importing power from the grid (buying). |
| **Grid Export Total** | Wh | Lifetime cumulative energy exported (sold) to the utility grid. Monotonically increasing value for tracking total exports. |
| **Grid Import Total** | Wh | Lifetime cumulative energy imported (purchased) from the utility grid. Monotonically increasing value for tracking total imports. |
| **Grid Voltage** | V | Current AC line-to-line voltage from the grid. Typical values are around 240V for US split-phase systems. |
| **Grid Frequency** | Hz | Current AC grid frequency. Typical values are 60 Hz (North America) or 50 Hz (Europe/Asia). Small variations indicate grid load conditions. |

### Calculated Sensors

| Sensor | Unit | Description |
|--------|------|-------------|
| **Home Load** | W | Calculated total power consumption of your home. This is derived from: `Solar Power + Battery Power - Grid Power`. Represents how much electricity your home is currently using. |
| **Excess Power** | W | Calculated surplus solar power available after meeting home demand. When positive, this represents power that could be stored in the battery or exported to the grid. |

### Sign Conventions

Understanding the sign conventions is important for interpreting power flow:

| Measurement | Positive (+) | Negative (-) |
|-------------|--------------|--------------|
| Grid Power | Exporting to grid | Importing from grid |
| Battery Power | Discharging (powering home) | Charging (storing energy) |
| Solar Power | Always positive | N/A |

### Entity IDs

All sensors are created under the device "FranklinWH aGate X" with entity IDs following this pattern:

```
sensor.franklinwh_agate_x_<sensor_name>
```

Examples:
- `sensor.franklinwh_agate_x_solar_power`
- `sensor.franklinwh_agate_x_battery_state_of_charge`
- `sensor.franklinwh_agate_x_grid_power`
- `sensor.franklinwh_agate_x_home_load`

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu in the top right
3. Select "Custom repositories"
4. Add this repository URL and select "Integration" as the category
5. Click "Add"
6. Search for "FranklinWH SunSpec" and install
7. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/franklin_wh_sunspec` folder
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "FranklinWH SunSpec"
4. Enter the connection details:
   - **Host**: IP address of your FranklinWH aGate X
   - **Port**: Modbus TCP port (default: 502)
   - **Slave ID**: Modbus slave ID (default: 1)

### Options

After setup, you can configure:
- **Update interval**: How often to poll the device (5-60 seconds, default: 10)

## Energy Dashboard Setup

Add these sensors to your Home Assistant Energy Dashboard:

- **Solar Production**: `sensor.franklinwh_agate_x_solar_energy_total`
- **Grid Consumption**: `sensor.franklinwh_agate_x_grid_import_total`
- **Return to Grid**: `sensor.franklinwh_agate_x_grid_export_total`

### Utility Meters (Optional)

Add to your `configuration.yaml` for daily/monthly tracking:

```yaml
utility_meter:
  solar_daily:
    source: sensor.franklinwh_agate_x_solar_energy_total
    cycle: daily
  solar_monthly:
    source: sensor.franklinwh_agate_x_solar_energy_total
    cycle: monthly
  grid_import_daily:
    source: sensor.franklinwh_agate_x_grid_import_total
    cycle: daily
  grid_import_monthly:
    source: sensor.franklinwh_agate_x_grid_import_total
    cycle: monthly
  grid_export_daily:
    source: sensor.franklinwh_agate_x_grid_export_total
    cycle: daily
  grid_export_monthly:
    source: sensor.franklinwh_agate_x_grid_export_total
    cycle: monthly
```

## Requirements

- FranklinWH aGate X with SunSpec Modbus enabled
- Network access to the device on port 502

## Troubleshooting

### Cannot connect to device
- Verify the IP address is correct
- Ensure Modbus TCP is enabled on your FranklinWH system
- Check that port 502 is not blocked by a firewall
- Verify the slave ID (usually 1)

### Sensors showing unavailable
- Check your network connection to the device
- Try increasing the update interval in options
- Check Home Assistant logs for specific error messages

## License

MIT License
