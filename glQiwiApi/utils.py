import re
import time
from copy import deepcopy
from datetime import datetime
from typing import (TypeVar, Callable, Union, Any, Dict, Type, Iterable, List, Optional, Literal)
import functools as ft
from pytz.reference import Local

from glQiwiApi.configs import DEFAULT_YOOMONEY_HEADERS
from glQiwiApi.data import Transaction, Commission, Bill, Limit, Identification, WrapperData, AccountInfo, Operation

F = TypeVar('F', bound=Callable[..., Any])


def measure_time(func: F):
    @ft.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        await func(*args, **kwargs)
        print(f'Executed for {time.monotonic() - start_time} secs')

    return wrapper


def datetime_to_str_in_iso(obj: datetime) -> Optional[str]:
    if not isinstance(obj, datetime):
        return ''
    return obj.isoformat(' ').replace(" ", "T") + re.findall(r'[+]\d{2}[:]\d{2}', str(datetime.now(tz=Local)))[0]


def parse_auth_link(response_data: Union[str, bytes]) -> str:
    return re.findall(r'https://yoomoney.ru/oauth2/authorize[?]requestid[=]\w+', str(response_data))[0]


def parse_headers(content_json: bool = False, auth: bool = False) -> Dict[Any, Any]:
    """
    Функция для добавления некоторых заголовков в запрос

    """
    headers = deepcopy(DEFAULT_YOOMONEY_HEADERS)
    if content_json:
        headers.update(
            {'Accept': 'application/json'}
        )
    if auth:
        headers.update(
            {'Authorization': 'Bearer {token}'}
        )
    return headers


class DataFormatter:

    @staticmethod
    def set_data_to_wallet(
            data: WrapperData,
            to_number: str,
            trans_sum: Union[str, int, float],
            comment: str,
            currency: str = '643'):
        data.json['sum']['amount'] = str(trans_sum)
        data.json['sum']['currency'] = currency
        data.json['fields']['account'] = to_number
        data.json['comment'] = comment
        data.headers.update({'User-Agent': 'Android v3.2.0 MKT'})
        return data

    @staticmethod
    def format_objects(
            iterable_obj: Iterable,
            obj: Type,
            transfers: Optional[Dict[str, str]] = None,
    ) -> Optional[List[Union[Transaction, Identification, Limit, Bill, Commission, AccountInfo, Operation]]]:
        kwargs = {}
        objects = []
        for transaction in iterable_obj:
            for key, value in transaction.items():
                if key in obj.__dict__.get('__annotations__').keys():
                    kwargs.update({
                        key: value
                    })
                elif key in transfers.keys():
                    kwargs.update({
                        transfers.get(key): value
                    })
            objects.append(obj(**kwargs))
            kwargs = {}
        return objects

    def set_data_p2p_create(self, wrapped_data: WrapperData,
                            amount: Union[str, int, float],
                            life_time: str,
                            comment: Optional[str] = None,
                            theme_code: Optional[str] = None,
                            pay_source_filter: Optional[Literal['qw', 'card', 'mobile']] = None
                            ):
        wrapped_data.json['amount']['value'] = str(amount)
        wrapped_data.json['comment'] = comment
        wrapped_data.json['expirationDateTime'] = life_time
        if pay_source_filter in ['qw', 'card', 'mobile']:
            wrapped_data.json['customFields']['paySourcesFilter'] = pay_source_filter
        if isinstance(theme_code, str):
            wrapped_data.json['customFields']['theme_code'] = theme_code
        if not isinstance(theme_code, str) and pay_source_filter not in ['qw', 'card', 'mobile']:
            wrapped_data.json.pop('customFields')
        return wrapped_data.json
