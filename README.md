# Coway IoCare Home Assistant Integration


[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration) ![GitHub manifest version (path)](https://img.shields.io/github/manifest-json/v/RobertD502/home-assistant-iocare?filename=custom_components%2Fcoway%2Fmanifest.json)

<a href="https://www.buymeacoffee.com/RobertD502" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="100" width="424"></a>
<a href="https://liberapay.com/RobertD502/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg" height="100" width="300"></a>

### A lot of work has been put into creating the backend and this integration. If you enjoy this integration, consider donating by clicking on one of the supported methods above.

***All proceeds go towards helping a local animal rescue.**

## ⚠️ IMPORTANT NOTICE

**Use of this integration requires that purifiers have been registered with the IoCare+ app**


## Confirmed Working Models
- [250S](https://cowaymega.com/products/airmega-250s)
- [300S](https://cowaymega.com/products/airmega-300s)
- [400S](https://cowaymega.com/products/airmega-400s)
- [MightyS (AP-1512HHS)](https://cowaymega.com/products/airmega-ap-1512hhs-ap-1519p)
- [IconS](https://cowaymega.com/products/airmega-icons)

# Installation

#### With HACS
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=RobertD502&repository=home-assistant-iocare&category=integration)

> [!Tip]
> If you are unable to use the button above, manually search for Coway in HACS.

#### Manual
1. Copy the `coway` directory from `custom_components` in this repository and place inside your Home Assistant's `custom_components` directory.
2. Restart Home Assistant
3. Follow the instructions in the `Setup` section

> [!WARNING]
> If installing manually, in order to be alerted about new releases, you will need to subscribe to releases from this repository.

# Setup
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=coway)

> [!Tip]
> If you are unable to use the button above, follow the steps below:
> 1. Navigate to the Home Assistant Integrations page (Settings --> Devices & Services)
> 2. Click the `+ ADD INTEGRATION` button in the lower right-hand corner
> 3. Search for `Coway`

> [!Caution]
> Coway has implemented password checks which prompts users to change or ignore changing passwords that are 60 or more days old. If you want to skip changing your password, select the `Skip password change` option during setup. Otherwise, when the time comes, you will need to manually login using the IoCare app and change your password followed by reauthentication of the integration within Home Assistant. 

# Devices

Each purifier is exposed as a device in Home Assistant.

Depending on your purifier model, the following entities are possible:



| Entity | Entity Type | Additional Comments |
| --- | --- | --- |
| `Purifier` | `Fan` | Ability of controlling power, speed, and preset mode (Auto Mode, Night Mode, etc) |
| `Current timer` | `Select` | Ability to set timer to OFF, 1 hour, 2 hours, 4 hours, or 8 hours. `Setting a timer can only be done when a purifier is powered ON` |
| `Light` | `Switch` | All purifiers except 250S/IconS. Ability to turn light on and off. `Controlling the light can only be done when a purifier is powered ON` |
| `Light` | `Select` | Only for 250S/IconS purifiers. Ability to set the light to Off, On, AQI Off, and Half off (only IconS). `Controlling the light can only be done when a purifier is powered ON` |
| `Lux` | `Sensor` | Light lux measurement, if reported by your purifier. |
| `Button lock` | `Switch` | Only for 250S. Lock/unlock buttons on purifier control panel. `Controlling the button lock can only be done when a purifier is powered ON` |
| `AQI` | `Sensor` | Air Quality Index, if reported by your purifier. |
| `MAX2 Filter` | `Sensor` | Percentage of MAX2 filter life remaining. |
| `Pre Filter` | `Sensor` | Percentage of Pre filter remaining. |
| `Particulate Matter 10` | `Sensor` | Not available for IconS purifiers. |
| `Particulate Matter 2.5` | `Sensor` | Only available for IconS and 250S purifiers. |
| `Timer remaining` | `Sensor` | Shows the current amount of time left on a timer. This is a string in the form of hours:minutes. |
| `Indoor air quality` | `Sensor` | Shows the current indoor air quality based on Coway's scale. The state can be Good, Moderate, Unhealthy, or Very Unhealthy. |
| `Pre-filter wash frequency` | `Select` | Shows current pre-filter wash frequency setting and allows you to change it. Temporarily unavailable for 250S purifiers. |
| `Smart mode sensitivity` | `Select` | Shows current smart mode sensitivity setting and allows you to change it. |

