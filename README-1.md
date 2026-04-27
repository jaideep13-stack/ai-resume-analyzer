# ATS Resume Analyser

AI-powered resume evaluator using Groq + LLaMA 3.
Scores your projects across 10 engineering criteria like a strict recruiter.

---

## Setup & Run

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run the app
```bash
streamlit run app.py
```

### Step 3 — Use it
1. Open http://localhost:8501 in your browser
2. Paste your Groq API key in the sidebar
3. Upload your resume PDF
4. Click **Analyse Resume**

---

## Get a Free Groq API Key
→ https://console.groq.com
Sign up → API Keys → Create Key → Copy it

---

## What it evaluates

| # | Criterion            |
|---|----------------------|
| 1 | Problem Clarity      |
| 2 | Problem Importance   |
| 3 | Approach & Decisions |
| 4 | Core Logic           |
| 5 | Tech Stack Usage     |
| 6 | Results & Impact     |
| 7 | Challenges Faced     |
| 8 | Future Improvements  |
| 9 | Practicality         |
|10 | Presentation Strength|

---

## Files
```
ATS_Analyser/
├── app.py            ← main Streamlit app
├── requirements.txt  ← dependencies
└── README.md         ← this file
```
