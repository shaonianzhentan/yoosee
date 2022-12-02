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

import av, io, time
from .const import SERVICE_PTZ
from urllib.parse import urlparse
from .yoosee import Yoosee
from .manifest import manifest

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

        self._attr_name = config.get(CONF_NAME)
        self._attr_supported_features = SUPPORT_STREAM

        self._hostname = parsed.hostname
        self.image_ticks = int(time.time())
        self.last_frame = None
        self.stream_options = {
            'rtsp_transport': 'udp'
        }
        self.ys = Yoosee(self._hostname)
        if hass.services.has_service(manifest.domain, SERVICE_PTZ) == False:
            hass.services.async_register(manifest.domain, SERVICE_PTZ, self.ptz)

    async def ptz(self, call):
        data = call.data
        if data.get('entity_id') == self.entity_id:
            self.ys.ptz(data.get('cmd'))

    async def stream_source(self):
        """Return the stream source."""
        return self._input

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        if not self.stream:
            await self.async_create_stream()
        if self.stream and int(time.time()) - self.image_ticks > 20:
            # 距离上一次刷新时间20秒，再次更新
            self.image_ticks = int(time.time())
            try:
                SOURCE_TIMEOUT = 30
                container = av.open(self.stream.source, options=self.stream.options, timeout=SOURCE_TIMEOUT)
                count = 0
                for frame in container.decode(video=0):
                    count = count + 1
                    if count > 30:
                        imgByteArr = io.BytesIO()
                        frame.to_image().save(imgByteArr, format='JPEG')
                        # 获取成功后，重置时间
                        self.image_ticks = self.image_ticks - 20
                        self.last_frame = imgByteArr.getvalue()
                        return self.last_frame
            except Exception as ex:
                print(ex)
                self.image_ticks = self.image_ticks - 20
        return self.last_frame
    
    @property
    def device_info(self):
        return {
            "identifiers": {
                (manifest.domain, self._attr_unique_id)
            },
            "name": self.name,
            "manufacturer": "Yoosee",
            "model": self._hostname,
            "sw_version": manifest.version,
            "via_device": (manifest.domain, self._attr_unique_id),
        }