from datetime import datetime, timedelta
from typing import ClassVar, List, Optional, Dict, Any


from pydantic import root_validator, Field

from glQiwiApi.base.api_method import APIMethod, Request
from glQiwiApi.qiwi.clients.wallet.types import Statistic, TransactionType
from glQiwiApi.utils.dates_conversion import datetime_to_iso8601_with_moscow_timezone


class FetchStatistics(APIMethod[Statistic]):
    url: ClassVar[str] = "https://edge.qiwi.com/payment-history/v2/persons/{phone_number}/payments/total"
    http_method: ClassVar[str] = "GET"

    start_date: datetime = Field(default_factory=datetime.now)
    end_date: datetime = Field(default_factory=lambda: datetime.now() - timedelta(days=90))
    operation: TransactionType = TransactionType.ALL
    sources: Optional[List[str]] = None

    @root_validator()
    def check_start_date_and_end_date_difference_not_greater_than_90_days(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        start_date: datetime = values["start_date"]
        end_date: datetime = values["end_date"]

        if (end_date - start_date).days > 90 or (start_date - end_date).days > 90:
            raise ValueError("The maximum period for downloading statistics is 90 calendar days.")

        return values

    def build_request(self, **url_format_kw: Any) -> Request:
        params = {
            "startDate": datetime_to_iso8601_with_moscow_timezone(self.start_date),
            "endDate": datetime_to_iso8601_with_moscow_timezone(self.end_date),
            "operation": self.operation.value,
        }
        if self.sources:
            params.update({"sources": " ".join(self.sources)})
        return Request(
            endpoint=self.url.format(**url_format_kw),
            params=params,
            http_method=self.http_method
        )
