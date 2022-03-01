import typing as t

from enum import Enum


class DataSrouce(Enum):
    GNOSIS_TX_LIST = 1


class CollectorContract(t.TypedDict):
    network: str
    label: str
    addr: str
