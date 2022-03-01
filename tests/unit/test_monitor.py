import os
import pytest

from datetime import datetime

from monitor.events.base import (
    NewTxEvent,
    TxIsReadyForExecuteEvent,
    TxSuccessEvent,
    TxFailedEvent
)

from monitor.app import Monitor, DiscordBot, GnosisService

from tests.mocks import (
    app_config,
    gnosis_tx_response_empty,
    gnosis_tx_response_data
)

discord_bot = DiscordBot(subscribers=[23453452345])


async def test_monitor_events_empty(monkeypatch):

    async def mock_get_safes_all_txs(*args, **kwargs):
        return gnosis_tx_response_empty

    monkeypatch.setattr(
        GnosisService,
        "get_safes_all_txs",
        mock_get_safes_all_txs
    )

    gnosis_service = GnosisService(
        'https://test-gnosis-mock-url.com', None
    )

    monitor = Monitor(discord_bot, gnosis_service, app_config)

    monitor._collection_time = datetime.now()

    await monitor._collect()

    assert len(monitor._events_queue) == 0


async def test_monitor_produces_events(monkeypatch):

    async def mock_get_safes_all_txs(*args, **kwargs):
        return gnosis_tx_response_data

    monkeypatch.setattr(
        GnosisService,
        "get_safes_all_txs",
        mock_get_safes_all_txs
    )

    gnosis_service = GnosisService(
        'https://test-gnosis-mock-url.com', None
    )

    monitor = Monitor(discord_bot, gnosis_service, app_config)

    monitor._collection_time = datetime.fromisoformat(
        '2022-02-24T19:55:00.104'
    )

    await monitor._collect()

    (
        new_tx_event,
        tx_is_ready_exec,
        tx_success,
        tx_failed,
        new_tx_eth
    ) = tuple(monitor._events_queue)

    assert isinstance(new_tx_event, NewTxEvent)
    assert new_tx_event.tx['to'] == '0x40A2aCCbd92BCA938b02010E17A5b8929b49130D'

    assert isinstance(tx_is_ready_exec, TxIsReadyForExecuteEvent)
    assert tx_is_ready_exec.tx['to'] == '0x40A2aCCbd92BCA938b02010E17A5b8929b49130D'

    assert isinstance(tx_success, TxSuccessEvent)
    assert tx_success.tx['to'] == '0xfreraCCbd92BCA938b02010E17A5b8929b4sdafe43'

    assert isinstance(tx_failed, TxFailedEvent)
    assert tx_failed.tx['to'] == '0x93DFH84CCbd92BCA938b02010E17A5b892d9fdDF79'

    assert isinstance(new_tx_eth, NewTxEvent)
    assert new_tx_eth.tx['to'] == '0x5Dce29e92b1b939F8E8C60DcF15BDE82A85be4a9'

    assert len(monitor._events_queue) == 5
