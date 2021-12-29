import json
from dataclasses import asdict
from decimal import Decimal
from typing import List, Optional

import requests

from .clients import get_client
from .exceptions import InvalidCredentialsException
from .helpers import Authorization, Credentials, Item, OperationStatus, object_to_xml
from .serializers import serialize_gaa, serialize_merchant, serialize_operation

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
            credentials = TodoPagoConnector.get_credentials(username, password)
            if None in asdict(credentials).values():
                raise InvalidCredentialsException()

        self.token = token or credentials.token
        self.merchant = merchant or credentials.merchant

    @staticmethod
    def get_credentials(username: str, password: str) -> Credentials:
        body = json.dumps({"USUARIO": username, "CLAVE": password})
        res = requests.post(
            API + "/Credentials",
            body,
            headers={"Content-Type": "application/json"},
        )
        data = res.json().get("Credentials")
        return Credentials(
            merchant=data.get("merchantId", None), token=data.get("APIKey", None)
        )

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
        req_body = serialize_merchant(
            self.token, self.merchant, self.success_url, self.failure_url
        )
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
        req_body = serialize_gaa(self.token, self.merchant, request_key, answer_key)
        res = client.service.GetAuthorizeAnswer(**req_body)
        return OperationStatus(res.StatusCode, res.StatusMessage, res.AuthorizationKey)
