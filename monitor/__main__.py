import sys
import asyncio
import logging
import typing as t

from aiohttp import web, web_runner, helpers, ClientSession

from monitor.config import get_config
from monitor.infrastructure.logging import setup_logger
from monitor.infrastructure.http import init_aiohttp_session

from monitor.services.gnosis import GnosisService
from monitor.services.bot import DiscordBot
from monitor.app import Monitor


log = logging.getLogger(__name__)

setup_logger()

loop = asyncio.get_event_loop()
config = get_config()
discord_bot = DiscordBot(
    subscribers=config['services']['discord']['subscribers']
)

monitor: t.Optional[Monitor] = None
aiohttp_session: t.Optional[ClientSession] = None


async def monitor_task():
    global monitor
    global aiohttp_session

    aiohttp_session = init_aiohttp_session(loop)

    gnosis_service = GnosisService(
        config['services']['gnosis']['url'], aiohttp_session
    )

    monitor = Monitor(discord_bot, gnosis_service, config)

    log.info('Monitor service has started')

    await monitor.launch()


if __name__ == '__main__':
    try:
        loop.create_task(monitor_task())

        discord_bot.run(config['services']['discord']['token'])

    except (web_runner.GracefulExit, KeyboardInterrupt):  # pragma: no cover
        log.info('Shutting down bot monitor')

        monitor.stop()
        aiohttp_session.close()
