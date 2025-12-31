import logging

from bleak import BleakClient

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.components.switch import SwitchEntity

from .const import (
    DOMAIN,
    DEVICE_NAME,
    MANUFACTURER,
    MODEL,
    CHARACTERISTIC_UUID,
    POWER_ON_COMMAND,
    POWER_OFF_COMMAND,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            IPixelBKLightPowerSwitch(
                hass,
                entry.data["address"],
                entry.data["name"],
            )
        ]
    )


class IPixelBKLightPowerSwitch(SwitchEntity):
    _attr_icon = "mdi:led-matrix"
    _attr_has_entity_name = True

    def __init__(self, hass, address, name):
        self.hass = hass
        self.address = address
        self._attr_name = name
        self._attr_is_on = True  # optimistic

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.address)},
            "name": DEVICE_NAME,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "connections": {("bluetooth", self.address)},
        }

    async def _send_command(self, command: bytearray):
        device = async_ble_device_from_address(
            self.hass,
            self.address,
        )

        if device is None:
            raise RuntimeError("BLE device not found")

        client = BleakClient(device)

        try:
            await client.connect(timeout=10)
            await client.write_gatt_char(
                CHARACTERISTIC_UUID,
                command,
                response=False,
            )
        finally:
            await client.disconnect()

    async def async_turn_on(self, **kwargs):
        await self._send_command(POWER_ON_COMMAND)
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs):
        await self._send_command(POWER_OFF_COMMAND)
        self._attr_is_on = False
