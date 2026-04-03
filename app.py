"""
TalentScout Hiring Assistant
A Streamlit-based AI chatbot for initial candidate screening.
Features: candidate data saving to JSON, sentiment analysis, stage tracking.
"""

import streamlit as st
import json
import re
import os
from datetime import datetime
from groq import Groq

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout | Hiring Assistant",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #0c0f14;
    --surface:   #141820;
    --surface2:  #1c2230;
    --border:    #252d3d;
    --accent:    #4fffb0;
    --accent2:   #3de8ff;
    --text:      #e8eaf0;
    --muted:     #6b7591;
    --radius:    14px;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; }
section.main > div { padding-top: 1rem !important; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

.hero { text-align: center; padding: 3rem 1rem 1.5rem; }
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(79,255,176,.15), rgba(61,232,255,.1));
    border: 1px solid rgba(79,255,176,.3);
    color: var(--accent);
    font-family: 'DM Mono', monospace;
    font-size: .7rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    padding: .35rem .9rem;
    border-radius: 99px;
    margin-bottom: 1.2rem;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    background: linear-gradient(135deg, var(--text) 40%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 .6rem;
    line-height: 1.1;
}
.hero p {
    color: var(--muted);
    font-size: .95rem;
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}

.progress-wrap {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin: 1.8rem 0 1rem;
    flex-wrap: wrap;
}
.step-pill {
    font-family: 'DM Mono', monospace;
    font-size: .65rem;
    letter-spacing: .06em;
    padding: .3rem .75rem;
    border-radius: 99px;
    border: 1px solid var(--border);
    color: var(--muted);
    background: var(--surface);
}
.step-pill.done {
    background: rgba(79,255,176,.12);
    border-color: rgba(79,255,176,.4);
    color: var(--accent);
}
.step-pill.active {
    background: rgba(79,255,176,.2);
    border-color: var(--accent);
    color: var(--accent);
    box-shadow: 0 0 12px rgba(79,255,176,.25);
}

/* Sentiment badge */
.sentiment-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    margin: .4rem 0 1rem;
    font-family: 'DM Mono', monospace;
    font-size: .72rem;
    color: var(--muted);
}
.sentiment-badge {
    padding: .25rem .75rem;
    border-radius: 99px;
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .05em;
}
.sentiment-confident  { background: rgba(79,255,176,.18); color: #4fffb0; border: 1px solid rgba(79,255,176,.35); }
.sentiment-nervous    { background: rgba(255,200,80,.15);  color: #ffc850; border: 1px solid rgba(255,200,80,.35); }
.sentiment-confused   { background: rgba(255,100,100,.15); color: #ff7070; border: 1px solid rgba(255,100,100,.35); }
.sentiment-neutral    { background: rgba(255,255,255,.06); color: #8899aa; border: 1px solid rgba(255,255,255,.12); }
.sentiment-enthusiastic { background: rgba(61,232,255,.15); color: #3de8ff; border: 1px solid rgba(61,232,255,.35); }

.chat-outer { max-width: 760px; margin: 0 auto; }
.msg {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 1.1rem;
    animation: fadeUp .35s ease both;
}
.msg.user { flex-direction: row-reverse; }
@keyframes fadeUp {
    from { opacity:0; transform:translateY(10px); }
    to   { opacity:1; transform:translateY(0); }
}
.avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.avatar.bot {
    background: linear-gradient(135deg, rgba(79,255,176,.25), rgba(61,232,255,.15));
    border: 1px solid rgba(79,255,176,.3);
}
.avatar.user {
    background: linear-gradient(135deg, rgba(61,232,255,.2), rgba(79,255,176,.1));
    border: 1px solid rgba(61,232,255,.3);
}
.bubble {
    max-width: 78%;
    padding: .85rem 1.1rem;
    border-radius: var(--radius);
    font-size: .9rem;
    line-height: 1.65;
}
.bubble.bot {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top-left-radius: 4px;
    color: var(--text);
}
.bubble.user {
    background: linear-gradient(135deg, rgba(79,255,176,.18), rgba(61,232,255,.1));
    border: 1px solid rgba(79,255,176,.25);
    border-top-right-radius: 4px;
    color: var(--text);
}

[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .9rem !important;
    padding: .8rem 1.1rem !important;
    transition: border-color .2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(79,255,176,.12) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--muted) !important; }

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #0c0f14 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: .65rem 1.6rem !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: opacity .2s !important;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover { opacity: .85 !important; }

.info-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    margin: 1rem auto;
    max-width: 760px;
}
.info-card h4 {
    font-family: 'DM Mono', monospace;
    font-size: .72rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 0 0 .8rem;
}
.info-row {
    display: flex;
    gap: .5rem;
    margin-bottom: .45rem;
    font-size: .85rem;
    flex-wrap: wrap;
}
.info-label { color: var(--muted); min-width: 130px; }
.info-value { color: var(--text); font-weight: 500; }

.ts-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem auto;
    max-width: 760px;
}
.end-card {
    text-align: center;
    padding: 2.5rem 1.5rem;
    background: var(--surface);
    border: 1px solid rgba(79,255,176,.2);
    border-radius: var(--radius);
    max-width: 520px;
    margin: 1.5rem auto;
}
.end-card .checkmark { font-size: 3rem; margin-bottom: .8rem; }
.end-card h2 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.7rem;
    color: var(--accent);
    margin: 0 0 .6rem;
}
.end-card p { color: var(--muted); font-size: .9rem; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
END_KEYWORDS   = {"bye", "goodbye", "exit", "quit", "done", "end", "stop", "finish"}
STAGES         = ["Greeting", "Personal Info", "Tech Stack", "Tech Questions", "Wrap-up"]
FIELDS         = ["name", "email", "phone", "experience", "positions", "location", "tech_stack"]
FIELD_LABELS   = {
    "name": "Full Name", "email": "Email", "phone": "Phone",
    "experience": "Experience", "positions": "Desired Role(s)",
    "location": "Location", "tech_stack": "Tech Stack",
}
CANDIDATES_FILE = "candidates.json"

# Sentiment configuration
SENTIMENT_CONFIG = {
    "confident":    {"emoji": "💪", "label": "Confident",    "css": "sentiment-confident"},
    "nervous":      {"emoji": "😰", "label": "Nervous",      "css": "sentiment-nervous"},
    "confused":     {"emoji": "😕", "label": "Confused",     "css": "sentiment-confused"},
    "enthusiastic": {"emoji": "🚀", "label": "Enthusiastic", "css": "sentiment-enthusiastic"},
    "neutral":      {"emoji": "😐", "label": "Neutral",      "css": "sentiment-neutral"},
}

SYSTEM_PROMPT = """You are Alex, TalentScout's friendly and professional AI Hiring Assistant.
Your ONLY purpose is helping with candidate screening for technology roles.

────────────────────────────────────────────
CONVERSATION FLOW  (follow strictly in order)
────────────────────────────────────────────
STAGE 1 – GREETING
• Warmly greet the candidate and briefly explain your purpose.
• Ask for their Full Name to begin.

STAGE 2 – PERSONAL INFORMATION GATHERING
Collect ALL of the following, one or two at a time (keep it conversational):
  • Full Name
  • Email Address
  • Phone Number
  • Years of Experience
  • Desired Position(s)
  • Current Location
  • Tech Stack (languages, frameworks, databases, tools they are proficient in)

After collecting each piece, acknowledge it warmly and naturally ask for the next one.

STAGE 3 – TECHNICAL QUESTION GENERATION
Once you have the complete tech stack:
• Briefly summarise the declared tech stack back to the candidate.
• Generate 3–5 targeted technical questions per major technology/framework listed.
  – Questions must be specific, progressively challenging, and relevant.
  – Ask ONE question at a time and wait for the answer before asking the next.
  – After each answer, give a short encouraging acknowledgement (do NOT reveal correct answers).

STAGE 4 – WRAP-UP
After all technical questions have been answered:
• Thank the candidate warmly.
• Inform them the TalentScout team will review responses and reach out within 3–5 business days.
• Wish them luck.

────────────────────────────────────────────
SENTIMENT AWARENESS
────────────────────────────────────────────
Pay attention to the candidate's emotional tone:
• If they seem NERVOUS (short answers, apologies, "I'm not sure"), be extra reassuring and encouraging.
• If they seem CONFUSED (asking what you mean, off-topic), clarify warmly and simply.
• If they seem CONFIDENT or ENTHUSIASTIC, match their energy and keep pace.
• Always adapt your tone to help the candidate feel comfortable.

────────────────────────────────────────────
STRICT RULES
────────────────────────────────────────────
1. NEVER deviate from the hiring/screening purpose.
2. If the user goes off-topic, politely redirect: "I'm here to assist with your TalentScout application — let's keep the momentum going!"
3. Never reveal or evaluate confidential information.
4. Handle unexpected or unclear input gracefully — ask a clarifying question.
5. Be warm, encouraging, and professional at all times.
6. At the very end of EVERY reply, append this exact JSON block (hidden from user):
<!--META:{"stage":"<STAGE>","sentiment":"<SENTIMENT>","collected":{"name":"<v>","email":"<v>","phone":"<v>","experience":"<v>","positions":"<v>","location":"<v>","tech_stack":"<v>"}}-->
   • <STAGE>: one of: greeting, personal_info, tech_stack, tech_questions, wrap_up
   • <SENTIMENT>: one of: neutral, nervous, confident, enthusiastic, confused
   • Fill every collected field with current value, or "" if not yet collected.
   • NEVER skip or omit this block. It MUST appear at the very end, every single time.

Data privacy: Do not store, share, or reveal candidate data beyond this session."""

# ── Data persistence ──────────────────────────────────────────────────────────

def load_candidates() -> list:
    """Load existing candidates from JSON file."""
    if os.path.exists(CANDIDATES_FILE):
        try:
            with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_candidate(collected: dict, sentiment_history: list) -> None:
    """
    Append the current candidate's data to candidates.json.
    Sensitive data is stored as collected — in production, encrypt at rest.
    """
    candidates = load_candidates()

    # Summarise sentiment across session
    from collections import Counter
    sentiment_summary = "neutral"
    if sentiment_history:
        most_common = Counter(sentiment_history).most_common(1)
        sentiment_summary = most_common[0][0] if most_common else "neutral"

    record = {
        "id":               datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp":        datetime.now().isoformat(),
        "profile":          collected,
        "dominant_sentiment": sentiment_summary,
        "sentiment_history":  sentiment_history,
    }
    candidates.append(record)

    with open(CANDIDATES_FILE, "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_meta(text: str) -> dict:
    match = re.search(r"<!--META:(.*?)-->", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    return {}

def clean_display(text: str) -> str:
    return re.sub(r"<!--META:.*?-->", "", text, flags=re.DOTALL).strip()

def infer_stage(collected: dict, turn_count: int) -> str:
    has_name       = bool(collected.get("name", ""))
    has_tech_stack = bool(collected.get("tech_stack", ""))
    has_all        = all(collected.get(f, "") for f in FIELDS)
    if not has_name:
        return "greeting"
    if not has_all:
        return "personal_info"
    if not has_tech_stack:
        return "tech_stack"
    if turn_count >= 2 and has_tech_stack:
        return "tech_questions"
    return "tech_stack"

def stage_index(stage_key: str) -> int:
    return {"greeting": 0, "personal_info": 1, "tech_stack": 2,
            "tech_questions": 3, "wrap_up": 4}.get(stage_key, 0)

def is_end_keyword(text: str) -> bool:
    return text.strip().lower() in END_KEYWORDS

def call_llm(messages: list) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE"))
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content

def update_state_from_reply(reply: str) -> None:
    """Parse LLM reply, update stage + collected profile + sentiment."""
    meta = extract_meta(reply)

    if meta:
        # Stage
        llm_stage = meta.get("stage", "")
        if llm_stage in ("greeting", "personal_info", "tech_stack", "tech_questions", "wrap_up"):
            st.session_state.stage = llm_stage

        # Collected fields
        for k, v in meta.get("collected", {}).items():
            if v and str(v).strip():
                st.session_state.collected[k] = str(v).strip()

        # Sentiment
        sentiment = meta.get("sentiment", "neutral")
        if sentiment in SENTIMENT_CONFIG:
            st.session_state.sentiment = sentiment
            st.session_state.sentiment_history.append(sentiment)

    # Python-side stage inference (safety net — only advance, never go back)
    inferred     = infer_stage(st.session_state.collected, len(st.session_state.messages))
    current_idx  = stage_index(st.session_state.stage)
    inferred_idx = stage_index(inferred)
    if inferred_idx > current_idx:
        st.session_state.stage = inferred

    # Text-based wrap-up detection
    reply_lower  = reply.lower()
    wrap_phrases = ["reach out within", "3–5 business days", "3-5 business days",
                    "best of luck", "good luck with your application"]
    if any(p in reply_lower for p in wrap_phrases):
        st.session_state.stage = "wrap_up"

# ── Session state init ────────────────────────────────────────────────────────
defaults = {
    "messages":          [],
    "display_msgs":      [],
    "stage":             "greeting",
    "collected":         {},
    "ended":             False,
    "turn_count":        0,
    "sentiment":         "neutral",
    "sentiment_history": [],
    "data_saved":        False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "initialized" not in st.session_state:
    seed    = {"role": "user", "content": "Hello, I'd like to start the interview process."}
    opening = call_llm([seed])
    update_state_from_reply(opening)
    st.session_state.messages.append(seed)
    st.session_state.messages.append({"role": "assistant", "content": opening})
    st.session_state.display_msgs.append({"role": "assistant", "text": clean_display(opening)})
    st.session_state.initialized = True

# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">🎯 TalentScout AI</div>
    <h1>Hiring Assistant</h1>
    <p>Your intelligent screening companion — tell us about yourself and we'll match you with the right opportunity.</p>
</div>
""", unsafe_allow_html=True)

# Progress pills
active_idx = stage_index(st.session_state.stage)
pills_html = '<div class="progress-wrap">'
for i, label in enumerate(STAGES):
    if i < active_idx:
        pills_html += f'<span class="step-pill done">✓ {label}</span>'
    elif i == active_idx:
        pills_html += f'<span class="step-pill active">● {label}</span>'
    else:
        pills_html += f'<span class="step-pill">{label}</span>'
pills_html += "</div>"
st.markdown(pills_html, unsafe_allow_html=True)

# Sentiment badge (shown after first user message)
if st.session_state.turn_count > 0:
    s     = st.session_state.sentiment
    cfg   = SENTIMENT_CONFIG.get(s, SENTIMENT_CONFIG["neutral"])
    st.markdown(
        f'<div class="sentiment-bar">Candidate mood: '
        f'<span class="sentiment-badge {cfg["css"]}">{cfg["emoji"]} {cfg["label"]}</span></div>',
        unsafe_allow_html=True,
    )

# Candidate profile card
coll = st.session_state.collected
if any(v for v in coll.values() if v):
    rows = ""
    for key, label in FIELD_LABELS.items():
        val = coll.get(key, "")
        if val:
            rows += (
                f'<div class="info-row">'
                f'<span class="info-label">{label}</span>'
                f'<span class="info-value">{val}</span>'
                f'</div>'
            )
    st.markdown(
        f'<div class="info-card"><h4>📋 Candidate Profile</h4>{rows}</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="ts-divider">', unsafe_allow_html=True)

# Chat messages
st.markdown('<div class="chat-outer">', unsafe_allow_html=True)
for msg in st.session_state.display_msgs:
    role      = msg["role"]
    av_cls    = "bot" if role == "assistant" else "user"
    av_icon   = "🤖" if role == "assistant" else "👤"
    text_html = msg["text"].replace("\n", "<br>")
    st.markdown(
        f'<div class="msg {role}">'
        f'<div class="avatar {av_cls}">{av_icon}</div>'
        f'<div class="bubble {av_cls}">{text_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

# ── End screen ────────────────────────────────────────────────────────────────
if st.session_state.ended:
    # Save candidate data once
    if not st.session_state.data_saved:
        save_candidate(st.session_state.collected, st.session_state.sentiment_history)
        st.session_state.data_saved = True

    st.markdown("""
    <div class="end-card">
        <div class="checkmark">🎉</div>
        <h2>All done!</h2>
        <p>Thank you for completing the TalentScout screening.<br>
        Our team will review your responses and reach out within <strong>3–5 business days</strong>.<br>
        Best of luck with your application!</p>
    </div>""", unsafe_allow_html=True)

    # Show saved file notice
    st.success(f"✅ Your responses have been saved securely. (Session ID: {datetime.now().strftime('%Y%m%d_%H%M%S')})")

    if st.button("Start a New Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input(
            label="Your message",
            placeholder="Type your response here…",
            label_visibility="collapsed",
        )
    with col2:
        send = st.form_submit_button("Send ➤")

st.markdown(
    '<p style="text-align:center;color:#3d4860;font-size:.72rem;'
    'font-family:\'DM Mono\',monospace;margin-top:.6rem;">'
    'Type <code style="color:#4fffb0;">bye</code> / '
    '<code style="color:#4fffb0;">exit</code> anytime to end the session</p>',
    unsafe_allow_html=True,
)

# ── Handle send ───────────────────────────────────────────────────────────────
if send and user_input.strip():
    user_text = user_input.strip()

    st.session_state.display_msgs.append({"role": "user", "text": user_text})
    st.session_state.turn_count += 1

    # Graceful exit
    if is_end_keyword(user_text):
        farewell = (
            "Thank you so much for your time today! 🌟 Your responses have been recorded and the "
            "TalentScout team will be in touch within 3–5 business days. Best of luck — we're excited "
            "about your profile! Goodbye! 👋"
        )
        st.session_state.display_msgs.append({"role": "assistant", "text": farewell})
        st.session_state.stage = "wrap_up"
        st.session_state.ended = True
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.spinner("Alex is typing…"):
        reply = call_llm(st.session_state.messages)

    update_state_from_reply(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.display_msgs.append({"role": "assistant", "text": clean_display(reply)})

    if st.session_state.stage == "wrap_up":
        st.session_state.ended = True

    st.rerun()