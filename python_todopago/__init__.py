import json
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import requests

from .clients import get_client
from .helpers import Authorization, Item, OperationStatus, object_to_xml
from .serializers import serialize_operation

API = "https://apis.todopago.com.ar/api"


class TodoPagoConnector:
    success_url: str
    failure_url: str
    token: str
    merchant: int

    def __init__(
        self,
        success_url: str,
        failure_url: str,
        token: str = None,
        merchant: int = None,
        username: str = None,
        password: str = None,
    ):
        self.success_url = success_url
        self.failure_url = failure_url

        if not token and (username and password):
            merchant, token = TodoPagoConnector.get_credentials(username, password)

        if not (token and merchant):
            raise Exception()

        self.token = token
        self.merchant = merchant

    @staticmethod
    def get_credentials(
        username: str, password: str
    ) -> Tuple[Optional[int], Optional[str]]:
        body = json.dumps({"USUARIO": username, "CLAVE": password})
        res = requests.post(
            API + "/Credentials",
            body,
            headers={"Content-Type": "application/json"},
        )
        data = res.json().get("Credentials")
        return data.get("merchantId", None), data.get("APIKey", None)

    def create_operation(
        self,
        operation_id: str,
        currency: int,
        amount: Decimal,
        city: str,
        country_code: str,
        state_code: str,
        billing_first_name: str,
        billing_last_name: str,
        billing_email: str,
        billing_phone: str,
        billing_postcode: str,
        billing_address_1: str,
        billing_address_2: Optional[str],
        customer_id: str,
        customer_ip_address: str,
        items: List[Item],
    ) -> Authorization:
        client = get_client(self.token)
        req_body = self._parse_merchant_info()
        operation = serialize_operation(
            self.merchant,
            operation_id,
            currency,
            amount,
            city,
            country_code,
            state_code,
            billing_first_name,
            billing_last_name,
            billing_email,
            billing_phone,
            billing_postcode,
            billing_address_1,
            billing_address_2,
            customer_id,
            customer_ip_address,
            items,
        )
        req_body.update({"Payload": object_to_xml(operation, "Request")})
        res = client.service.SendAuthorizeRequest(**req_body)
        return Authorization(
            res.StatusCode,
            res.StatusMessage,
            res.URL_Request,
            res.RequestKey,
            res.PublicRequestKey,
        )

    def get_operation_status(
        self, request_key: str, answer_key: str
    ) -> OperationStatus:
        client = get_client(self.token)
        req_body = {
            "Security": self.token[-32:],
            "Merchant": self.merchant,
            "RequestKey": request_key,
            "AnswerKey": answer_key,
        }
        res = client.service.GetAuthorizeAnswer(**req_body)
        return OperationStatus(res.StatusCode, res.StatusMessage, res.AuthorizationKey)

    def _parse_merchant_info(self) -> Dict:
        return {
            "Security": self.token[-32:],
            "Merchant": self.merchant,
            "URL_OK": self.success_url,
            "URL_ERROR": self.failure_url,
        }
