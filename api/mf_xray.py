import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.parser import parse_cams_text
from core.calculator import calculate_xirr
from core.prompts import build_mf_xray_prompt
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


@app.post("/api/mf-xray")
async def mf_xray(
    file: UploadFile = File(..., description="CAMS or KFin PDF/text statement"),
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
            raise HTTPException(
                status_code=422,
                detail="Could not parse statement. Please upload a text-based CAMS or KFin statement.",
            )

        total_value = parsed["current_value"]
        avg_expense_ratio = sum(
            f.get("expense_ratio", 0.015) for f in parsed["funds"]
        ) / max(len(parsed["funds"]), 1)
        annual_drag = round(total_value * avg_expense_ratio)

        calculated = {
            "total_invested": parsed["total_invested"],
            "current_value": parsed["current_value"],
            "fund_count": parsed["fund_count"],
            "avg_expense_ratio": round(avg_expense_ratio, 4),
            "annual_expense_drag": annual_drag,
            "ten_year_drag": round(annual_drag * 10),
            "absolute_return": round(
                (parsed["current_value"] - parsed["total_invested"])
                / max(parsed["total_invested"], 1) * 100, 2
            ),
        }

        prompt = build_mf_xray_prompt(
            portfolio=parsed,
            calculated=calculated,
        )
        ai_result = call_gemini(prompt)

        if not ai_result["success"]:
            raise HTTPException(status_code=502, detail=f"AI service error: {ai_result['error']}")

        validation = validate_ai_response("mf_xray", ai_result["data"])
        clean_data = sanitize_response(validation["data"])

        return {
            "success": True,
            "parsed": parsed,
            "calculated": calculated,
            "ai_analysis": clean_data,
            "validation_warnings": validation["errors"] if not validation["valid"] else [],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))