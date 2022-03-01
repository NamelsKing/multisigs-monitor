import typing as t

from enum import Enum


class GnosisAllTxsType(Enum):
    MULTISIG_TRANSACTION = 'MULTISIG_TRANSACTION'
    ETHEREUM_TRANSACTION = 'ETHEREUM_TRANSACTION'
    MODULE_TRANSACTION = 'MODULE_TRANSACTION'


class GnosisAllTransactionsMultisigConfirmation(t.TypedDict):
    owner: str
    submissionDate: str
    transactionHash: str
    signature: str
    signatureType: str


class GnosisAllTransactionsTokenInfo(t.TypedDict):
    type: str
    address: str
    name: str
    symbol: str
    decimals: int
    logoUri: str


class GnosisAllTransactionsTrasfersWithTokens(t.TypedDict):
    type: str
    executionDate: str
    blockNumber: int
    transactionHash: str
    to: str
    value: t.Optional[str]
    tokenId: t.Optional[str]
    tokenAddress: t.Optional[str]
    tokenInfo: GnosisAllTransactionsTokenInfo
    fromAddr: str


class GnosisAllTransactionsModuleResp(t.TypedDict):
    created: t.Optional[str]
    executionDate: str
    blockNumber: int
    isSuccessful: bool
    transactionHash: str
    safe: str
    module: str
    to: str
    value: str
    date: t.Optional[str]
    operation: int
    dataDecoded: int
    transfers: t.List[GnosisAllTransactionsTrasfersWithTokens]
    txType: str


class GnosisAllTransactionsMultisigResp(t.TypedDict):
    submissionDate: str
    executionDate: str
    isExecuted: bool
    isSuccessful: bool
    confirmationsRequired: int
    confirmations: t.List[GnosisAllTransactionsMultisigConfirmation]
    ethGasPrice: bool
    safe: str
    to: str
    data: str
    operation: int
    gasToken: int
    safeTxGas: int
    baseGas: int
    gasPrice: int
    refundReceiver: str
    nonce: int
    modified: str
    blockNumber: int
    transactionHash: str
    safeTxHash: str
    executor: str
    gasUsed: int
    fee: int
    origin: str
    dataDecoded: str
    signatures: str
    transfers: t.List[GnosisAllTransactionsTrasfersWithTokens]
    txType: str


class GnosisAllTransactionsEthereumTxResp(t.TypedDict):
    executionDate: str
    to: str
    data: str
    txHash: str
    blockNumber: int
    transfers: t.List[GnosisAllTransactionsTrasfersWithTokens]
    fromAddr: str
    txType: str


GnosisAllTransactionsResp = t.Union[
    GnosisAllTransactionsModuleResp,
    GnosisAllTransactionsMultisigResp,
    GnosisAllTransactionsEthereumTxResp
]
