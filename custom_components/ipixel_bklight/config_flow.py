import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import async_discovered_devices

from .const import DOMAIN


class IPixelBKLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        devices = async_discovered_devices(self.hass)

        ble_devices = {
            device.address: f"{device.name or 'Unknown'} ({device.address})"
            for device in devices
        }

        schema = vol.Schema(
            {
                vol.Required("address"): vol.In(ble_devices),
                vol.Required(
                    "name",
                    default="BK-Light iPixel",
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
