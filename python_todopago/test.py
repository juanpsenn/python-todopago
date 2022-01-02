from decimal import Decimal

import pytest
import requests_mock

from . import TodoPagoConnector
from .clients import ENDPOINTS
from .helpers import Item


@pytest.fixture
def items():
    return [
        Item("Harry Potter", "A book", "1234", Decimal(1.0), 1, Decimal(1.0)),
        Item("Harry Potter", "A book", "1234", Decimal(1.0), 1, Decimal(1.0)),
    ]


@pytest.fixture
def operation_info(items):
    return {
        "operation_id": "ABC",
        "currency": 32,
        "amount": 2.00,
        "city": "Cordoba",
        "country_code": "AR",
        "state_code": "D",
        "billing_first_name": "Juan",
        "billing_last_name": "Lopez",
        "billing_email": "test@gmail.com",
        "billing_phone": "+543513840243",
        "billing_postcode": "5000",
        "billing_address_1": "Arrayan 8958",
        "billing_address_2": None,
        "customer_id": "1",
        "customer_ip_address": "192.168.0.1",
        "items": items,
    }


def test_authorize_operation(operation_info):
    connector = TodoPagoConnector(
        "http://example.com/success/",
        "http://example.com/failure/",
        "PRISMA A793D307441615AF6AAAD7497A75DE59",
        2159,
        sandbox=True,
    )

    authorization_response = """
    <?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <api:SendAuthorizeRequestResponse xmlns:api="http://api.todopago.com.ar">
            <api:StatusCode>-1</api:StatusCode>
            <api:StatusMessage>Solicitud de Autorizacion Registrada</api:StatusMessage>
            <api:URL_Request>https://forms.todopago.com.ar/formulario/commands?command=formulario&amp;m=a6104bad3-1be7-4e8e-932e-e927100b2e86&amp;fr=1</api:URL_Request>
            <api:RequestKey>f5ad41bc-92ba-40ff-889d-8a23fe562a28</api:RequestKey>
            <api:PublicRequestKey>a6104bad3-1be7-4e8e-932e-e927100b2e86</api:PublicRequestKey>
        </api:SendAuthorizeRequestResponse>
    </soapenv:Body>
    </soapenv:Envelope>
    """.strip()

    with requests_mock.mock() as m:
        m.post(
            ENDPOINTS[True] + "Authorize",
            text=authorization_response,
        )
        authorization = connector.authorize_operation(**operation_info)
        assert authorization.status_code == -1


def test_get_operation_status():
    connector = TodoPagoConnector(
        "http://example.com/success/",
        "http://example.com/failure/",
        "PRISMA A793D307441615AF6AAAD7497A75DE59",
        2159,
        sandbox=True,
    )
    status_response = """
    <?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <api:GetAuthorizeAnswerResponse xmlns:api="http://api.todopago.com.ar">
            <api:StatusCode>-1</api:StatusCode>
            <api:StatusMessage>APROBADA</api:StatusMessage>
            <api:AuthorizationKey>817824df-8614-4ce8-a6c9-abdf884024ab</api:AuthorizationKey>
            <api:EncodingMethod>XML</api:EncodingMethod>
            <api:Payload>
                <Answer xmlns="http://api.todopago.com.ar">
                <DATETIME>2022-01-01T20:46:03 -0300</DATETIME>
                <CURRENCYNAME>Peso Argentino</CURRENCYNAME>
                <PAYMENTMETHODNAME>VISA DEBITO</PAYMENTMETHODNAME>
                <TICKETNUMBER>5770</TICKETNUMBER>
                <AUTHORIZATIONCODE>646962</AUTHORIZATIONCODE>
                <CARDNUMBERVISIBLE>4517XXXXXXXX6388</CARDNUMBERVISIBLE>
                <BARCODE />
                <OPERATIONID>ABC</OPERATIONID>
                <COUPONEXPDATE />
                <COUPONSECEXPDATE />
                <COUPONSUBSCRIBER />
                <BARCODETYPE />
                <ASSOCIATEDDOCUMENTATION />
                <INSTALLMENTPAYMENTS>1</INSTALLMENTPAYMENTS>
                <OPERATIONNUMBER>56827509</OPERATIONNUMBER>
                <CFT>0</CFT>
                <TEA>0</TEA>
                </Answer>
                <Request xmlns="http://api.todopago.com.ar">
                <MERCHANT>2033247</MERCHANT>
                <OPERATIONID>ABC</OPERATIONID>
                <AMOUNT>2.00</AMOUNT>
                <CURRENCYCODE>32</CURRENCYCODE>
                <AMOUNTBUYER>2.00</AMOUNTBUYER>
                <BANKID>18</BANKID>
                <PROMOTIONID />
                </Request>
            </api:Payload>
        </api:GetAuthorizeAnswerResponse>
    </soapenv:Body>
    </soapenv:Envelope>
    """.strip()

    with requests_mock.mock() as m:
        m.post(
            ENDPOINTS[True] + "Authorize",
            text=status_response,
        )
        status = connector.get_operation_status(
            "1fb7cc9a-14dd-42ec-bf1e-6d5820799642",
            "44caba31-1373-4544-aa6b-42abff696944",
        )
        assert status.status_code == -1
        assert status.status_message == "APROBADA"
        assert status.authorization_key == "817824df-8614-4ce8-a6c9-abdf884024ab"
