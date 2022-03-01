import logging
import asyncio
import typing as t

from datetime import datetime, timedelta

from functools import reduce

from monitor.config import Config

from monitor.services.gnosis import GnosisService
from monitor.services.bot import DiscordBot

from monitor.events.collector import EventsCollector
from monitor.events.base import BaseEvent
from monitor.events.types import DataSrouce

FIVE_MINS_IN_SEC = 60 * 5

log = logging.getLogger(__name__)


class Monitor:
    _running: bool
    _collection_time: datetime
    _collect_interval: int = FIVE_MINS_IN_SEC
    _events_queue: t.List[BaseEvent] = []

    discord_bot: DiscordBot
    gnosis_service: GnosisService
    config: Config

    def __init__(
        self,
        discord_bot: DiscordBot,
        gnosis_service: GnosisService,
        config: Config
    ):
        self.discord_bot = discord_bot
        self.gnosis_service = gnosis_service

        self.config = config

    async def launch(self):
        self._running = True

        # here could be a problem, if transactions appear
        # in gnosis db later than loop interval fallbacks
        # can be solved by separation of loop interval and fallback time
        # /collect time, and cr8 hash map with garbage collections
        while self._running:
            # debug
            # await asyncio.sleep(10)
            # ---
            await asyncio.sleep(self._collect_interval)

            # debug
            # self._collection_time = datetime.now() - timedelta(
            #     hours=5
            # )
            # ---
            # delta should equal to sleep time
            self._collection_time = datetime.now() - timedelta(
                seconds=self._collect_interval + 10
            )

            await self._collect()
            await self._publish()

            self._clear_queue()

            # debug
            # exit(1)
            # ---

    def stop(self):
        self._running = False

    def _clear_queue(self):
        if len(self._events_queue) == 0:
            return

        log.info(f'Events cleared after send {self._events_queue}')

        self._events_queue = []

    async def _collect(self):
        networks = self.config['multisig']['networks']

        # possible improvement: combine all io calls with asyncio.wait
        # and limit them with asyncio.Semaphore if needed
        for nw_key in networks.keys():
            for contract in networks[nw_key]:

                # mb here timeout will be needed in case gnosis has
                # rps limitations for public api
                try:
                    gnosis_txs_data = (
                        await self.gnosis_service.get_safes_all_txs(
                            contract['addr']
                        )
                    )
                except Exception as err:
                    log.error(
                        f'Failed to fetch gnosis data for '
                        f'contract {contract["addr"]} \n Error: {err}'
                    )
                    continue

                contract = {
                    'network': nw_key,
                    'label': contract['label'],
                    'addr': contract['addr'],
                }

                self._events_queue += EventsCollector(
                    source=DataSrouce.GNOSIS_TX_LIST,
                    data=gnosis_txs_data,
                    contract=contract,
                    collection_time=self._collection_time
                ).process().grab_events()

    async def _publish(self):
        if len(self._events_queue) == 0:
            log.info('Nothing to publish from _event_queue')
            return

        BUTCH_SIZE = 6
        
        def _events_reduce_func(acc, _inner_event) -> t.Dict[str, str]:
            batched_events = acc['batched_events']

            curr_batch_ix = acc['current_batch_ix']
            curr_batched_events = []

            try:
                curr_batched_events = batched_events[curr_batch_ix]
            except IndexError:
                batched_events.append(curr_batched_events)

            curr_batched_events.append(_inner_event.serialize())
            curr_batched_events.append('---')

            if len(curr_batched_events) > BUTCH_SIZE:
                acc['current_batch_ix'] += 1

            return acc

        serialized_events_accum = reduce(
            _events_reduce_func,
            self._events_queue, {
                'current_batch_ix': 0,
                'batched_events': []
            }
        )

        # There can be a lot of events, so send them with small batches
        # for not to face apis limits
        for events_batch in serialized_events_accum['batched_events']:
            await self.discord_bot.publish_to_subscribers(
                '\n'.join(events_batch)
            )
