import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

if os.getenv("RENDER") is None:
    load_dotenv()

app = FastAPI(
    title="AI Money Mentor API",
    description="AI-powered personal finance mentor for India",
    version="1.0.0",
)

origins = os.getenv("ALLOWED_ORIGINS", "*")

if origins == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [o.strip() for o in origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include all routers
from api.fire import app as fire_app
from api.score import app as score_app
from api.tax import app as tax_app
from api.life_event import app as life_event_app
from api.mf_xray import app as mf_xray_app
from api.couples import app as couples_app

# Mount each sub-app as a router
from fastapi.routing import APIRoute

def include_routes(source_app, target_app):
    for route in source_app.routes:
        if isinstance(route, APIRoute):
            target_app.add_api_route(
                path=route.path,
                endpoint=route.endpoint,
                methods=route.methods,
                tags=route.tags or [route.path.split("/")[2]],
            )

include_routes(fire_app, app)
include_routes(score_app, app)
include_routes(tax_app, app)
include_routes(life_event_app, app)
include_routes(mf_xray_app, app)
include_routes(couples_app, app)


@app.get("/")
def root():
    return {
        "product": "AI Money Mentor",
        "version": "1.0.0",
        "status": "live",
        "endpoints": [
            "/api/fire",
            "/api/score",
            "/api/tax",
            "/api/life-event",
            "/api/mf-xray",
            "/api/couples",
        ],
    }

@app.get("/api/health")
def health():
    return {"status": "ok"}