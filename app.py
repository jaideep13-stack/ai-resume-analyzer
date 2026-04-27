import streamlit as st
import fitz  
import json
import requests
from dotenv import load_dotenv
import os 
load_dotenv()

# Page config 
st.set_page_config(
    page_title="ATS Resume Analyser",
    page_icon=" ",
    layout="centered",
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: #080C10;
    color: #CBD5E1;
}

.stApp { background-color: #080C10; }

/* Cards */
.card {
    background: #0D1117;
    border: 1px solid #1C2433;
    border-radius: 6px;
    padding: 20px 24px;
    margin-bottom: 16px;
}

/* Section label */
.sec-label {
    font-size: 10px;
    color: #475569;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
    border-bottom: 1px solid #1C2433;
    padding-bottom: 6px;
}

/* Score badge */
.score-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 3px;
    font-size: 12px;
    font-weight: 700;
}

.hi  { background: rgba(16,185,129,0.15); color: #10B981; border: 1px solid rgba(16,185,129,0.3); }
.mid { background: rgba(245,158,11,0.15); color: #F59E0B; border: 1px solid rgba(245,158,11,0.3); }
.lo  { background: rgba(239,68,68,0.15);  color: #EF4444; border: 1px solid rgba(239,68,68,0.3); }

/* Verdict box */
.verdict-pass  { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.35); color: #6ee7b7; border-radius:4px; padding:14px 18px; }
.verdict-maybe { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.35); color: #fcd34d; border-radius:4px; padding:14px 18px; }
.verdict-fail  { background: rgba(239,68,68,0.08);  border: 1px solid rgba(239,68,68,0.35);  color: #fca5a5; border-radius:4px; padding:14px 18px; }

/* Criterion row */
.crit-row {
    background: #080C10;
    border: 1px solid #1C2433;
    border-radius: 4px;
    padding: 14px 16px;
    margin-bottom: 10px;
}

.crit-name { font-size: 11px; font-weight: 600; color: #F1F5F9; letter-spacing: 1px; }
.crit-feedback { font-size: 11px; color: #64748B; line-height: 1.7; margin-top: 6px; }

/* Override Streamlit defaults */
div[data-testid="stFileUploader"] { background: #0D1117 !important; }
</style>
""", unsafe_allow_html=True)


#  Header 
st.markdown("""
<div style="margin-bottom:32px;">
    <div style="font-size:10px;color:#3B82F6;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">
        ● AI/ML Recruiter Simulator
    </div>
    <h1 style="font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:800;
               color:#F1F5F9;margin:0;letter-spacing:-1px;">
        ATS Resume <span style="color:#3B82F6;">Analyser</span>
    </h1>
    <p style="color:#475569;font-size:11.5px;margin-top:10px;line-height:1.8;">
        Evaluates resume projects across 10 engineering criteria.<br>
        Powered by Groq + LLaMA 3. Brutally honest. No sugarcoating.
    </p>
</div>
""", unsafe_allow_html=True)


#  Sidebar — config 
with st.sidebar:
    st.markdown("###  Configuration")
    api_key = os.getenv("GROQ_API_KEY") or st.text_input(
    "Groq API Key",
    type="password",
    placeholder="gsk_xxxx...",
    help="Get your key at console.groq.com"
    )
    model = st.selectbox(
        "Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
        index=0,
    )
    st.markdown("---")
    st.markdown("""
**How to use:**
1. Paste your Groq API key
2. Upload your resume PDF
3. Click **Analyse Resume**

**Get Groq key free:**
[console.groq.com](https://console.groq.com)
""")


# PDF extraction 
def extract_pdf_text(uploaded_file) -> str:
    data = uploaded_file.read()
    doc  = fitz.open(stream=data, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


# Groq API call 
def call_groq(api_key: str, model: str, resume_text: str) -> dict:
    prompt = f"""
Act as a strict senior AI/ML engineer reviewing this resume for an internship position.
Evaluate ONLY the projects section. Score each criterion from 0–10.

RESUME TEXT:
\"\"\"
{resume_text[:6000]}
\"\"\"

Evaluate based on these 10 criteria and return ONLY a JSON object in this exact shape:
{{
  "overall_score": <number 0–100>,
  "overall_label": "<Weak|Below Average|Average|Strong|Excellent>",
  "overall_summary": "<2–3 sentence harsh, specific verdict on the resume project quality>",
  "verdict": "<pass|maybe|fail>",
  "verdict_text": "<1–2 sentences: would you shortlist this candidate? Why or why not?>",
  "criteria": [
    {{ "name": "Problem Clarity",       "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Problem Importance",    "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Approach & Decisions",  "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Core Logic",            "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Tech Stack Usage",      "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Results & Impact",      "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Challenges Faced",      "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Future Improvements",   "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Practicality",          "score": <0–10>, "feedback": "<specific, max 2 sentences>" }},
    {{ "name": "Presentation Strength", "score": <0–10>, "feedback": "<specific, max 2 sentences>" }}
  ]
}}

Rules:
- Be brutally specific. Name which project is weak and exactly why.
- Do not give 7+ unless there is clear, measurable evidence of that quality.
- Do not reward tool listing — reward engineering reasoning.
- Return ONLY the JSON. No markdown. No preamble. No explanation outside JSON.
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        },
        json={
            "model":       model,
            "temperature": 0.2,
            "max_tokens":  2000,
            "messages": [
                {
                    "role":    "system",
                    "content": (
                        "You are a brutally honest senior AI/ML engineer and recruiter. "
                        "You evaluate resumes with zero tolerance for vague claims, "
                        "theory-heavy language, or surface-level tool usage. "
                        "You ALWAYS respond with valid JSON only. "
                        "No preamble. No markdown fences. Just the raw JSON object."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )

    if response.status_code != 200:
        err = response.json().get("error", {}).get("message", f"HTTP {response.status_code}")
        raise RuntimeError(f"Groq API error: {err}")

    raw   = response.json()["choices"][0]["message"]["content"]
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ── Score colour helper ───────────────────────────────────────────────────────
def score_class(s: int) -> str:
    return "hi" if s >= 7 else "mid" if s >= 5 else "lo"

def score_color(s: int) -> str:
    return "#10B981" if s >= 7 else "#F59E0B" if s >= 5 else "#EF4444"


#  Main UI 
uploaded = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"],
    help="Upload a text-based PDF (not scanned image).",
)

run = st.button("🎯 Analyse Resume", use_container_width=True, type="primary")

if run:
    # Validations
    if not api_key:
        st.error(" Enter your Groq API key in the sidebar.")
        st.stop()
    if not uploaded:
        st.error(" Upload a resume PDF first.")
        st.stop()

    # Extract text
    with st.spinner("Extracting PDF text…"):
        try:
            resume_text = extract_pdf_text(uploaded)
        except Exception as e:
            st.error(f"PDF extraction failed: {e}")
            st.stop()

    if not resume_text:
        st.error("Could not extract text. Make sure it's a text-based PDF, not a scanned image.")
        st.stop()

    # Call Groq
    with st.spinner("Sending to Groq + LLaMA 3… this takes ~5 seconds"):
        try:
            result = call_groq(api_key, model, resume_text)
        except json.JSONDecodeError:
            st.error("Model returned invalid JSON. Try again or switch to llama3-70b-8192.")
            st.stop()
        except RuntimeError as e:
            st.error(str(e))
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.stop()

    #  Render results 

    overall = result.get("overall_score", 0)
    label   = result.get("overall_label", "")
    summary = result.get("overall_summary", "")
    verdict = result.get("verdict", "fail")
    v_text  = result.get("verdict_text", "")
    criteria = result.get("criteria", [])

    # Overall score
    oc = score_color(overall / 10)
    st.markdown(f"""
<div class="card">
    <div class="sec-label">Overall Evaluation</div>
    <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
        <div style="text-align:center;min-width:80px;">
            <div style="font-size:36px;font-weight:800;color:{oc};font-family:'JetBrains Mono',monospace;">
                {overall}
            </div>
            <div style="font-size:10px;color:#475569;">/ 100</div>
        </div>
        <div>
            <div style="font-size:16px;font-weight:700;color:#F1F5F9;margin-bottom:6px;">{label}</div>
            <div style="font-size:11.5px;color:#64748B;line-height:1.8;max-width:500px;">{summary}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Verdict
    v_class = {"pass": "verdict-pass", "maybe": "verdict-maybe", "fail": "verdict-fail"}.get(verdict, "verdict-fail")
    v_emoji = {"pass": "✅ Shortlist: Yes", "maybe": "⚠️ Shortlist: Maybe", "fail": "❌ Shortlist: No"}.get(verdict, "❌")
    st.markdown(f"""
<div class="{v_class}" style="margin-bottom:20px;">
    <strong style="font-size:13px;display:block;margin-bottom:4px;">{v_emoji}</strong>
    <span style="font-size:11.5px;">{v_text}</span>
</div>
""", unsafe_allow_html=True)

    # Per-criterion breakdown
    st.markdown('<div class="sec-label" style="font-size:10px;color:#475569;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">Criteria Breakdown</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for i, c in enumerate(criteria):
        sc   = c.get("score", 0)
        cls  = score_class(sc)
        col  = col1 if i % 2 == 0 else col2
        pct  = int((sc / 10) * 100)
        bar_color = score_color(sc)

        with col:
            st.markdown(f"""
<div class="crit-row">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span class="crit-name">{c.get('name','')}</span>
        <span class="score-badge {cls}">{sc}/10</span>
    </div>
    <div style="height:3px;background:#1C2433;border-radius:2px;margin-bottom:10px;">
        <div style="height:3px;width:{pct}%;background:{bar_color};border-radius:2px;"></div>
    </div>
    <div class="crit-feedback">{c.get('feedback','')}</div>
</div>
""", unsafe_allow_html=True)

    st.success("Analysis complete. Review the gaps above and fix them before applying.")
