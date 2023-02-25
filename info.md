[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

All credit's have to go to the original creator [@pattisonmichael](https://github.com/pattisonmichael):

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

**This component will set up the following platforms.**

| Platform        | Description                                          |
| --------------- |------------------------------------------------------|
| `binary_sensor` | Show something `True` or `False`.                    |
| `sensor`        | Show info from Waterkotte Heatpump API.              |
| `switch`        | Switch something `True` or `False`.                  |
| `select`        | Select a value from options.                         |
| `number`        | adjustable Temperatures (demanded or heating curves) |

{% if not installed %}

## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Waterkotte Heatpump [+2020]".

{% endif %}

## Configuration is done in the UI

Use the Config flow to add the integration. You will need the IP/Hostname and Username/Password to log in.
<!---->

Most of the available sensors are __not__ enabled by default.

### Setting dates & times
- To set the times for the holiday mode use the provided service `waterkotte_heatpump.set_holiday` and set `start` and `end` parameter.
- To set the water disinfection start time (HH:MM) use the provided service `waterkotte_heatpump.set_time` and set `time` parameter (seconds will be ignored).

## Credits
This project is a fork from [@pattisonmichael](https://github.com/pattisonmichael)'s [Waterkotte-Integration](https://github.com/pattisonmichael/waterkotte-integration)

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[buymecoffee]: https://www.buymeacoffee.com/pattisonmichael
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/marq24/ha-waterkotte.svg?style=for-the-badge
[commits]: https://github.com/marq24/ha-waterkotte/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[logoimg]: logo.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com/marq24/ha-waterkotte/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/marq24/ha-waterkotte.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40marq24-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/marq24/ha-waterkotte.svg?style=for-the-badge
[releases]: https://github.com/marq24/ha-waterkotte/releases
[user_profile]: https://github.com/marq24
