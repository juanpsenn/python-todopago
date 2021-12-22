from zeep import Client, Settings

wsdl = "python_todopago/wsdl/Authorize.wsdl"


def get_client(token: str) -> Client:
    settings = Settings(extra_http_headers={"Authorization": token})
    return Client(wsdl, settings=settings)
