import time
import traceback

import requests

from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from llm.base import LLMProvider

from llm.exceptions import (
    LLMTimeoutError,
    LLMConnectionError,
    LLMResponseError
)

from logger import log_operation

def retry_log(retry_state):
    print(f"Retry attempt: {retry_state.attempt_number}")
    exception = retry_state.outcome.exception()
    log_operation(
        "llm_retry",
        "WARNING",
        {
            "attempt": retry_state.attempt_number,
            "error": str(exception)
        }
    )


class OllamaProvider(LLMProvider):

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=retry_log,
        reraise=True
    )
    def generate(self, model, prompt):

        try:
            
            log_operation(
                "llm_request_started", 
                "INFO", 
                {"model": model}
            )
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/generate",
                headers={"X-API-Key": self.api_key},
                json={"model": model, "prompt": prompt},
                timeout=(5, 30)
            )

            response.raise_for_status()

            latency_ms = int((time.time() - start_time) * 1000)

            log_operation(
                "llm_request_completed",
                "INFO",
                {"model": model, "latency_ms": latency_ms}
            )

            data = response.json()

            return {
                "request_id": data["request_id"],
                "content": data["content"],
                "model": data["model"],
                "client_latency_ms": latency_ms,
                "server_latency_ms": data["latency_ms"],
                "prompt_tokens": data.get("prompt_tokens"),
                "completion_tokens": data.get("completion_tokens")
            }

        except requests.Timeout:
            log_operation(
                "llm_timeout",
                "ERROR",
                {"model": model}
            )
            raise LLMTimeoutError(f"Timeout while calling {model}")

        except requests.ConnectionError:
            log_operation(
                "llm_connection_error",
                "ERROR",
                {"model": model}
            )
            raise LLMConnectionError(f"Connection failed to {model}")

        except Exception as e:
            log_operation(
                "llm_unknown_error",
                "ERROR",
                {
                    "model": model, 
                    "error": str(e),
                    "exception_name": type(e).__name__,
                    "exception_module": type(e).__module__,
                    "traceback": traceback.format_exc()
                }
            )
            raise LLMResponseError(str(e))
            
