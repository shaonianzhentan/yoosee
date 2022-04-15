from __future__ import annotations

import voluptuous as vol

from homeassistant.components.camera import (
    DEFAULT_CONTENT_TYPE,
    PLATFORM_SCHEMA,
    Camera,
    SUPPORT_STREAM,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

import av, io
from .const import DOMAIN, DEFAULT_NAME, VERSION, SERVICE_PTZ
from urllib.parse import urlparse
from .yoosee import Yoosee

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    async_add_entities([YooseeCamera(hass, entry.data, entry.entry_id)], True)

class YooseeCamera(Camera):
   
    def __init__(self, hass, config, identifier):
        super().__init__()
        self._attr_unique_id = identifier
        url = config.get('url')
        parsed = urlparse(url)
        self._input = url
        self._name = config.get(CONF_NAME)
        self._hostname = parsed.hostname
        self._attr_supported_features = SUPPORT_STREAM
        self.image_loading = False
        self.stream_options = {
            'rtsp_transport': 'udp'
        }
        if hass.services.has_service(DOMAIN, SERVICE_PTZ) == False:
            hass.services.async_register(DOMAIN, SERVICE_PTZ, self.ptz)

    async def ptz(self, call):
        data = call.data
        if data.get('entity_id') == self.entity_id:
            ys = Yoosee(self._hostname)
            ys.ptz(data.get('cmd'))

    async def stream_source(self):
        """Return the stream source."""
        return self._input

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        if not self.stream:
            await self.async_create_stream()
        if self.stream and self.image_loading == False:
            self.image_loading = True
            SOURCE_TIMEOUT = 30
            container = av.open(self.stream.source, options=self.stream.options, timeout=SOURCE_TIMEOUT)
            count = 0
            for frame in container.decode(video=0):
                count = count + 1
                if count > 30:
                    imgByteArr = io.BytesIO()
                    frame.to_image().save(imgByteArr, format='JPEG')
                    self.image_loading = False
                    return imgByteArr.getvalue()
            
            self.image_loading = False
        return None

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name
    
    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._attr_unique_id)
            },
            "name": self.name,
            "manufacturer": "Yoosee",
            "model": self._hostname,
            "sw_version": VERSION,
            "via_device": (DOMAIN, self._attr_unique_id),
        }