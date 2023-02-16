# Waterkotte Heatpump

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

All credit's should go to the original creator [@pattisonmichael](https://github.com/pattisonmichael):
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

# Waterkotte Heatpump Integration for Home Assistant
**This component will set up the following platforms.**

| Platform        | Description                             |
| --------------- | --------------------------------------- |
| `binary_sensor` | Show something `True` or `False`.       |
| `sensor`        | Show info from Waterkotte Heatpump API. |
| `switch`        | Switch something `True` or `False`.     |
| `select`        | Select a value from options.            |

![logo][logoimg]

## Installation
## Installation
### HACS [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
1. Add a custom integration repository to HACS: [waterkotte-integration](https://github.com/marq24/waterkotte-integration)
1. Install the custom integration
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Waterkotte Heatpump"
1. Setup the waterkotte custom integration as described below
  <!--1. In HACS Store, search for [***pattisonmichael/waterkotte-integration***]-->
### Manual
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `waterkotte_heatpump`.
4. Download _all_ the files from the `custom_components/waterkotte_heatpump/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Waterkotte Heatpump"

## Configuration is done in the UI

Use the Config flow to add the integration. You will need the IP/Hostname and Username/Password to log in.
<!---->

Not all available sensors are enabled by default.

To set the the times for the holiday mode use the provided service `waterkotte_heatpump.set_holiday` and set `start` and `end` parameter.

## Troubleshooting


### Sessions

The Heatpump only allows 2 sessions and there is not way to close a session. Sometimes you will get an error about the login. Just wait a few minutes and it should auto correct itself. Session usually time out within about 5 min.

### Stale Data

The Heatpump will not always respond with data. This happens usually after the system changes status, e.g. start/stop the heating. There is not much we can do about this unfortunately. I try to cache the data in possible for a better UX.

## Credits
This project is a fork from [@pattisonmichael](https://github.com/pattisonmichael)'s [Waterkotte-Integration](https://github.com/pattisonmichael/waterkotte-integration)

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[buymecoffee]: https://www.buymeacoffee.com/pattisonmichael
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/marq24/waterkotte-integration.svg?style=for-the-badge
[commits]: https://github.com/marq24/waterkotte-integration/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[logoimg]: logo.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/40marq24/waterkotte-integration.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40marq24-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/marq24/waterkotte-integration.svg?style=for-the-badge
[releases]: https://github.com/marq24/waterkotte-integration/releases
[user_profile]: https://github.com/marq24
