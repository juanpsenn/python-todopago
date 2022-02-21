import pytest

from python_todopago import helpers


def get_fieldname():
    string = helpers.get_fieldname("ARS")
    numeric_a = helpers.get_fieldname("32")
    numeric_b = helpers.get_fieldname(32)

    assert string == "alphabetic_code"
    assert numeric_a == "numeric_code"
    assert numeric_b == "numeric_code"


def test_get_currency_by_alphabetic_code():
    currency = helpers.get_currency("ARS")
    assert currency.alpha == "ARS"


def test_get_currency_by_numeric_code():
    currency_a = helpers.get_currency(32)
    currency_b = helpers.get_currency("32")
    assert currency_a.alpha == currency_b.alpha == "ARS"


def test_get_currency_with_invalidcode():
    # Test with invalid code
    with pytest.raises(ValueError):
        _ = helpers.get_currency("AAA")

    # Test with invalid code type
    with pytest.raises(TypeError):
        _ = helpers.get_currency(32.5)
