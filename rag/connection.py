import weaviate

from weaviate.auth import AuthApiKey

from config import (
    WEAVIATE_URL,
    WEAVIATE_HTTP_PORT,
    WEAVIATE_GRPC_PORT,
    WEAVIATE_API_KEY
)

_client = None


def get_client():
    global _client

    if _client is not None and _client.is_connected():
        return _client

    host = (
        WEAVIATE_URL
        .replace("http://", "")
        .replace("https://", "")
        .split(":")[0]
    )

    secure = False #WEAVIATE_URL.startswith("https://")

    _client = weaviate.connect_to_custom(
        http_host=host,
        http_port=WEAVIATE_HTTP_PORT,
        http_secure=secure,
        grpc_host=host,
        grpc_port=WEAVIATE_GRPC_PORT,
        grpc_secure=secure,
        auth_credentials=AuthApiKey(
            WEAVIATE_API_KEY
        )
    )

    return _client


def close():

    global _client

    if (
        _client is not None
        and _client.is_connected()
    ):
        _client.close()

    _client = None