import logging
import asyncio

from typing import Dict, Any

from aiohttp import TCPConnector, ClientSession

from monitor.config import Config


log = logging.getLogger(__name__)


def init_aiohttp_session(
    loop: asyncio.AbstractEventLoop
) -> ClientSession:
    tcp_connector = TCPConnector(
        ssl=False,
        loop=loop,
    )
    aio_http_session = ClientSession(
        loop=loop,
        connector=tcp_connector
    )

    return aio_http_session
