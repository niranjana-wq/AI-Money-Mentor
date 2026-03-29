# AI Money Mentor

> India's AI-powered personal finance mentor. Free, instant, built for the Indian middle class.

Built for the ET GenAI Hackathon — gives every Indian what only HNIs could afford: a personalised financial plan.

---

## What it does

| Feature | Description |
|---|---|
| FIRE Path Planner | Month-by-month roadmap to financial independence |
| Money Health Score | Wellness score across 6 financial dimensions |
| Tax Wizard | Find every deduction you're missing · old vs new regime |
| Life Event Advisor | Bonus, marriage, baby — AI advice for your exact situation |
| MF Portfolio X-Ray | Upload CAMS statement · get XIRR, overlap, rebalancing plan |
| Couple's Money Planner | Optimise HRA, NPS, SIP splits across both incomes |

---

## Tech stack

- **Frontend** — HTML, CSS, JavaScript (no framework)
- **Backend** — Python, FastAPI
- **AI** — Google Gemini 1.5 Flash
- **Deployment** — Vercel

---

## Local setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/ai-money-mentor.git
cd ai-money-mentor
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add environment variables

Create a `.env` file in the root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
APP_ENV=development
INFLATION_RATE=0.06
EQUITY_RETURN_RATE=0.11
DEBT_RETURN_RATE=0.07
FD_RETURN_RATE=0.065
SAFE_WITHDRAWAL_RATE=0.04
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

Get your free Gemini API key at [aistudio.google.com](https://aistudio.google.com)

### 5. Run the backend
```bash
uvicorn api.index:app --reload --port 8000
```

Backend live at: `http://127.0.0.1:8000`
API docs at: `http://127.0.0.1:8000/docs`

### 6. Run the frontend

Open a second terminal:
```bash
# Windows (PowerShell)
cd frontend
python -m http.server 5500

# Mac / Linux
cd frontend
python3 -m http.server 5500
```

Frontend live at: `http://127.0.0.1:5500`

### 7. Open in browser
```
http://127.0.0.1:5500/index.html
```

---

## Deploy to Vercel

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/yourusername/ai-money-mentor.git
git push -u origin main
```

### 2. Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **Add New Project**
3. Import your GitHub repo
4. Add environment variable: `GEMINI_API_KEY` = your key
5. Click **Deploy**

Done — your app is live.

---

## Project structure
```
ai-money-mentor/
├── frontend/
│   ├── index.html          # Landing page
│   ├── onboarding.html     # Input form
│   ├── result.html         # Output dashboard
│   ├── css/
│   │   ├── style.css       # Design tokens
│   │   └── components.css  # UI components
│   └── js/
│       ├── engine.js       # API calls + form logic
│       └── render.js       # Result rendering
├── api/
│   ├── index.py            # FastAPI app + router
│   ├── fire.py             # FIRE planner endpoint
│   ├── score.py            # Health score endpoint
│   ├── tax.py              # Tax wizard endpoint
│   ├── life_event.py       # Life event endpoint
│   ├── mf_xray.py          # MF X-ray endpoint
│   └── couples.py          # Couples planner endpoint
├── core/
│   ├── calculator.py       # FIRE math formulas
│   ├── scorer.py           # Health score logic
│   ├── prompts.py          # All AI system prompts
│   ├── ai_client.py        # Gemini API wrapper
│   ├── validator.py        # AI response validation
│   └── parser.py           # CAMS/Form16 parser
├── vercel.json             # Vercel routing config
├── requirements.txt        # Python dependencies
└── .env                    # API keys (never commit)
```

---

## Demo persona

To test quickly, use these inputs:

| Field | Value |
|---|---|
| Age | 28 |
| Monthly income | ₹80,000 |
| Monthly expenses | ₹50,000 |
| Existing investments | ₹5,00,000 |
| Current SIP | ₹8,000 |
| Emergency fund | ₹1,00,000 |
| Life insurance | ₹1,00,00,000 |
| Health insurance | ₹5,00,000 |

---

## Problem statement

95% of Indians have no financial plan. Financial advisors charge ₹25,000+/year and serve only HNIs. AI Money Mentor democratises access — giving every Indian the same quality financial guidance, free, in under 2 minutes.

---

*Built with for India · ET GenAI Hackathon 2024*