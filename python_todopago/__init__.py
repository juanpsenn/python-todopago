import json
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import requests

from .clients import get_client
from .helpers import Item, get_currency, object_to_xml

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
    ):
        client = get_client(self.token)
        req_body = self._parse_merchant_info()
        operation = {
            "MERCHANT": self.merchant,
            "OPERATIONID": operation_id,
            "CURRENCYCODE": str(currency).zfill(3),
            "AMOUNT": "%.2f" % (amount),
            "TIMEOUT": "300000",
            "CSBTCITY": city,
            "CSSTCITY": city,
            "CSBTCOUNTRY": country_code,
            "CSSTCOUNTRY": country_code,
            "CSBTEMAIL": billing_email,
            "CSSTEMAIL": billing_email,
            "CSBTFIRSTNAME": billing_first_name,
            "CSSTFIRSTNAME": billing_first_name,
            "CSBTLASTNAME": billing_last_name,
            "CSSTLASTNAME": billing_last_name,
            "CSBTPHONENUMBER": billing_phone,
            "CSSTPHONENUMBER": billing_phone,
            "CSBTPOSTALCODE": billing_postcode,
            "CSSTPOSTALCODE": billing_postcode,
            "CSBTSTATE": state_code,
            "CSSTSTATE": state_code,
            "CSBTSTREET1": billing_address_1,
            "CSSTSTREET1": billing_address_1,
            "CSBTSTREET2": billing_address_2,
            "CSSTSTREET2": billing_address_2,
            "CSBTCUSTOMERID": str(customer_id),
            "CSBTIPADDRESS": customer_ip_address,
            "CSPTCURRENCY": get_currency(currency),
            "CSPTGRANDTOTALAMOUNT": "%.2f" % (amount),
            "CSITPRODUCTCODE": str("default#" * len(items))[:-1],
            "CSITPRODUCTDESCRIPTION": "#".join([i.description for i in items]),
            "CSITPRODUCTNAME": "#".join([i.name for i in items]),
            "CSITPRODUCTSKU": "#".join([i.sku for i in items]),
            "CSITTOTALAMOUNT": "#".join(["%.2f" % (i.amount) for i in items]),
            "CSITQUANTITY": "#".join([str(i.quantity) for i in items]),
            "CSITUNITPRICE": "#".join(["%.2f" % (i.unit_price) for i in items]),
        }
        req_body.update({"Payload": object_to_xml(operation, "Request")})
        res = client.service.SendAuthorizeRequest(**req_body)
        return res

    def get_operation_status(self, request_key: str, answer_key: str):
        client = get_client(self.token)
        req_body = {
            "Security": self.token[-32:],
            "Merchant": self.merchant,
            "RequestKey": request_key,
            "AnswerKey": answer_key,
        }
        res = client.service.GetAuthorizeAnswer(**req_body)
        return res

    def _parse_merchant_info(self) -> Dict:
        return {
            "Security": self.token[-32:],
            "Merchant": self.merchant,
            "URL_OK": self.success_url,
            "URL_ERROR": self.failure_url,
        }
