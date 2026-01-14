# Home Assistant Integration for Waterkotte Heatpumps [+2020]

![logo](https://github.com/marq24/ha-waterkotte/raw/main/logo.png)

This Home Assistant Integration is providing information from the German heatpump pioneer Waterkotte. In addition and where possible functions are provided to control the system.

__Please note__, _that this integration is not official and not supported by the Waterkotte development team. I am not affiliated with Waterkotte in any way._

All data will be fetched (or send) to your Waterkotte via the build in webserver of the unit. So the functionality is based on the data and settings that are available also via the frontend that you can directly access via a web-browser.

[![hacs_badge][hacsbadge]][hacs] [![hainstall][hainstallbadge]][hainstall] [![Wero][werobadge]][wero] [![Revolut][revolutbadge]][revolut] [![PayPal][paypalbadge]][paypal] [![github][ghsbadge]][ghs] [![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

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

## What you can get [with Version 2024.3.0 (or higher)]

[![sampleview](https://github.com/marq24/ha-waterkotte/raw/main/sample-view-s.png)](https://github.com/marq24/ha-waterkotte/raw/main/sample-view.png)

[[Get the sources for the sample dashboard_above](https://github.com/marq24/ha-waterkotte/blob/main/sample-view.yaml)] - Please note, that this sample dashboard makes use of the custom [multiple-entity-row](https://github.com/benct/lovelace-multiple-entity-row) frontend integration that need to be installed separately. 

## Setup / Installation
if you have installed the previous version of the waterkotte integration from me (marq24) - please [follow the migration guide](https://github.com/marq24/ha-waterkotte/blob/main/README.md#migration).

### Step I: Install the integration

#### Option 1: via HACS
[![Open your Home Assistant instance and adding repository to HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=marq24&repository=ha-waterkotte&category=integration)

- Install [Home Assistant Community Store (HACS)](https://hacs.xyz/)
- Add integration repository (search for "Waterkotte Heatpump [+2020]" in "Explore & Download Repositories")
- Use the 3-dots at the right of the list entry (not at the top bar!) to download/install the custom integration - the latest release version is automatically selected. Only select a different version if you have specific reasons.
- After you presses download and the process has completed, you must __Restart Home Assistant__ to install all dependencies
- Setup the custom integration as described below (see _Step II: Adding or enabling the integration_)

#### Option 2: manual steps

- Copy all files from `custom_components/waterkotte_heatpump/` to `custom_components/waterkotte_heatpump/` inside your config Home Assistant directory.
- Restart Home Assistant to install all dependencies

### Step II: Adding or enabling the integration

__You must have installed the integration (manually or via HACS before)!__

#### Option 1: My Home Assistant (2021.3+)

Just click the following Button to start the configuration automatically (for the rest see _Option 2: Manually steps by step_):

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=waterkotte_heatpump)

#### Option 2: Manually steps by step

Use the following steps for a manual configuration by adding the custom integration using the web interface and follow instruction on screen:

- Go to `Configuration -> Integrations` and add "Waterkotte" integration
- Provide the IP address (or hostname) of your Waterkotte Heatpump web server
- Select the Interface-Type of your Waterkotte (see table below)
- Select the number of TAGs that can be fetched in a single call to your device (older devices might need to adjust this value - for my in 2022 installed Waterkotte 75 is totally fine)
- Provide area where the heatpump is located

#### General additional notes

After the integration was added you can use the 'config' button to adjust your settings and you can additionally modify the update intervall

Please note, that most of the available sensors are __not__ enabled by default.

#### EcoTouch or EasyCon Mode - How to decide?

Please take a look at the different login options and compare with your waterkotte in order to decide, what mode you must select for the integration (sorry only german example screens here)

| EcoTouch | EasyCon                                                                                    |
| --- |--------------------------------------------------------------------------------------------|
| web login form | browser basic-auth                                                                         |
| <img src="https://github.com/marq24/ha-waterkotte/raw/main/login_ecotouch.png" width="350"> | <img src="https://github.com/marq24/ha-waterkotte/raw/main/login_easycon.png" width="350"> |

__Don't get confused!__ The EcoTouch web login for newer Waterkotte models shows the text _EasyCon_ - but when there is a webpage where you must enter the login credentials, then you __must select the EcoTouch__ Mode for this integration!

## Services

The Integration provides currently 5 services:

### Setting dates & times

#### SET_HOLIDAY
To set the times for the holiday mode use the provided service `waterkotte_heatpump.set_holiday` and set `start` and `end` parameter.

#### SET_DISINFECTION_START_TIME
To set the water disinfection start time (HH:MM) use the provided service `waterkotte_heatpump.set_disinfection_start_time` and set `starthhmm` parameter (seconds will be ignored).

#### SET_SCHEDULE

When using the service, first select the schedule (type) you want to adjust [Heating, Cooling, Hot Water, Mixer 1-3, Pool, Buffer Tank Circulation Pump, Solar Control, Photovoltaic], select then the __start time__ and the __end time__, __enable/disable__ the schedule and select the __days__ you would apply the setting.

Additionally, it's possible to specify the __Adjustment I__ and the __Adjustment II__ options. Please be a bit patient when using the Service since there are approx. 100 different tags that have to be written to the heatpump when you apply adjustments for all 7 days.

Please note also, that I did not find a way (yet) to load the current values of the entities into the 'Set a Schedule' dialog. So when adjusting the values via the service you do not see the current values of the fields.

### Get Energy Balance

#### GET_ENERGY_BALANCE
Retrieves the overall energy consumption data for the year

#### GET_ENERGY_BALANCE_MONTHLY
Retrieves the monthly breakdown energy consumption data for a moving 12 month window. 1 = January, 2 = February, etc...

<a href="migration"></a>

## Waterkotte schedule adjustment support

### Introduction

With this the integration it will be possible to adjust the Waterkotte Schedules for:
- Heating
- Cooling
- Hot Water
- Mixer 1, Mixer 2 & Mixer 3
- Pool
- Buffer Tank Circulation Pump
- Solar Control (without adjustment I & adjustment II)
- Photovoltaic (without adjustment I & adjustment II)

The easiest way to adjust a schedule is via the 'Set Schedule' Service that can be found in your HA installation. Only via the service it's possible to adjust the start and end times.

When you want to use/display schedule settings in your HA dashboards or use them in your automations you must enable the optional schedule entities [in the configuration of the integration]. __But be smart__ - only add these additional entities if you really need them. If they are added once it's quite tricky to get rid of them again. Please read further to get additional information about the amount of additional schedule entities that will be added to your HA installation.

### Calculating the amount of additional entities

For each of the Schedules there are per __day__:
1. One __switch__ to turn ON/OFF the schedule
2. Two __switches__ to turn ON/OFF adjustment I & II
3. Two __values__ for each of the adjustments (+/- 10°K)
4. Three __start times__ (one for the schedule, and two for the adjustments)
5. Three __end times__ (one for the schedule, and two for the adjustments)

This makes a total of 11 Sensor-Entities per day - each Schedule consist obviously of 7 days - so for each of the schedules above 77 Sensor-Entities will be available (even if added - all are disabled by default).

This will result in __a total of 659__ additional (new) Sensor-Entities in order to support all Schedules - yes this is not a typo! __SIX HUNDRED FIFTY-NINE__!

So please __only add the additional sensors__ if the use of the 'set schedule service' __is not sufficient for your use case.__ The service can make all the adjustments to your Waterkotte schedules, __without the need of having the additional sensor entities added__.

## Migration Guide

This is the new version of the previous 'ha-waterkotte' repository (which have now been renamed to [`ha-waterkotte-the-fork`](https://github.com/marq24/ha-waterkotte-the-fork)). After the refactoring process have been completed, I have decided to create an independent repository - since the refactored version does not have much in common with the origin sources.

Unfortunately HACS does not 'like' renaming of repositories, so you have to perform few steps in order to upgrade your home assistant installation to the latest ha-waterkotte integration version - sorry for this inconvenience!

### How to migrate to the new integration version
1. make a backup (just in case)
2. go to HACS menu of your home assistant installation
3. remove the (old) custom HACS repository 'https://github.com/marq24/ha-waterkotte'

   (This step will/should remove the Waterkotte Integration entry from the list of installed HACS Integrations)
5. add the __new__ repository 'https://github.com/marq24/ha-waterkotte' to HACS
6. install the waterkotte integration to your local HACS
7. restart your home assistant system

YES - this procedure sounds *totally* silly - but HACS stores a custom-id for each repository - And since I have decided to rename the old repository which base on the work from pattisonmichael to 'https://github.com/marq24/ha-waterkotte-the-fork' and created an independent repository, this procedure is necessary in order to be notified about any future updates.

## Troubleshooting

### Sessions

The Heatpump only allows 2 sessions and there is no way to close a session. Sometimes you will get an error about the login. Just wait a few minutes and it should autocorrect itself. Session usually time out within about 5 min.

### Stale Data

The Heatpump will not always respond with data. This happens usually after the system changes status, e.g. start/stop the heating. There is not much we can do about this, unfortunately. I try to cache the data in possible for a better UX.

## Credits & Kudos

| who                                                    | what                                                                                                                                                                                                                                                                                                                   |
|--------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [@pattisonmichael](https://github.com/pattisonmichael) | This project was initially forked from [Waterkotte-Integration](https://github.com/pattisonmichael/waterkotte-integration) by pattisonmichael  (but both projects drifted apart over time - so this repo is now independent).                                                                                          |
| [@chboland](https://github.com/chboland)               | Christian Boland created a Python Waterkotte library [https://github.com/chboland/pywaterkotte](https://github.com/chboland/pywaterkotte) which was forked by [@pattisonmichael pywatterkotte library](https://github.com/pattisonmichael/pywaterkotte), so this integration is also based on the work from @chboland. |
| [@oncleben31](https://github.com/oncleben31)           | The forked original project was generated via the [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.                                                                                                                                  |
| [@Ludeeus](https://github.com/ludeeus)                 | The forked original code template was mainly taken from the [integration_blueprint](https://github.com/custom-components/integration_blueprint) template                                                                                                                                                               |

---

###### Advertisement / Werbung - alternative way to support me

### Switch to Tibber!

Be smart switch to Tibber - that's what I did in october 2023. If you want to join Tibber (become a customer), you might want to use my personal invitation link. When you use this link, Tibber will grant you and me a bonus of 50,-€ for each of us. This bonus then can be used in the Tibber store (not for your power bill) - e.g. to buy a Tibber Bridge. If you are already a Tibber customer and have not used an invitation link yet, you can also enter one afterward in the Tibber App (up to 14 days). [[see official Tibber support article](https://support.tibber.com/en/articles/4601431-tibber-referral-bonus#h_ae8df266c0)]

Please consider [using my personal Tibber invitation link to join Tibber today](https://invite.tibber.com/6o0kqvzf) or Enter the following code: 6o0kqvzf (six, oscar, zero, kilo, quebec, victor, zulu, foxtrot) afterward in the Tibber App - TIA!

---

[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-blue?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=ccc

[ghs]: https://github.com/sponsors/marq24
[ghsbadge]: https://img.shields.io/github/sponsors/marq24?style=for-the-badge&logo=github&logoColor=ccc&link=https%3A%2F%2Fgithub.com%2Fsponsors%2Fmarq24&label=Sponsors

[buymecoffee]: https://www.buymeacoffee.com/marquardt24
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a-coffee-blue.svg?style=for-the-badge&logo=buymeacoffee&logoColor=ccc

[paypal]: https://paypal.me/marq24
[paypalbadge]: https://img.shields.io/badge/paypal-me-blue.svg?style=for-the-badge&logo=paypal&logoColor=ccc

[wero]: https://share.weropay.eu/p/1/c/6O371wjUW5
[werobadge]: https://img.shields.io/badge/_wero-me_-blue.svg?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZwogICByb2xlPSJpbWciCiAgIHZpZXdCb3g9IjAgMCA0Mi4wNDY1MDEgNDAuODg2NyIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgo+CiAgPGcKICAgICBjbGlwLXBhdGg9InVybCgjY2xpcDApIgogICAgIHRyYW5zZm9ybT0idHJhbnNsYXRlKC01Ny4zODE4KSI+CiAgICA8cGF0aAogICAgICAgZD0ibSA3OC40MDUxLDMwLjM1NzQgYyAwLDAgLTAuMDE4NSwwIC0wLjAyNzgsMCAtNC4zMTg0LDAgLTcuMzQ2MiwtMi41NzY5IC04LjY0NjEsLTUuOTg4NyBIIDk5LjA2OTggQyA5OS4zMDU3LDIzLjA4NDkgOTkuNDI4MywyMS43NzExIDk5LjQyODMsMjAuNDQxIDk5LjQyODMsOS43NTY3MyA5MS43Mzc1LDAuMDEzODc4NyA3OC40MDUxLDAgdiAxMC41MjcgYyA0LjM0MzksMC4wMTE2IDcuMzQxNiwyLjU4MzcgOC42Mjc2LDUuOTg4NyBoIC0yOS4yOTcgYyAtMC4yMzM2LDEuMjgzNyAtMC4zNTM5LDIuNTk3NiAtMC4zNTM5LDMuOTI3NiAwLDEwLjY5MTMgNy43MDAyLDIwLjQ0MzQgMjAuOTk1NSwyMC40NDM0IDAuMDA5MywwIDAuMDE4NSwwIDAuMDI3OCwwIHYgLTEwLjUyNyB6IgogICAgICAgZmlsbD0iI0NDQ0NDQyIvPgogICAgPHBhdGgKICAgICAgIGQ9Im0gNzguMzc3NCw0MC44ODQ0IGMgMC40NTEsMCAwLjg5NTEsLTAuMDEzOSAxLjMzNDYsLTAuMDM0NyAyLjcwMTcsLTAuMTM2NSA1LjE1MzUsLTAuNjgwMSA3LjMzOTMsLTEuNTU2NyAyLjE4NTgsLTAuODc2NyA0LjEwNTcsLTIuMDgxOCA1LjczODcsLTMuNTM5MSAxLjYzMywtMS40NTczIDIuOTgxNSwtMy4xNjQzIDQuMDI3LC01LjA0NDkgMC45NTA2LC0xLjcwOTQgMS42NDQ1LC0zLjU1OTkgMi4wNzk0LC01LjQ5MTMgSCA4Ni42NzIgYyAtMC4yNDk4LDAuNTE1OCAtMC41NDEzLDEuMDA4NSAtMC44NzQ0LDEuNDY4OCAtMC40NTU2LDAuNjI5MSAtMC45ODk5LDEuMjAwNSAtMS41OTYsMS42OTMyIC0wLjYwNiwwLjQ5MjcgLTEuMjg2LDAuOTA5IC0yLjAzNTQsMS4yMzA2IC0wLjc0OTUsMC4zMjE1IC0xLjU2NiwwLjU0ODIgLTIuNDQ5NSwwLjY2MTUgLTAuNDMwMywwLjA1NTUgLTAuODc0NCwwLjA4NzkgLTEuMzM0NywwLjA4NzkgLTIuNzUwMiwwIC00Ljk3NzYsLTEuMDQ3OCAtNi41NjY3LC0yLjY4NzggbCAtNy45NDc2LDcuOTQ3OCBjIDMuNTM2NiwzLjIyOTIgOC40NDI2LDUuMjY0NyAxNC41MTY2LDUuMjY0NyB6IgogICAgICAgZmlsbD0idXJsKCNwYWludDApIgogICAgICAgc3R5bGU9ImZpbGw6dXJsKCNwYWludDApIiAvPgogICAgPHBhdGgKICAgICAgIGQ9Ik0gNzguMzc3NywwIEMgNjcuMTAxNiwwIDU5Ljg1MDIsNy4wMTMzNyA1Ny45MDcyLDE1LjY2OTEgSCA3MC4wOTcgYyAxLjQ1NzIsLTIuOTgxNyA0LjMyNzcsLTUuMTQyMSA4LjI4MDcsLTUuMTQyMSAzLjE1MDMsMCA1LjU5NTIsMS4zNDYyIDcuMTkzNSwzLjM4MTggTCA5My41OTA1LDUuODg5MiBDIDkwLjAwNzYsMi4zMDE1NSA4NC44NTY1LDAuMDAyMzEzMTIgNzguMzc1MywwLjAwMjMxMzEyIFoiCiAgICAgICBmaWxsPSJ1cmwoI3BhaW50MSkiCiAgICAgICBzdHlsZT0iZmlsbDp1cmwoI3BhaW50MSkiIC8+CiAgPC9nPgogIDxkZWZzPgogICAgPGxpbmVhckdyYWRpZW50CiAgICAgICBpZD0icGFpbnQwIgogICAgICAgeDE9IjkyLjc0MzY5OCIKICAgICAgIHkxPSIxOC4wMjYxOTkiCiAgICAgICB4Mj0iNzQuNzU0NTAxIgogICAgICAgeTI9IjQwLjMxMDIiCiAgICAgICBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CiAgICAgIDxzdG9wCiAgICAgICAgIG9mZnNldD0iMC4wMiIKICAgICAgICAgc3RvcC1jb2xvcj0iI0NDQ0NDQyIKICAgICAgICAgc3RvcC1vcGFjaXR5PSIwIi8+CiAgICAgIDxzdG9wCiAgICAgICAgIG9mZnNldD0iMC4zOSIKICAgICAgICAgc3RvcC1jb2xvcj0iI0NDQ0NDQyIKICAgICAgICAgc3RvcC1vcGFjaXR5PSIwLjY2Ii8+CiAgICAgIDxzdG9wCiAgICAgICAgIG9mZnNldD0iMC42OCIKICAgICAgICAgc3RvcC1jb2xvcj0iI0NDQ0NDQyIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudAogICAgICAgaWQ9InBhaW50MSIKICAgICAgIHgxPSI2MS4yNzA0MDEiCiAgICAgICB5MT0iMjMuMDE3Nzk5IgogICAgICAgeDI9Ijc5Ljc1NDUwMSIKICAgICAgIHkyPSI0LjUzNDI5OTkiCiAgICAgICBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CiAgICAgIDxzdG9wCiAgICAgICAgIG9mZnNldD0iMC4wMiIKICAgICAgICAgc3RvcC1jb2xvcj0iI0NDQ0NDQyIKICAgICAgICAgc3RvcC1vcGFjaXR5PSIwIi8+CiAgICAgIDxzdG9wCiAgICAgICAgIG9mZnNldD0iMC4zOSIKICAgICAgICAgc3RvcC1jb2xvcj0iI0NDQ0NDQyIKICAgICAgICAgc3RvcC1vcGFjaXR5PSIwLjY2Ii8+CiAgICAgIDxzdG9wCiAgICAgICAgIG9mZnNldD0iMC42OCIKICAgICAgICAgc3RvcC1jb2xvcj0iI0NDQ0NDQyIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxjbGlwUGF0aAogICAgICAgaWQ9ImNsaXAwIj4KICAgICAgPHJlY3QKICAgICAgICAgd2lkdGg9IjE3Ny45MSIKICAgICAgICAgaGVpZ2h0PSI0MSIKICAgICAgICAgZmlsbD0iI2ZmZmZmZiIKICAgICAgICAgeD0iMCIKICAgICAgICAgeT0iMCIgLz4KICAgIDwvY2xpcFBhdGg+CiAgPC9kZWZzPgo8L3N2Zz4=

[revolut]: https://revolut.me/marq24
[revolutbadge]: https://img.shields.io/badge/_revolut-me_-blue.svg?style=for-the-badge&logo=revolut&logoColor=ccc

[hainstall]: https://my.home-assistant.io/redirect/config_flow_start/?domain=waterkotte_heatpump
[hainstallbadge]: https://img.shields.io/badge/dynamic/json?style=for-the-badge&logo=home-assistant&logoColor=ccc&label=usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.waterkotte_heatpump.total
