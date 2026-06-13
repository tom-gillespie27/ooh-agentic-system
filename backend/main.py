from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from data import BILLBOARDS, CREATIVES
from weather import get_weather
from agent import choose_creative

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/billboards")
def list_billboards():
    return BILLBOARDS

@app.get("/creatives")
def list_creatives():
    return CREATIVES

@app.get("/decision/{billboard_id}")
def get_decision(billboard_id: str):
    billboard = next((b for b in BILLBOARDS if b["id"] == billboard_id), None)
    if not billboard:
        return {"error": "Billboard not found"}

    weather = get_weather(billboard["lat"], billboard["lon"])
    decision = choose_creative(billboard, weather)

    selected = next((c for c in CREATIVES if c["id"] == decision["selected_creative_id"]), None)

    return {
        "billboard": billboard,
        "weather": weather,
        "decision": decision,
        "creative": selected
    }