from typing import (
    TypedDict, Dict, List
)


class Discord(TypedDict):
    token: str
    subscribers: List[int]


class Gnosis(TypedDict):
    url: str


class Services(TypedDict):
    discord: Discord
    gnosis: Gnosis


class Network(TypedDict):
    label: str
    addr: str


class Multisig(TypedDict):
    networks: Dict[str, List[Network]]


class Config(TypedDict):
    services: Services
    multisig: Multisig
