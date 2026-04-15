from playwright.async_api import BrowserContext

from namespaces import ResponseData


class RequestPayload:
    def __init__(self, **kwargs) -> None:
        self.query: dict = kwargs.get("query", {})
        self.response: ResponseData | None = kwargs.get("response")
        self.browser: BrowserContext = kwargs.get("browser")

    def HasEmptyValues(self, keys: tuple) -> bool:
        return any(not getattr(self, key) for key in keys)
