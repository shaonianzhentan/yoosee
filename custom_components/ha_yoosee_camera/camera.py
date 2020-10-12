"""Support for Cameras with FFmpeg as decoder."""
import asyncio
import logging

from .yoosee import Yoosee

from haffmpeg.camera import CameraMjpeg
from haffmpeg.tools import IMAGE_JPEG, ImageFrame
import voluptuous as vol

from homeassistant.components.camera import PLATFORM_SCHEMA, SUPPORT_STREAM, Camera
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_yoosee_camera'
CONF_IP = 'ip'
DEFAULT_NAME = "yoosee"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    
    ys = Yoosee(config.get(CONF_IP))
    # 添加PTZ服务
    async def ptz(service):
        ip = service.data.get('ip', '')
        cmd = service.data.get('cmd', '').upper()
        if ip == '' or ['UP', 'DOWN', 'LEFT', 'RIGHT'].count() != 1:
            return
        # 协议命令为DWON，所以要转一下，不知道为啥
        if cmd == 'DOWN':
            cmd = 'DWON'
        await ys.move(ip, cmd)

    hass.services.async_register(DOMAIN, "ptz", ptz)
    
    # 添加Yoosee摄像头
    async_add_entities([YooseeCamera(hass, config)])

class YooseeCamera(Camera):
   
    def __init__(self, hass, config):
        super().__init__()

        """
        1. 首先启动子进程运行ffmpeg命令
        2. 然后将RTSP协议视频转成m3u8文件存放到本地
        """
        self._name = config.get(CONF_NAME)

    @property
    def entity_picture(self):
        """
        1. 获取视频的当前画面，保存到临时目录
        2. 将图片复制到本地目录，替换原有图片
        3. 返回当前图片链接
        """
        return ''

    @property
    def supported_features(self):
        """Return supported features."""
        return SUPPORT_STREAM

    async def stream_source(self):
        """Return the stream source."""
        return ''

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name