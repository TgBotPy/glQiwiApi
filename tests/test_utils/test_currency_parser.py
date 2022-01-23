import pytest

from glQiwiApi.base import described
from glQiwiApi.utils.currency_util import Currency

pytestmark = pytest.mark.asyncio


@pytest.fixture(name="_")
def currency_fixture():
    """:class:`Currency` fixture"""
    _ = Currency()
    yield _


async def test_currency_parser(_: Currency):
    from glQiwiApi.base import CurrencyModel

    condition = all(isinstance(_.get(key), CurrencyModel) for key in described.keys())
    assert condition
