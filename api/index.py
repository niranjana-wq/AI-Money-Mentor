import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from core.calculator import calculate_fire, calculate_emergency_fund, calculate_tax
from core.scorer import compute_health_score
from core.prompts import (
    build_fire_prompt, build_health_score_prompt,
    build_tax_prompt, build_life_event_prompt,
    build_mf_xray_prompt, build_couples_prompt
)
from core.ai_client import call_gemini
from core.validator import validate_ai_response, sanitize_response
from core.parser import parse_cams_text

app = FastAPI(
    title="AI Money Mentor API",
    description="AI-powered personal finance mentor for India",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-money-mentor-mauve.vercel.app",
        "https://ai-money-mentor.vercel.app",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ──

class FIRERequest(BaseModel):
    age: int = Field(..., ge=18, le=70)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    monthly_savings: float = Field(default=0, ge=0)
    existing_investments: float = Field(default=0, ge=0)
    existing_sip: float = Field(default=0, ge=0)
    emergency_fund: float = Field(default=0, ge=0)
    total_debt_emi: float = Field(default=0, ge=0)
    life_insurance_cover: float = Field(default=0, ge=0)
    health_insurance_cover: float = Field(default=0, ge=0)
    tax_saving_investments: float = Field(default=0, ge=0)
    gross_annual_salary: float = Field(default=0, ge=0)
    goals: list[str] = Field(default=[])
    risk_profile: str = Field(default="moderate")
    city: str = Field(default="metro")


class ScoreRequest(BaseModel):
    age: int = Field(..., ge=18, le=80)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    monthly_savings: float = Field(default=0, ge=0)
    emergency_fund: float = Field(default=0, ge=0)
    existing_investments: float = Field(default=0, ge=0)
    existing_sip: float = Field(default=0, ge=0)
    total_debt_emi: float = Field(default=0, ge=0)
    life_insurance_cover: float = Field(default=0, ge=0)
    health_insurance_cover: float = Field(default=0, ge=0)
    tax_saving_investments: float = Field(default=0, ge=0)
    gross_annual_salary: float = Field(default=0, ge=0)


class TaxRequest(BaseModel):
    gross_annual_salary: float = Field(..., gt=0)
    age: int = Field(..., ge=18, le=80)
    city_type: str = Field(default="metro")
    hra_received: float = Field(default=0, ge=0)
    rent_paid: float = Field(default=0, ge=0)
    other_80c: float = Field(default=0, ge=0)
    nps_80ccd: float = Field(default=0, ge=0)
    medical_insurance_80d: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0)
    other_deductions: float = Field(default=0, ge=0)
    risk_profile: str = Field(default="moderate")


class LifeEventRequest(BaseModel):
    age: int = Field(..., ge=18, le=80)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    monthly_savings: float = Field(default=0, ge=0)
    existing_investments: float = Field(default=0, ge=0)
    existing_sip: float = Field(default=0, ge=0)
    emergency_fund: float = Field(default=0, ge=0)
    total_debt_emi: float = Field(default=0, ge=0)
    risk_profile: str = Field(default="moderate")
    event_type: str = Field(...,)
    event_amount: float = Field(default=0, ge=0)
    event_details: str = Field(default="")


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
    combined_goals: list[str] = Field(default=[])
    risk_profile: str = Field(default="moderate")
    years_married: int = Field(default=0, ge=0)


# ── Routes ──

@app.get("/")
def root():
    return {
        "product": "AI Money Mentor",
        "version": "1.0.0",
        "status": "live",
        "endpoints": [
            "/api/fire", "/api/score", "/api/tax",
            "/api/life-event", "/api/mf-xray", "/api/couples"
        ],
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


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
        profile = req.model_dump()
        calculated = {"fire": fire_calc, "emergency_fund": ef_calc, "health_score": health}
        prompt = build_fire_prompt(profile=profile, calculated=calculated)
        ai_result = call_gemini(prompt)
        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI error: {ai_result['error']}")
        validation = validate_ai_response("fire", ai_result["data"])
        return {"success": True, "calculated": calculated, "ai_analysis": sanitize_response(validation["data"])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            raise HTTPException(status_code=502, detail=f"AI error: {ai_result['error']}")
        validation = validate_ai_response("health_score", ai_result["data"])
        return {"success": True, "calculated": calculated, "ai_analysis": sanitize_response(validation["data"])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        profile = req.model_dump()
        prompt = build_tax_prompt(profile=profile, calculated=calculated)
        ai_result = call_gemini(prompt)
        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI error: {ai_result['error']}")
        validation = validate_ai_response("tax", ai_result["data"])
        return {"success": True, "calculated": calculated, "ai_analysis": sanitize_response(validation["data"])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        profile = req.model_dump()
        event = {"type": req.event_type, "amount": req.event_amount, "details": req.event_details}
        calculated = {"fire": fire_calc, "emergency_fund": ef_calc}
        prompt = build_life_event_prompt(profile=profile, event=event, calculated=calculated)
        ai_result = call_gemini(prompt)
        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI error: {ai_result['error']}")
        validation = validate_ai_response("life_event", ai_result["data"])
        return {"success": True, "calculated": calculated, "ai_analysis": sanitize_response(validation["data"])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mf-xray")
async def mf_xray(
    file: UploadFile = File(...),
    age: int = Form(...),
    risk_profile: str = Form(default="moderate"),
):
    try:
        content = await file.read()
        try:
            raw_text = content.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = content.decode("latin-1")
        parsed = parse_cams_text(raw_text)
        if not parsed["parsed_successfully"]:
            raise HTTPException(status_code=422, detail="Could not parse statement.")
        avg_expense_ratio = sum(
            f.get("expense_ratio", 0.015) for f in parsed["funds"]
        ) / max(len(parsed["funds"]), 1)
        calculated = {
            "total_invested": parsed["total_invested"],
            "current_value": parsed["current_value"],
            "fund_count": parsed["fund_count"],
            "avg_expense_ratio": round(avg_expense_ratio, 4),
            "annual_expense_drag": round(parsed["current_value"] * avg_expense_ratio),
        }
        prompt = build_mf_xray_prompt(portfolio=parsed, calculated=calculated)
        ai_result = call_gemini(prompt)
        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI error: {ai_result['error']}")
        validation = validate_ai_response("mf_xray", ai_result["data"])
        return {"success": True, "parsed": parsed, "calculated": calculated, "ai_analysis": sanitize_response(validation["data"])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/couples")
async def couples_planner(req: CouplesRequest):
    try:
        p1, p2 = req.partner1, req.partner2
        fire1 = calculate_fire(
            age=p1.age, monthly_income=p1.monthly_income,
            monthly_expenses=p1.monthly_expenses,
            monthly_savings=p1.monthly_income - p1.monthly_expenses,
            existing_investments=p1.existing_investments, existing_sip=p1.existing_sip,
        )
        fire2 = calculate_fire(
            age=p2.age, monthly_income=p2.monthly_income,
            monthly_expenses=p2.monthly_expenses,
            monthly_savings=p2.monthly_income - p2.monthly_expenses,
            existing_investments=p2.existing_investments, existing_sip=p2.existing_sip,
        )
        tax1 = calculate_tax(gross_salary=p1.gross_annual_salary, hra_received=p1.hra_received, rent_paid=p1.rent_paid, city_type=p1.city_type, nps_80ccd=p1.nps_contribution)
        tax2 = calculate_tax(gross_salary=p2.gross_annual_salary, hra_received=p2.hra_received, rent_paid=p2.rent_paid, city_type=p2.city_type, nps_80ccd=p2.nps_contribution)
        combined_income = p1.monthly_income + p2.monthly_income
        combined_expenses = p1.monthly_expenses + p2.monthly_expenses
        calculated = {
            "combined_income": round(combined_income),
            "combined_expenses": round(combined_expenses),
            "combined_savings_rate": round((combined_income - combined_expenses) / combined_income, 4) if combined_income > 0 else 0,
            "combined_net_worth": round(p1.existing_investments + p2.existing_investments),
            "partner1_fire": fire1, "partner2_fire": fire2,
            "partner1_tax": tax1, "partner2_tax": tax2,
        }
        prompt = build_couples_prompt(partner1=p1.model_dump(), partner2=p2.model_dump(), calculated=calculated)
        ai_result = call_gemini(prompt)
        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI error: {ai_result['error']}")
        return {"success": True, "calculated": calculated, "ai_analysis": sanitize_response(ai_result["data"])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))