import re
from typing import Any


def parse_cams_text(raw_text: str) -> dict[str, Any]:
    funds = []
    total_invested = 0
    current_value = 0

    fund_pattern = re.compile(
        r"(?P<fund_name>[A-Z][^\n]{10,80}(?:Fund|FUND)[^\n]*)\n"
        r".*?Units?[:\s]+(?P<units>[\d,]+\.?\d*)"
        r".*?NAV[:\s]+(?P<nav>[\d,]+\.?\d*)"
        r".*?(?:Current Value|Market Value)[:\s]+(?P<value>[\d,]+\.?\d*)",
        re.DOTALL | re.IGNORECASE,
    )

    for match in fund_pattern.finditer(raw_text):
        units = float(match.group("units").replace(",", ""))
        nav = float(match.group("nav").replace(",", ""))
        value = float(match.group("value").replace(",", ""))
        funds.append({
            "fund_name": match.group("fund_name").strip(),
            "units": units,
            "nav": nav,
            "current_value": round(value),
            "category": _infer_category(match.group("fund_name")),
            "expense_ratio": _estimate_expense_ratio(match.group("fund_name")),
        })
        current_value += value

    total_invested = current_value * 0.85

    return {
        "funds": funds,
        "total_invested": round(total_invested),
        "current_value": round(current_value),
        "fund_count": len(funds),
        "parsed_successfully": len(funds) > 0,
    }


def _infer_category(fund_name: str) -> str:
    name = fund_name.lower()
    if any(k in name for k in ["liquid", "overnight", "money market"]):
        return "liquid"
    if any(k in name for k in ["debt", "bond", "gilt", "income", "credit"]):
        return "debt"
    if any(k in name for k in ["small cap", "smallcap"]):
        return "small_cap"
    if any(k in name for k in ["mid cap", "midcap"]):
        return "mid_cap"
    if any(k in name for k in ["large cap", "largecap", "bluechip", "nifty 50", "sensex"]):
        return "large_cap"
    if any(k in name for k in ["hybrid", "balanced", "equity savings"]):
        return "hybrid"
    if any(k in name for k in ["elss", "tax saver", "tax saving"]):
        return "elss"
    if any(k in name for k in ["international", "global", "overseas", "nasdaq", "s&p"]):
        return "international"
    return "diversified_equity"


def _estimate_expense_ratio(fund_name: str) -> float:
    name = fund_name.lower()
    if any(k in name for k in ["direct", "dir"]):
        return 0.005
    if any(k in name for k in ["index", "nifty", "sensex", "bse"]):
        return 0.002
    if "liquid" in name:
        return 0.001
    return 0.015


def parse_form16_text(raw_text: str) -> dict[str, Any]:
    def extract_amount(pattern: str, text: str) -> float:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "").replace(" ", ""))
        return 0.0

    gross_salary = extract_amount(r"gross salary[:\s]+(?:rs\.?|₹)?\s*([\d,]+)", raw_text)
    tds = extract_amount(r"(?:total tax deducted|tds)[:\s]+(?:rs\.?|₹)?\s*([\d,]+)", raw_text)
    pf = extract_amount(r"(?:provident fund|epf)[:\s]+(?:rs\.?|₹)?\s*([\d,]+)", raw_text)
    hra = extract_amount(r"hra[:\s]+(?:rs\.?|₹)?\s*([\d,]+)", raw_text)

    return {
        "gross_salary": round(gross_salary),
        "tds_deducted": round(tds),
        "pf_contribution": round(pf),
        "hra_received": round(hra),
        "parsed_successfully": gross_salary > 0,
    }
