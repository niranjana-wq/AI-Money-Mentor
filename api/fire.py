import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from core.calculator import calculate_fire, calculate_emergency_fund
from core.scorer import compute_health_score
from core.prompts import build_fire_prompt
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


class FIRERequest(BaseModel):
    age: int = Field(..., ge=18, le=70, description="Current age")
    monthly_income: float = Field(..., gt=0, description="Monthly take-home income in ₹")
    monthly_expenses: float = Field(..., gt=0, description="Monthly expenses in ₹")
    monthly_savings: float = Field(..., ge=0, description="Monthly savings in ₹")
    existing_investments: float = Field(default=0, ge=0, description="Total existing investments in ₹")
    existing_sip: float = Field(default=0, ge=0, description="Current monthly SIP in ₹")
    emergency_fund: float = Field(default=0, ge=0, description="Current emergency fund in ₹")
    total_debt_emi: float = Field(default=0, ge=0, description="Total monthly EMIs in ₹")
    life_insurance_cover: float = Field(default=0, ge=0, description="Life insurance cover in ₹")
    health_insurance_cover: float = Field(default=0, ge=0, description="Health insurance cover in ₹")
    tax_saving_investments: float = Field(default=0, ge=0, description="Annual 80C investments in ₹")
    gross_annual_salary: float = Field(default=0, ge=0, description="Gross annual CTC in ₹")
    goals: list[str] = Field(default=[], description="Financial goals e.g. house, child education")
    risk_profile: str = Field(default="moderate", description="conservative/moderate/aggressive")
    city: str = Field(default="metro", description="metro/non-metro")


@app.post("/api/fire")
async def fire_planner(req: FIRERequest):
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

        health = compute_health_score(
            monthly_income=req.monthly_income,
            monthly_expenses=req.monthly_expenses,
            monthly_savings=req.monthly_savings,
            emergency_fund=req.emergency_fund,
            existing_investments=req.existing_investments,
            existing_sip=req.existing_sip,
            total_debt_emi=req.total_debt_emi,
            life_insurance_cover=req.life_insurance_cover,
            health_insurance_cover=req.health_insurance_cover,
            tax_saving_investments=req.tax_saving_investments,
            age=req.age,
            gross_annual_salary=req.gross_annual_salary,
        )

        profile = {
            "age": req.age,
            "monthly_income": req.monthly_income,
            "monthly_expenses": req.monthly_expenses,
            "monthly_savings": req.monthly_savings,
            "existing_investments": req.existing_investments,
            "existing_sip": req.existing_sip,
            "risk_profile": req.risk_profile,
            "goals": req.goals,
            "city": req.city,
            "life_insurance_cover": req.life_insurance_cover,
            "health_insurance_cover": req.health_insurance_cover,
            "total_debt_emi": req.total_debt_emi,
        }

        calculated = {
            "fire": fire_calc,
            "emergency_fund": ef_calc,
            "health_score": health,
        }

        prompt = build_fire_prompt(profile=profile, calculated=calculated)
        ai_result = call_gemini(prompt)

        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI service error: {ai_result['error']}")

        validation = validate_ai_response("fire", ai_result["data"])
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