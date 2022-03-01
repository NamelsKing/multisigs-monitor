import typing as t

import discord
import asyncio
import logging

from monitor.types import Discord

log = logging.getLogger(__name__)


class DiscordBot(discord.Client):
    def __init__(
        self,
        *args,
        subscribers: t.List[str] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.subscribers = subscribers

    async def on_ready(self):
        log.info(f'Logged in as {self.user.name}:{self.user.id}')

    async def publish_to_subscribers(
        self,
        msg: str
    ):
        if not self.is_ready():
            log.info('Bot is not connected yet')
            return

        for channel_id in self.subscribers:
            channel = self.get_channel(channel_id)

            try:
                await channel.send(msg)
            except Exception as err:
                log.error(
                    f'Failed to send msg to channel: {channel} \n'
                    f'With error: {err}'
                )

            log.info(
                f'Msg to channel: {channel_id}, with content {msg} was sent'
            )
