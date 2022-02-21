import pytest

from python_todopago import helpers


def get_fieldname():
    string = helpers.get_fieldname("ARS")
    numeric_a = helpers.get_fieldname("32")
    numeric_b = helpers.get_fieldname(32)

    assert string == "alphabetic_code"
    assert numeric_a == "numeric_code"
    assert numeric_b == "numeric_code"


def test_get_currency_with_alphacode():
    code = helpers.get_currency("ARS")
    assert code == "ARS"


def test_get_currency_with_numericcode():
    code_a = helpers.get_currency(32)
    code_b = helpers.get_currency("32")
    assert code_a == code_b == "ARS"


def test_get_currency_with_invalidcode():
    # Test with invalid code
    code = helpers.get_currency("AAA")
    assert code is None

    # Test with invalid code type
    with pytest.raises(TypeError):
        code = helpers.get_currency(32.5)
