import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from core.calculator import calculate_fire, calculate_tax
from core.prompts import build_couples_prompt
from core.ai_client import call_gemini
from core.validator import sanitize_response

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PartnerProfile(BaseModel):
    name: str = Field(default="Partner")
    age: int = Field(..., ge=18, le=80)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    existing_investments: float = Field(default=0, ge=0)
    existing_sip: float = Field(default=0, ge=0)
    gross_annual_salary: float = Field(default=0, ge=0)
    hra_received: float = Field(default=0, ge=0)
    rent_paid: float = Field(default=0, ge=0)
    city_type: str = Field(default="metro")
    nps_contribution: float = Field(default=0, ge=0)
    life_insurance_cover: float = Field(default=0, ge=0)
    health_insurance_cover: float = Field(default=0, ge=0)


class CouplesRequest(BaseModel):
    partner1: PartnerProfile
    partner2: PartnerProfile
    combined_goals: list[str] = Field(default=[], description="e.g. house, child education, travel")
    risk_profile: str = Field(default="moderate")
    years_married: int = Field(default=0, ge=0)


@app.post("/api/couples")
async def couples_planner(req: CouplesRequest):
    try:
        p1 = req.partner1
        p2 = req.partner2

        fire1 = calculate_fire(
            age=p1.age,
            monthly_income=p1.monthly_income,
            monthly_expenses=p1.monthly_expenses,
            monthly_savings=p1.monthly_income - p1.monthly_expenses,
            existing_investments=p1.existing_investments,
            existing_sip=p1.existing_sip,
        )

        fire2 = calculate_fire(
            age=p2.age,
            monthly_income=p2.monthly_income,
            monthly_expenses=p2.monthly_expenses,
            monthly_savings=p2.monthly_income - p2.monthly_expenses,
            existing_investments=p2.existing_investments,
            existing_sip=p2.existing_sip,
        )

        tax1 = calculate_tax(
            gross_salary=p1.gross_annual_salary,
            hra_received=p1.hra_received,
            rent_paid=p1.rent_paid,
            city_type=p1.city_type,
            nps_80ccd=p1.nps_contribution,
        )

        tax2 = calculate_tax(
            gross_salary=p2.gross_annual_salary,
            hra_received=p2.hra_received,
            rent_paid=p2.rent_paid,
            city_type=p2.city_type,
            nps_80ccd=p2.nps_contribution,
        )

        combined_income = p1.monthly_income + p2.monthly_income
        combined_expenses = p1.monthly_expenses + p2.monthly_expenses
        combined_investments = p1.existing_investments + p2.existing_investments
        combined_savings_rate = (combined_income - combined_expenses) / combined_income if combined_income > 0 else 0

        calculated = {
            "combined_income": round(combined_income),
            "combined_expenses": round(combined_expenses),
            "combined_savings_rate": round(combined_savings_rate, 4),
            "combined_net_worth": round(combined_investments),
            "partner1_fire": fire1,
            "partner2_fire": fire2,
            "partner1_tax": tax1,
            "partner2_tax": tax2,
            "combined_tax_current": round(
                tax1["old_regime"]["tax_payable"] + tax2["old_regime"]["tax_payable"]
            ),
        }

        prompt = build_couples_prompt(
            partner1=p1.model_dump(),
            partner2=p2.model_dump(),
            calculated=calculated,
        )
        ai_result = call_gemini(prompt)

        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI service error: {ai_result['error']}")

        clean_data = sanitize_response(ai_result["data"])

        return {
            "success": True,
            "calculated": calculated,
            "ai_analysis": clean_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
