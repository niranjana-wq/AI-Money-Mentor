import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from core.calculator import calculate_tax
from core.prompts import build_tax_prompt
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


class TaxRequest(BaseModel):
    gross_annual_salary: float = Field(..., gt=0)
    age: int = Field(..., ge=18, le=80)
    city_type: str = Field(default="metro", description="metro/non-metro")
    hra_received: float = Field(default=0, ge=0)
    rent_paid: float = Field(default=0, ge=0)
    other_80c: float = Field(default=0, ge=0, description="PPF, ELSS, LIC etc")
    nps_80ccd: float = Field(default=0, ge=0, description="NPS contribution u/s 80CCD(1B)")
    medical_insurance_80d: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0, description="Section 24b")
    other_deductions: float = Field(default=0, ge=0)
    risk_profile: str = Field(default="moderate")


@app.post("/api/tax")
async def tax_wizard(req: TaxRequest):
    try:
        calculated = calculate_tax(
            gross_salary=req.gross_annual_salary,
            hra_received=req.hra_received,
            rent_paid=req.rent_paid,
            city_type=req.city_type,
            other_80c=req.other_80c,
            nps_80ccd=req.nps_80ccd,
            medical_insurance_80d=req.medical_insurance_80d,
            home_loan_interest=req.home_loan_interest,
            other_deductions=req.other_deductions,
        )

        profile = {
            "age": req.age,
            "gross_annual_salary": req.gross_annual_salary,
            "city_type": req.city_type,
            "risk_profile": req.risk_profile,
            "hra_received": req.hra_received,
            "rent_paid": req.rent_paid,
            "current_deductions": {
                "80c": req.other_80c,
                "nps": req.nps_80ccd,
                "80d": req.medical_insurance_80d,
                "home_loan": req.home_loan_interest,
            },
        }

        prompt = build_tax_prompt(profile=profile, calculated=calculated)
        ai_result = call_gemini(prompt)

        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI service error: {ai_result['error']}")

        validation = validate_ai_response("tax", ai_result["data"])
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