import time
import uuid

# import traceback

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException

import ollama

from config import API_KEY
from models import GenerateRequest, EmbedRequest
from logger import logger

router = APIRouter()

@router.get("/health")
def health():
    try:
        models = ollama.list()
        return {
            "status": "healthy",
            "ollama": "reachable",
            "models": len(models["models"])
        }
    except:
        raise HTTPException(status_code=503, detail="Ollama unavailable")

@router.get("/version")
def version():
    try:
        return {
            "service": "ollama_service",
            "version": "0.1.0"
        }
    except:
        raise HTTPException(status_code=503, detail="Ollama unavailable")

@router.post("/generate")
def generate(request: GenerateRequest, x_api_key: str = Header()):

    logger.info(f"Request received for model={request.model}")

    if x_api_key != API_KEY:
        logger.warning("Invalid API key received")
        raise HTTPException(status_code=401, detail="Invalid API key")

    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        response = ollama.chat(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}]
        )

    except Exception as e:
        logger.exception("An error occurred")
        # logger.error("Traceback:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

    latency_ms = round(((time.time() - start_time) * 1000), 2)
    logger.info(
        f"Completed request_id={request_id} "
        f"model={request.model} "
        f"latency={latency_ms}ms"
    )
    return {
        "request_id": request_id,
        "content": response["message"]["content"],
        "model": request.model,
        "latency_ms": latency_ms,
        "prompt_tokens": None,
        "completion_tokens": None
    }

@router.post("/embed")
def embed(request: EmbedRequest, x_api_key: str = Header()):

    logger.info(f"Embedding request received for model={request.model}")

    if x_api_key != API_KEY:
        logger.warning("Invalid API key received")
        raise HTTPException(status_code=401, detail="Invalid API key")

    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        response = ollama.embed(
            model=request.model,
            input=request.text
        )

    except Exception as e:
        logger.exception("An error occurred")

        raise HTTPException(status_code=500, detail=str(e))

    latency_ms = round(((time.time() - start_time) * 1000), 2)
    logger.info(
        f"Completed request_id={request_id} "
        f"model={request.model} "
        f"latency={latency_ms}ms"
    )
    return {
        "request_id": request_id,
        "embedding": response["embeddings"][0],
        "model": request.model,
        "latency_ms": latency_ms
    }
