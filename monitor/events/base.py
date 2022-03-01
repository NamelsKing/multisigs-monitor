import typing as t

from datetime import datetime, timedelta

from monitor.services.utils import gnosis_date_to_iso

from monitor.services.types import GnosisAllTxsType

from .types import DataSrouce, CollectorContract


class BaseEvent:
    source: DataSrouce
    tx: t.Any
    contract: CollectorContract

    def __init__(
        self, source: DataSrouce, tx: t.Any,
        contract: CollectorContract,
    ):
        self.source = source
        self.tx = tx
        self.contract = contract

    @classmethod
    def check(
        cls,
        source: DataSrouce,
        tx: t.Any,
        collection_time: datetime
    ) -> bool:
        _checkers_map = {
            DataSrouce.GNOSIS_TX_LIST: cls.check_tx_list
        }

        tx['collection_time'] = collection_time

        return _checkers_map[source](tx)

    def serialize(self) -> str:
        _serializers_map = {
            DataSrouce.GNOSIS_TX_LIST: {
                'func': self.serialize_tx_list,
                'text': (
                    f'📩 `{self.__class__.__name__}` has landed; \n'
                    f'🏭 Network: `{self.contract["network"]}`;    '
                    f'🎑 Label: `{self.contract["label"]}`; \n'
                    f'📃 On addr: `{self.contract["addr"]}`; \n'
                )
            }
        }

        serializer_func = _serializers_map[self.source]['func']
        serializer_text = _serializers_map[self.source]['text']

        return serializer_func(serializer_text)


class NewTxEvent(BaseEvent):
    @staticmethod
    def check_tx_list(tx: t.Any) -> bool:
        past_time = datetime.now() - timedelta(days=300)

        if tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            submission_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['submissionDate'])
            ) if tx['submissionDate'] else past_time

            return submission_date > tx['collection_time']
        if tx['txType'] == GnosisAllTxsType.ETHEREUM_TRANSACTION.value:
            execution_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['executionDate'])
            ) if tx['executionDate'] else past_time

            return execution_date > tx['collection_time']

        return False

    def serialize_tx_list(self, text: str) -> str:
        serialized_text = text

        if self.tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            serialized_text += (
                f'📃 To addr: `{self.tx["to"]}`; \n'
                f'🗂 TxType: `{self.tx["txType"]}`; \n'
                f'#️⃣ TransactionHash: `{self.tx["transactionHash"]}`; \n'
                f'🔢 BlockNumber: `{self.tx["blockNumber"]}`; \n'
                f'🛂 Executor: `{self.tx["executor"]}`; \n'
            )
        if self.tx['txType'] == GnosisAllTxsType.ETHEREUM_TRANSACTION.value:
            serialized_text += (
                f'📃 To addr: `{self.tx["to"]}`; \n'
                f'🗂 TxType: `{self.tx["txType"]}`; \n'
                f'#️⃣ TransactionHash: `{self.tx["txHash"]}`; \n'
                f'🔢 BlockNumber: `{self.tx["blockNumber"]}`; \n'
            )

        return serialized_text


class TxIsReadyForExecuteEvent(BaseEvent):
    @staticmethod
    def check_tx_list(tx: t.Any) -> bool:
        if tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            past_time = datetime.now() - timedelta(days=300)

            modified_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['modified'])
            ) if tx['modified'] else past_time

            confirmations_required = tx['confirmationsRequired'] or 0
            confirmations = tx['confirmations'] or []

            return modified_date > tx['collection_time'] and (
                confirmations_required > 0 and len(confirmations) > 0
            ) and confirmations_required == len(confirmations) and not (
                tx['isExecuted']
            )

        return False

    def serialize_tx_list(self, text: str) -> str:
        serialized_text = text

        if self.tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            serialized_text += (
                f'📃 To addr `{self.tx["to"]}`; \n'
                f'🗂 TxType `{self.tx["txType"]}`; \n'
                f'#️⃣ TransactionHash `{self.tx["transactionHash"]}`; \n'
                f'🔢 BlockNumber `{self.tx["blockNumber"]}`; \n'
                f'🛂 Executor `{self.tx["executor"]}`; \n'
                f'🏛 Confirmations Required - `{self.tx["confirmationsRequired"]}`; \n'
                f'🏛 Confirmations Done - `{len(self.tx["confirmations"])}`; \n'
            )

        return serialized_text


class TxSuccessEvent(BaseEvent):
    @staticmethod
    def check_tx_list(tx: t.Any) -> bool:
        if tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            past_time = datetime.now() - timedelta(days=300)

            execution_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['executionDate'])
            ) if tx['executionDate'] else past_time

            return execution_date > tx['collection_time'] and (
                tx['isExecuted'] and tx['isSuccessful']
            )

        return False

    def serialize_tx_list(self, text: str) -> str:
        serialized_text = text

        if self.tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            serialized_text += (
                f'📃 To addr `{self.tx["to"]}`; \n'
                f'🗂 TxType `{self.tx["txType"]}`; \n'
                f'#️⃣ TransactionHash `{self.tx["transactionHash"]}`; \n'
                f'🔢 BlockNumber `{self.tx["blockNumber"]}`; \n'
                f'🛂 Executor `{self.tx["executor"]}`; \n'
            )

        return serialized_text


class TxFailedEvent(BaseEvent):
    @staticmethod
    def check_tx_list(tx: t.Any) -> bool:
        if tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            past_time = datetime.now() - timedelta(days=300)

            execution_date = datetime.fromisoformat(
                gnosis_date_to_iso(tx['executionDate'])
            ) if tx['executionDate'] else past_time

            return execution_date > tx['collection_time'] and (
                tx['isExecuted'] and (tx['isSuccessful'] is False)
            )

        return False

    def serialize_tx_list(self, text: str) -> str:
        serialized_text = text

        if self.tx['txType'] == GnosisAllTxsType.MULTISIG_TRANSACTION.value:
            serialized_text += (
                f'📃 To addr `{self.tx["to"]}`; \n'
                f'🗂 TxType `{self.tx["txType"]}`; \n'
                f'#️⃣ TransactionHash `{self.tx["transactionHash"]}`; \n'
                f'🔢 BlockNumber `{self.tx["blockNumber"]}`; \n'
                f'🛂 Executor `{self.tx["executor"]}`; \n'
            )

        return serialized_text


class NotificationEvent:
    _events_class_map = {
        DataSrouce.GNOSIS_TX_LIST: [
            NewTxEvent,
            TxIsReadyForExecuteEvent,
            TxSuccessEvent,
            TxFailedEvent
        ]
    }

    @staticmethod
    def factory(
        source: DataSrouce, tx: t.Any,
        contract: CollectorContract,
        collection_time: datetime
    ) -> t.Optional[BaseEvent]:
        events = NotificationEvent._events_class_map[source]

        for event in events:
            if event.check(source, tx, collection_time):
                return event(source, tx, contract)

        return None
