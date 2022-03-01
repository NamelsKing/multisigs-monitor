import typing as t

from datetime import datetime

from .base import BaseEvent, NotificationEvent

from .filters import gnosis_tx_list_data_filter

from .types import DataSrouce, CollectorContract


class EventsCollector:
    _events: t.List[BaseEvent] = []

    _filters_map = {
        DataSrouce.GNOSIS_TX_LIST: gnosis_tx_list_data_filter
    }

    source: DataSrouce
    data: t.Any
    contract: CollectorContract
    collection_time: datetime

    def __init__(
        self,
        source: DataSrouce,
        data: t.Any,
        contract: CollectorContract,
        collection_time: datetime
    ):
        self.source = source
        self.data = data
        self.contract = contract
        self.collection_time = collection_time

    def process(self) -> 'EventsCollector':
        data = self.data
        data_filter = None

        try:
            data_filter = self._filters_map[self.source]
            data = data_filter(
                self.collection_time, data
            )
        except KeyError:
            pass

        for tx in data:
            self._events.append(
                NotificationEvent.factory(
                    self.source, tx,
                    self.contract, self.collection_time
                )
            )

        return self

    def grab_events(self) -> t.List[BaseEvent]:
        return [event for event in self._events if event is not None]
