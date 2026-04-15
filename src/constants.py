from aiohttp.client_exceptions import (
    ClientConnectorError,
    ClientOSError,
    ConnectionTimeoutError,
    ClientConnectionResetError,
    ServerDisconnectedError,
    ClientHttpProxyError,
)

NETWORK_EXCEPTIONS = (
    ClientConnectorError,
    ClientConnectionResetError,
    ConnectionTimeoutError,
    ClientOSError,
    ServerDisconnectedError,
    ClientHttpProxyError,
)
MAX_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)
