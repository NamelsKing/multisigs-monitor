import typing as t

from datetime import datetime, timedelta

from monitor.services.utils import gnosis_date_to_iso

from monitor.services.types import (
    GnosisAllTxsType,
    GnosisAllTransactionsResp,
    GnosisAllTransactionsMultisigResp,
    GnosisAllTransactionsEthereumTxResp
)

from .base import BaseEvent


def gnosis_tx_list_data_filter(
    collection_time: datetime,
    data: GnosisAllTransactionsResp
) -> t.List[BaseEvent]:
    filtered_txs = []

    past_time = datetime.now() - timedelta(days=300)

    for tx in data:
        have_nonce = None

        try:
            have_nonce = tx['nonce']
        except KeyError:
            continue

        if not bool(have_nonce):
            continue

        if tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            submission_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['submissionDate'])
            ) if tx['submissionDate'] else past_time
            modified_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['modified'])
            ) if tx['modified'] else past_time
            execution_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['executionDate'])
            ) if tx['executionDate'] else past_time

            if submission_date > collection_time or (
                modified_date > collection_time
            ) or execution_date > collection_time:
                filtered_txs.append(tx)

        if tx['txType'] == GnosisAllTxsType.ETHEREUM_TRANSACTION.value:
            execution_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['executionDate'])
            ) if tx['executionDate'] else past_time

            if execution_date > collection_time:
                filtered_txs.append(tx)

        if tx['txType'] == GnosisAllTxsType.MODULE_TRANSACTION.value:
            # just coz I couldn't find this type in response
            continue

    return filtered_txs
