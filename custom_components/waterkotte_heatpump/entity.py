"""WaterkotteHeatpumpEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
# from .const import ATTRIBUTION
from .const import DOMAIN
from .const import NAME
# from .const import VERSION


class WaterkotteHeatpumpEntity(CoordinatorEntity):
    """ WaterkotteHeatpumpEntity Main common Class """

    def __init__(self, coordinator, config_entry):
        self.config_entry = config_entry
        super().__init__(coordinator)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.data['serial']
        # return self.config_entry.entry_id

    @property
    def device_info(self):
        ip = self.config_entry.data['ip'] if isinstance(self.config_entry, ConfigEntry) else self.config_entry.config_entry.data['ip']  # pylint: disable=line-too-long,invalid-name
        serial = self.config_entry.data['serial'] if isinstance(self.config_entry, ConfigEntry) else self.config_entry.config_entry.data['serial']  # pylint: disable=line-too-long
        device = self.config_entry.entry_id if isinstance(self.config_entry, ConfigEntry)else self.config_entry.config_entry.entry_id  # pylint: disable=line-too-long
        series = self.config_entry.data['series'] if isinstance(self.config_entry, ConfigEntry) else self.config_entry.config_entry.data['series']  # pylint: disable=line-too-long
        deviceid = self.config_entry.data['id'] if isinstance(self.config_entry, ConfigEntry) else self.config_entry.config_entry.data['id']  # pylint: disable=line-too-long
        fw = self.config_entry.data['fw'] if isinstance(self.config_entry, ConfigEntry) else self.config_entry.config_entry.data['fw']  # pylint: disable=line-too-long,invalid-name
        bios = self.config_entry.data['bios'] if isinstance(self.config_entry, ConfigEntry) else self.config_entry.config_entry.data['bios']  # pylint: disable=line-too-long
        return {
            "identifiers": {
                (DOMAIN, self.unique_id),
                ("IP", ip),
                ('device', device),
                ('serial', serial)
            },
            "name": series,
            "model": deviceid,
            "manufacturer": NAME,
            "sw_version": f"{fw} BIOS: {bios}",
        }
        # return DeviceInfo(
        #     id=DOMAIN,
        #     identifiers={
        #         # Serial numbers are unique identifiers within a specific domain
        #         #                (DOMAIN
        #         # , self.unique_id
        #         #                )
        #         (DOMAIN, self._device_id),
        #         ("IP", self._entry_data['ip']),
        #         ('device', self._device_id)
        #     },
        #     name=NAME,
        #     manufacturer=NAME,
        #     model="modelstr",
        #     sw_version=f"{self._entry_data['fw']} BIOS:{self._entry_data['bios']}",
        #     # via_device=(hue.DOMAIN, self.api.bridgeid),
        # )

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            # "attribution": ATTRIBUTION,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }
