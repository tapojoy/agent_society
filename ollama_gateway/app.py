from fastapi import FastAPI

from logger import logger
from routes import router
from config import API_KEY

app = FastAPI()


@app.on_event("startup")
async def startup():

    logger.info("Gateway starting")
    logger.info("Configuration validated successfully")


@app.on_event("shutdown")
async def shutdown():

    logger.info("Gateway stopping")


app.include_router(router)
