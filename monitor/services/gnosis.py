import asyncio
import logging

from typing import (
    Optional, Tuple, Union, List
)

from aiohttp import ClientSession
from json import JSONDecodeError

from .types import GnosisAllTransactionsResp

log = logging.getLogger(__name__)


class GnosisServiceError(Exception):
    pass


class GnosisService:
    UNKNOWN_ERROR_MESSAGE = 'Ooops, something went wrong'
    REQUEST_TIMEOUT = 5  # sec

    SAFES_ALL_TXS_PATH = '/safes/{address}/all-transactions/'

    def __init__(
        self,
        base_url: str,
        aiohttp_session: ClientSession
    ):
        self.base_url = base_url
        self.session = aiohttp_session

    def constaruct_api_url(self, path: Optional[str]) -> str:
        if not path:
            return self.base_url

        return f'{self.base_url}{path}'

    @staticmethod
    def inject_rest_param(
        path: str,
        params: Optional[dict] = None
    ) -> str:
        if not params:
            return path

        formatted_path = path

        for key in list(params.keys()):
            formatted_path = path.replace(f'{{{key}}}', params[key])

        return formatted_path

    async def _call_get(
            self,
            path: Optional[str] = '',
            rest_params: Optional[dict] = None,
            params: Optional[dict] = None,
    ) -> Tuple[dict, Optional[int]]:

        path_with_rest_params = GnosisService.inject_rest_param(
            path, rest_params
        )
        url = self.constaruct_api_url(path_with_rest_params)

        headers = {
            'content-type': 'application/json',
        }

        try:
            async with self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=None
            ) as resp:
                query_response = await resp.json()
                return query_response, resp.status
        except JSONDecodeError:
            log.exception('Failed to parse Etherscan response', exc_info={
                'response': await resp.text(),
                'url': url
            })
            return {}, None
        except asyncio.TimeoutError:
            log.exception('timeout request to Etherscan', exc_info={
                'url': url
            })
            return {}, None

    async def get_safes_all_txs(
        self,
        address: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[GnosisAllTransactionsResp]:
        params = {
            'limit': limit,
        }

        if offset > 0:
            params['offset'] = offset

        rest_params = {
            'address': address
        }

        response_data, status = await self._call_get(
            self.SAFES_ALL_TXS_PATH,
            rest_params=rest_params,
            params=params
        )

        if status != 200 or response_data.get('results') is None:
            log.error(
                f'get_safes_all_txs failed {response_data}',
            )
            message = self.UNKNOWN_ERROR_MESSAGE
            if response_data:
                message = response_data.get('message', message)
            raise GnosisServiceError(message)

        return response_data.get('results')
