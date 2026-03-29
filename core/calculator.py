import math
from typing import Any


def calculate_fire(
    age: int,
    monthly_income: float,
    monthly_expenses: float,
    monthly_savings: float,
    existing_investments: float,
    existing_sip: float,
    inflation_rate: float = 0.06,
    equity_return: float = 0.11,
    safe_withdrawal_rate: float = 0.04,
    retirement_age: int = 60,
) -> dict[str, Any]:

    monthly_expenses_today = monthly_expenses
    years_to_retirement = retirement_age - age
    monthly_return = equity_return / 12
    corpus_needed = (monthly_expenses_today * 12 * (1 + inflation_rate) ** years_to_retirement) / safe_withdrawal_rate

    if monthly_return > 0:
        fv_existing = existing_investments * (1 + equity_return) ** years_to_retirement
        months = years_to_retirement * 12
        fv_sip = existing_sip * (((1 + monthly_return) ** months - 1) / monthly_return) * (1 + monthly_return)
    else:
        fv_existing = existing_investments
        fv_sip = existing_sip * years_to_retirement * 12

    corpus_gap = max(0, corpus_needed - fv_existing - fv_sip)

    if monthly_return > 0 and corpus_gap > 0:
        months = years_to_retirement * 12
        additional_sip = corpus_gap * monthly_return / (((1 + monthly_return) ** months - 1) * (1 + monthly_return))
    else:
        additional_sip = 0

    total_sip_needed = existing_sip + additional_sip
    savings_rate = monthly_savings / monthly_income if monthly_income > 0 else 0
    target_savings_rate = total_sip_needed / monthly_income if monthly_income > 0 else 0

    fire_age = age
    accumulated = existing_investments
    monthly_sip_total = total_sip_needed
    for yr in range(1, 51):
        accumulated = accumulated * (1 + equity_return) + monthly_sip_total * 12
        annual_expenses_future = monthly_expenses_today * 12 * (1 + inflation_rate) ** yr
        corpus_at_this_age = annual_expenses_future / safe_withdrawal_rate
        if accumulated >= corpus_at_this_age:
            fire_age = age + yr
            break

    equity_pct = max(0.4, min(0.8, 1 - ((age - 20) / 100)))
    debt_pct = 1 - equity_pct - 0.05 - 0.05

    return {
        "corpus_needed": round(corpus_needed),
        "fv_existing_investments": round(fv_existing),
        "fv_current_sip": round(fv_sip),
        "corpus_gap": round(corpus_gap),
        "additional_sip_needed": round(additional_sip),
        "total_sip_needed": round(total_sip_needed),
        "existing_sip": round(existing_sip),
        "sip_gap": round(total_sip_needed - existing_sip),
        "savings_rate": round(savings_rate, 4),
        "target_savings_rate": round(target_savings_rate, 4),
        "fire_age": fire_age,
        "fire_year": 2024 + (fire_age - age),
        "years_to_fire": fire_age - age,
        "asset_allocation": {
            "equity": round(equity_pct, 2),
            "debt": round(max(0.1, debt_pct), 2),
            "gold": 0.05,
            "cash": 0.05,
        },
    }


def calculate_emergency_fund(
    monthly_expenses: float,
    current_emergency_fund: float,
    months_target: int = 6,
) -> dict[str, Any]:
    target = monthly_expenses * months_target
    gap = max(0, target - current_emergency_fund)
    coverage_months = current_emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
    score = min(100, int((coverage_months / months_target) * 100))
    return {
        "target": round(target),
        "current": round(current_emergency_fund),
        "gap": round(gap),
        "coverage_months": round(coverage_months, 1),
        "score": score,
    }


def calculate_sip_for_goal(
    goal_amount: float,
    years: int,
    annual_return: float = 0.11,
) -> int:
    if years <= 0:
        return int(goal_amount)
    monthly_return = annual_return / 12
    months = years * 12
    if monthly_return == 0:
        return int(goal_amount / months)
    sip = goal_amount * monthly_return / (((1 + monthly_return) ** months - 1) * (1 + monthly_return))
    return round(sip)


def calculate_tax(
    gross_salary: float,
    hra_received: float = 0,
    rent_paid: float = 0,
    city_type: str = "metro",
    other_80c: float = 0,
    nps_80ccd: float = 0,
    medical_insurance_80d: float = 0,
    home_loan_interest: float = 0,
    other_deductions: float = 0,
) -> dict[str, Any]:

    std_deduction = 75000
    taxable_old = gross_salary - std_deduction

    if rent_paid > 0 and hra_received > 0:
        hra_limit_pct = 0.50 if city_type == "metro" else 0.40
        hra_exemption = min(
            hra_received,
            rent_paid - 0.10 * gross_salary,
            hra_limit_pct * gross_salary,
        )
        taxable_old -= max(0, hra_exemption)

    deduction_80c = min(150000, other_80c)
    deduction_80d = min(25000, medical_insurance_80d)
    deduction_nps = min(50000, nps_80ccd)
    deduction_home_loan = min(200000, home_loan_interest)

    total_deductions_old = deduction_80c + deduction_80d + deduction_nps + deduction_home_loan + other_deductions
    taxable_old = max(0, taxable_old - total_deductions_old)

    taxable_new = max(0, gross_salary - std_deduction)

    def compute_tax_old(income: float) -> float:
        tax = 0.0
        slabs = [(250000, 0), (500000, 0.05), (1000000, 0.20), (float("inf"), 0.30)]
        prev = 0
        for limit, rate in slabs:
            if income <= prev:
                break
            taxable_in_slab = min(income, limit) - prev
            tax += taxable_in_slab * rate
            prev = limit
        return tax

    def compute_tax_new(income: float) -> float:
        tax = 0.0
        slabs = [
            (300000, 0), (700000, 0.05), (1000000, 0.10),
            (1200000, 0.15), (1500000, 0.20), (float("inf"), 0.30),
        ]
        prev = 0
        for limit, rate in slabs:
            if income <= prev:
                break
            taxable_in_slab = min(income, limit) - prev
            tax += taxable_in_slab * rate
            prev = limit
        if income <= 700000:
            tax = 0
        return tax

    tax_old = compute_tax_old(taxable_old) * 1.04
    tax_new = compute_tax_new(taxable_new) * 1.04

    unused_80c = max(0, 150000 - other_80c)
    unused_nps = max(0, 50000 - nps_80ccd)
    unused_80d = max(0, 25000 - medical_insurance_80d)

    return {
        "gross_salary": round(gross_salary),
        "old_regime": {
            "taxable_income": round(taxable_old),
            "tax_payable": round(tax_old),
            "effective_rate": round(tax_old / gross_salary, 4) if gross_salary > 0 else 0,
            "total_deductions": round(total_deductions_old + std_deduction),
        },
        "new_regime": {
            "taxable_income": round(taxable_new),
            "tax_payable": round(tax_new),
            "effective_rate": round(tax_new / gross_salary, 4) if gross_salary > 0 else 0,
            "total_deductions": round(std_deduction),
        },
        "recommended_regime": "old" if tax_old < tax_new else "new",
        "tax_saving_by_choice": round(abs(tax_old - tax_new)),
        "unused_deductions": {
            "80c_unused": round(unused_80c),
            "nps_unused": round(unused_nps),
            "80d_unused": round(unused_80d),
        },
    }


def calculate_xirr(cash_flows: list[dict], guess: float = 0.1) -> float:
    if not cash_flows or len(cash_flows) < 2:
        return 0.0
    try:
        dates = [cf["date"] for cf in cash_flows]
        amounts = [cf["amount"] for cf in cash_flows]
        base_date = dates[0]
        days = [(d - base_date).days for d in dates]

        def npv(rate):
            return sum(amt / (1 + rate) ** (d / 365.0) for amt, d in zip(amounts, days))

        def npv_derivative(rate):
            return sum(-d / 365.0 * amt / (1 + rate) ** (d / 365.0 + 1) for amt, d in zip(amounts, days))

        rate = guess
        for _ in range(100):
            f = npv(rate)
            f_prime = npv_derivative(rate)
            if abs(f_prime) < 1e-10:
                break
            rate_new = rate - f / f_prime
            if abs(rate_new - rate) < 1e-6:
                rate = rate_new
                break
            rate = rate_new
        return round(rate, 4)
    except Exception:
        return 0.0