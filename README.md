# Home Assistant Integration for Waterkotte Heatpumps [+2020]

![logo](https://github.com/marq24/ha-waterkotte/raw/main/logo.png)

This Home Assistant Integration is providing information from the German heatpump pioneer Waterkotte. In addition and where possible functions are provided to control the system.

All data will be fetched (or send) to your Waterkotte via the build in webserver of the unit. So the functionality is based on the data and settings that are available also via the frontend that you can directly access via a web-browser.

[![hacs_badge][hacsbadge]][hacs] [![BuyMeCoffee][buymecoffeebadge]][buymecoffee] [![PayPal][paypalbadge]][paypal]

## This component will set up the following platforms

| Platform        | Description                                          |
|-----------------|------------------------------------------------------|
| `binary_sensor` | Show something `True` or `False`.                    |
| `sensor`        | Show info from Waterkotte Heatpump API.              |
| `switch`        | Switch something `True` or `False`.                  |
| `select`        | Select a value from options.                         |
| `number`        | adjustable Temperatures (demanded or heating curves) |
| `service`       | Provides services to interact with heatpump          |

## Disclaimer

Please be aware, that we are developing this integration to best of our knowledge and belief, but cant give a guarantee. Therefore, use this integration **at your own risk**.

## What you get [2024.02.15]

[![sampleview](https://github.com/marq24/ha-waterkotte/raw/main/sample-view-s.png)](https://github.com/marq24/ha-waterkotte/raw/main/sample-view.png)

[[Get the sources for the sample dashboard_above](https://github.com/marq24/ha-waterkotte/blob/main/sample-view.yaml)] - Please note, that this sample dashboard makes use of the custom [multiple-entity-row](https://github.com/benct/lovelace-multiple-entity-row) frontend integration that need to be installed separately. 

## Installation

### HACS

1. Add a custom integration repository to HACS: [ha-waterkotte](https://github.com/marq24/ha-waterkotte)
1. Install the custom integration
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Waterkotte Heatpump [+2020]"
1. Setup the waterkotte custom integration as described below

  <!--1. In HACS Store, search for [***marq24/ha-waterkotte***]-->

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `waterkotte_heatpump`.
4. Download _all_ the files from the `custom_components/waterkotte_heatpump/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Waterkotte Heatpump [+2020]"

## Adding or enabling the integration

### My Home Assistant (2021.3+)

Just click the following Button to start the configuration automatically:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=waterkotte)

### Manual

Use the following steps for a manual configuration by adding the custom integration using the web interface and follow instruction on screen:

- Go to `Configuration -> Integrations` and add "Waterkotte" integration
- Provide the IP address (or hostname) of your Waterkotte Heatpump web server
- Select the Interface-Type of your Waterkotte (when you need to provide the user & password 'waterkotte' to login via your app/browser, then select `EcoTouch Mode`)
- Select the number of TAGs that can be fetched in a single call to your device (older devices might need to adjust this value - for my in 2022 installed Waterkotte 75 is totally fine)
- Provide area where the heatpump is located

After the integration was added you can use the 'config' button to adjust your settings and you can additionally modify the update intervall

Please note, that most of the available sensors are __not__ enabled by default.

## Services

The Integration provides currently 4 services:

### Setting dates & times

- SET_HOLIDAY

  To set the times for the holiday mode use the provided service `waterkotte_heatpump.set_holiday` and set `start` and `end` parameter.

- SET_DISINFECTION_START_TIME

  To set the water disinfection start time (HH:MM) use the provided service `waterkotte_heatpump.set_disinfection_start_time` and set `starthhmm` parameter (seconds will be ignored).

### Get Energy Balance

- GET_ENERGY_BALANCE

  Retrieves the overall energy consumption data for the year

- GET_ENERGY_BALANCE_MONTHLY

  Retrieves the monthly breakdown energy consumption data for a moving 12 month window. 1 = January, 2 = February, etc...

## Troubleshooting

### Sessions

The Heatpump only allows 2 sessions and there is no way to close a session. Sometimes you will get an error about the login. Just wait a few minutes and it should autocorrect itself. Session usually time out within about 5 min.

### Stale Data

The Heatpump will not always respond with data. This happens usually after the system changes status, e.g. start/stop the heating. There is not much we can do about this, unfortunately. I try to cache the data in possible for a better UX.

## Credits

This project is a fork from [@pattisonmichael](https://github.com/pattisonmichael)'
s [Waterkotte-Integration](https://github.com/pattisonmichael/waterkotte-integration)

The original project was generated from [@oncleben31](https://github.com/oncleben31)'
s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component)
template.

The original code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'
s [integration_blueprint](https://github.com/custom-components/integration_blueprint) template

---

###### Advertisement / Werbung - alternative way to support me

### Switch to Tibber!

Be smart switch to Tibber - that's what I did in october 2023. If you want to join Tibber (become a customer), you might want to use my personal invitation link. When you use this link, Tibber will we grant you and me a bonus of 50,-€ for each of us. This bonus then can be used in the Tibber store (not for your power bill) - e.g. to buy a Tibber Bridge. If you are already a Tibber customer and have not used an invitation link yet, you can also enter one afterward in the Tibber App (up to 14 days). [[see official Tibber support article](https://support.tibber.com/en/articles/4601431-tibber-referral-bonus#h_ae8df266c0)]

Please consider [using my personal Tibber invitation link to join Tibber today](https://invite.tibber.com/6o0kqvzf) or Enter the following code: 6o0kqvzf (six, oscar, zero, kilo, quebec, victor, zulu, foxtrot) afterward in the Tibber App - TIA!

---

[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=ccc

[buymecoffee]: https://www.buymeacoffee.com/marquardt24
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a-coffee-blue.svg?style=for-the-badge&logo=buymeacoffee&logoColor=ccc

[paypal]: https://paypal.me/marq24
[paypalbadge]: https://img.shields.io/badge/paypal-me-blue.svg?style=for-the-badge&logo=paypal&logoColor=ccc

[commits-shield]: https://img.shields.io/github/commit-activity/y/marq24/ha-waterkotte.svg?style=for-the-badge
[commits]: https://github.com/marq24/ha-waterkotte/commits/main
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[logoimg]: logo.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/marq24/ha-waterkotte.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40marq24-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/marq24/ha-waterkotte.svg?style=for-the-badge
[releases]: https://github.com/marq24/ha-waterkotte/releases
