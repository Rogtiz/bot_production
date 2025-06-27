from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging

from app.gwent.router import router as gwent_router
from app.bot.router import router as bot_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # твой фронт
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gwent_router, prefix="/gwent", tags=["Gwent"])
app.include_router(bot_router, prefix="/bot", tags=["Bot"])

@app.get("/")
def read_root():
    return {"Info": "No info for now"}
