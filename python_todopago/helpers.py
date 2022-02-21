import json
from dataclasses import dataclass
from decimal import Decimal
from os import path
from typing import Optional, Union


@dataclass(frozen=True)
class Item:
    """A dataclass holding an operation item information"""

    description: str
    name: str
    sku: str
    amount: Decimal
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class Authorization:
    """A datacalss holding response details from SendAuthorizeRequest service"""

    status_code: int
    status_message: str
    form_url: Optional[str]
    request_key: Optional[str]
    public_request_key: Optional[str]


@dataclass(frozen=True)
class OperationStatus:
    """A datacalss holding response details from GetAuthorizedAnswer service"""

    status_code: int
    status_message: str
    authorization_key: str


@dataclass(frozen=True)
class Credentials:
    """A datacalss holding response details from /api/Credentials"""

    merchant: int
    token: str


def get_currency(code: Union[int, str]) -> Optional[str]:
    """
    Get alphabetic currency code by numeric code, if there is no match returns None.
    Also, if the code is not numeric verifies if it is a valid currency code.
    This codes are based on ISO 4217 standard.
    """
    field = get_fieldname(code)

    basedir = path.dirname(__file__)
    with open(basedir + "/iso4217.json") as data:
        currencies = json.load(data)
        return next(
            (c["alphabetic_code"] for c in currencies if str(c[field]) == str(code)),
            None,
        )


def get_fieldname(code: Union[int, str]) -> str:
    """
    Get the field name based on the field name.
    """
    if isinstance(code, int):
        return "numeric_code"
    elif isinstance(code, str):
        return "alphabetic_code" if code.isalpha() else "numeric_code"
    raise TypeError(f"Invalid type for code: {type(code)}, expected int or str.")


def object_to_xml(data: Union[dict, bool], root="object"):
    xml = f"<{root}>"
    if isinstance(data, dict):
        for key, value in data.items():
            xml += object_to_xml(value, key)

    elif isinstance(data, (list, tuple, set)):
        for item in data:
            xml += object_to_xml(item, "item")

    else:
        xml += str(data)

    xml += f"</{root}>"
    return xml
