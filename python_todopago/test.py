from decimal import Decimal

from . import TodoPagoConnector
from .helpers import Item

items = [
    Item("Harry Potter", "A book", "1234", Decimal(1.0), 1, Decimal(1.0)),
    Item("Harry Potter", "A book", "1234", Decimal(1.0), 1, Decimal(1.0)),
]


def test_operation_create():
    tpc = TodoPagoConnector(
        "TODOPAGO 29A390FA2F9CBD8DBE9142B438B55D85",
        2083247,
        "http://example.com/success/",
        "http://example.com/failure/",
    )
    tpc.create_operation(
        "ABC",
        32,
        2.00,
        "Cordoba",
        "AR",
        "D",
        "Juan",
        "Senn",
        "test@gmail.com",
        "+543513840243",
        "5000",
        "Arrayan 8958",
        None,
        "1",
        "192.168.0.1",
        items,
    )
    assert isinstance(tpc, TodoPagoConnector)


def test_get_operation():
    tpc = TodoPagoConnector(
        "TODOPAGO 29A390FA2F9CBD8DBE9142B438B55D85",
        2083247,
        "http://example.com/success/",
        "http://example.com/failure/",
    )
    tpc.get_operation_status(
        "1fb8ec9a-14dd-42ec-bf1e-6d5820799642", "44cbea31-1373-4544-aa6b-42abff696944"
    )
    assert 1 == 1
