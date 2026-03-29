import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from core.scorer import compute_health_score
from core.prompts import build_health_score_prompt
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


class ScoreRequest(BaseModel):
    age: int = Field(..., ge=18, le=80)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    monthly_savings: float = Field(..., ge=0)
    emergency_fund: float = Field(default=0, ge=0)
    existing_investments: float = Field(default=0, ge=0)
    existing_sip: float = Field(default=0, ge=0)
    total_debt_emi: float = Field(default=0, ge=0)
    life_insurance_cover: float = Field(default=0, ge=0)
    health_insurance_cover: float = Field(default=0, ge=0)
    tax_saving_investments: float = Field(default=0, ge=0)
    gross_annual_salary: float = Field(default=0, ge=0)


@app.post("/api/score")
async def money_health_score(req: ScoreRequest):
    try:
        calculated = compute_health_score(
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

        profile = req.model_dump()
        prompt = build_health_score_prompt(profile=profile, calculated=calculated)
        ai_result = call_gemini(prompt)

        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI service error: {ai_result['error']}")

        validation = validate_ai_response("health_score", ai_result["data"])
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