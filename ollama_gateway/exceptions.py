class GatewayException(Exception):
    pass


class AuthenticationError(GatewayException):
    pass


class OllamaConnectionError(GatewayException):
    pass


class OllamaResponseError(GatewayException):
    pass


class ModelNotFoundError(GatewayException):
    pass


class GenerationError(GatewayException):
    pass

