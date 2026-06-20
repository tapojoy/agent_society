class LLMError(Exception):
    pass


class LLMTimeoutError(LLMError):
    pass


class LLMConnectionError(LLMError):
    pass


class LLMResponseError(LLMError):
    pass