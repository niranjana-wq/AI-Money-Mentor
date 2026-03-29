from typing import Any


def compute_health_score(
    monthly_income: float,
    monthly_expenses: float,
    monthly_savings: float,
    emergency_fund: float,
    existing_investments: float,
    existing_sip: float,
    total_debt_emi: float,
    life_insurance_cover: float,
    health_insurance_cover: float,
    tax_saving_investments: float,
    age: int,
    gross_annual_salary: float,
) -> dict[str, Any]:

    # 1. Emergency fund score
    months_covered = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
    ef_score = min(100, int((months_covered / 6) * 100))
    ef_status = "on_track" if ef_score >= 80 else "needs_attention" if ef_score >= 40 else "critical"

    # 2. Insurance score
    recommended_life = monthly_income * 12 * 10
    life_score = min(100, int((life_insurance_cover / recommended_life) * 100)) if recommended_life > 0 else 0
    health_score_val = 100 if health_insurance_cover >= 500000 else int((health_insurance_cover / 500000) * 100)
    insurance_score = int((life_score + health_score_val) / 2)
    insurance_status = "on_track" if insurance_score >= 80 else "needs_attention" if insurance_score >= 40 else "critical"

    # 3. Investment diversification score
    savings_rate = monthly_savings / monthly_income if monthly_income > 0 else 0
    sip_rate = existing_sip / monthly_income if monthly_income > 0 else 0
    inv_score = min(100, int(savings_rate * 200) + min(50, int(sip_rate * 300)))
    inv_status = "on_track" if inv_score >= 70 else "needs_attention" if inv_score >= 40 else "critical"

    # 4. Debt health score
    foir = total_debt_emi / monthly_income if monthly_income > 0 else 0
    if foir <= 0.30:
        debt_score = 100
    elif foir <= 0.40:
        debt_score = 80
    elif foir <= 0.50:
        debt_score = 60
    elif foir <= 0.60:
        debt_score = 40
    else:
        debt_score = 20
    debt_status = "on_track" if debt_score >= 80 else "needs_attention" if debt_score >= 50 else "critical"

    # 5. Tax efficiency score
    max_80c = 150000
    tax_utilisation = min(1.0, tax_saving_investments / max_80c) if max_80c > 0 else 0
    tax_score = int(tax_utilisation * 100)
    tax_status = "on_track" if tax_score >= 80 else "needs_attention" if tax_score >= 40 else "critical"

    # 6. Retirement readiness score
    recommended_corpus_proxy = monthly_expenses * 12 * 25
    current_corpus = existing_investments
    years_to_60 = max(1, 60 - age)
    fv_investments = current_corpus * (1.11 ** years_to_60)
    retirement_score = min(100, int((fv_investments / recommended_corpus_proxy) * 100))
    retirement_status = "on_track" if retirement_score >= 70 else "needs_attention" if retirement_score >= 40 else "critical"

    # Overall weighted score
    weights = {
        "emergency_fund": 0.20,
        "insurance": 0.20,
        "investments": 0.20,
        "debt_health": 0.15,
        "tax_efficiency": 0.10,
        "retirement_readiness": 0.15,
    }
    overall = int(
        ef_score * weights["emergency_fund"]
        + insurance_score * weights["insurance"]
        + inv_score * weights["investments"]
        + debt_score * weights["debt_health"]
        + tax_score * weights["tax_efficiency"]
        + retirement_score * weights["retirement_readiness"]
    )

    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F"
    grade_label = {"A": "Excellent", "B": "Good", "C": "Average", "D": "Poor", "F": "Critical"}[grade]

    return {
        "overall_score": overall,
        "grade": grade,
        "grade_label": grade_label,
        "dimensions": {
            "emergency_fund": {"score": ef_score, "status": ef_status, "months_covered": round(months_covered, 1)},
            "insurance": {"score": insurance_score, "status": insurance_status, "life_cover": round(life_insurance_cover), "health_cover": round(health_insurance_cover)},
            "investments": {"score": inv_score, "status": inv_status, "savings_rate": round(savings_rate, 4)},
            "debt_health": {"score": debt_score, "status": debt_status, "foir": round(foir, 4)},
            "tax_efficiency": {"score": tax_score, "status": tax_status, "utilisation": round(tax_utilisation, 4)},
            "retirement_readiness": {"score": retirement_score, "status": retirement_status, "fv_investments": round(fv_investments)},
        },
    }