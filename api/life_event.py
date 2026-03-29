import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from core.calculator import calculate_fire, calculate_emergency_fund
from core.prompts import build_life_event_prompt
from core.ai_client import call_gemini
from core.validator import validate_ai_response, sanitize_response

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LifeEventRequest(BaseModel):
    age: int = Field(..., ge=18, le=80)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    monthly_savings: float = Field(..., ge=0)
    existing_investments: float = Field(default=0, ge=0)
    existing_sip: float = Field(default=0, ge=0)
    emergency_fund: float = Field(default=0, ge=0)
    total_debt_emi: float = Field(default=0, ge=0)
    risk_profile: str = Field(default="moderate")
    event_type: str = Field(..., description="bonus/marriage/baby/inheritance/job_change")
    event_amount: float = Field(default=0, ge=0, description="Amount involved e.g. bonus amount")
    event_details: str = Field(default="", description="Any additional context")


@app.post("/api/life-event")
async def life_event_advisor(req: LifeEventRequest):
    try:
        fire_calc = calculate_fire(
            age=req.age,
            monthly_income=req.monthly_income,
            monthly_expenses=req.monthly_expenses,
            monthly_savings=req.monthly_savings,
            existing_investments=req.existing_investments,
            existing_sip=req.existing_sip,
        )

        ef_calc = calculate_emergency_fund(
            monthly_expenses=req.monthly_expenses,
            current_emergency_fund=req.emergency_fund,
        )

        profile = {
            "age": req.age,
            "monthly_income": req.monthly_income,
            "monthly_expenses": req.monthly_expenses,
            "existing_investments": req.existing_investments,
            "emergency_fund": req.emergency_fund,
            "total_debt_emi": req.total_debt_emi,
            "risk_profile": req.risk_profile,
        }

        event = {
            "type": req.event_type,
            "amount": req.event_amount,
            "details": req.event_details,
        }

        calculated = {
            "fire": fire_calc,
            "emergency_fund": ef_calc,
        }

        prompt = build_life_event_prompt(
            profile=profile,
            event=event,
            calculated=calculated,
        )
        ai_result = call_gemini(prompt)

        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI service error: {ai_result['error']}")

        validation = validate_ai_response("life_event", ai_result["data"])
        clean_data = sanitize_response(validation["data"])

        return {
            "success": True,
            "calculated": calculated,
            "ai_analysis": clean_data,
            "validation_warnings": validation["errors"] if not validation["valid"] else [],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))