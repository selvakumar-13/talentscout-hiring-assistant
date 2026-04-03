# 🎯 TalentScout Hiring Assistant

> An AI-powered conversational chatbot that conducts initial candidate screening for technology roles — built with **Streamlit** and **Groq (Llama 3.3 70B)**.

---

## 📌 Project Overview

TalentScout Hiring Assistant is an intelligent hiring chatbot designed for **TalentScout**, a fictional recruitment agency specialising in technology placements. The chatbot automates the initial screening process by:

- Greeting candidates and explaining the screening process
- Collecting all essential personal and professional details
- Generating **3–5 tailored technical questions** per declared technology
- Performing **real-time sentiment analysis** to adapt its tone to the candidate's emotional state
- Saving candidate data securely to a local JSON file after each session
- Displaying a live **Candidate Profile card** as information is collected
- Tracking progress through a **5-stage visual tracker**
- Ending gracefully on exit keywords or after wrap-up

---

## 🗂️ Repository Structure

```
talentscout-hiring-assistant/
├── app.py              # Main Streamlit application (all logic in one file)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .gitignore          # Excludes candidates.json, __pycache__, .env
└── candidates.json     # Auto-generated at runtime — NOT committed to Git
```

---

## 🖥️ Demo

> 📹 **[Watch the Loom Demo](#)** ← replace with your Loom link

**Screenshots:**

| Greeting Stage | Tech Questions Stage | Wrap-up |
|---|---|---|
| Progress tracker at Step 1 | Sentiment badge + technical Q&A | 🎉 End card + data saved |

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.9 or higher
- A free [Groq API key](https://console.groq.com) (no credit card required)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/talentscout-hiring-assistant.git
cd talentscout-hiring-assistant

# 2. Create and activate a virtual environment (recommended)
python -m venv venv

# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
$env:GROQ_API_KEY="YOUR_GROQ_API_KEY"
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## 🚀 Usage Guide

1. The chatbot **automatically greets** you on page load — no button click needed.
2. **Respond naturally** in the text box at the bottom and press **Send** or hit **Enter**.
3. Watch the **5-stage progress tracker** advance as you move through the conversation.
4. Your **Candidate Profile card** fills in live as Alex collects your information.
5. The **sentiment badge** shows your detected emotional tone (Confident, Nervous, Confused, Enthusiastic, Neutral).
6. Type `bye`, `exit`, `quit`, `done`, `end`, or `stop` at any time to end the session gracefully.
7. After wrap-up, your data is saved and a **Start a New Session** button appears.

---

## 🛠️ Technical Details

| Item | Detail |
|------|--------|
| **Language** | Python 3.9+ |
| **Frontend** | Streamlit 1.35+ |
| **LLM** | Groq — `llama-3.3-70b-versatile` |
| **Styling** | Custom CSS with Google Fonts (DM Serif Display, DM Mono, DM Sans) |
| **State Management** | Streamlit `session_state` (in-memory per session) |
| **Data Storage** | Local `candidates.json` (appended after each session) |
| **Sentiment Analysis** | LLM-driven — 5 categories: neutral, confident, nervous, enthusiastic, confused |

### Architecture

```
User Input (st.form)
        │
        ▼
 End-keyword check ──────────────────► Farewell message + save data + end screen
        │
        ▼
  call_llm(messages)
        │   ┌─────────────────────────────────────────────┐
        │   │  System prompt with:                         │
        │   │  • 4-stage flow enforcement                  │
        │   │  • Sentiment awareness instructions          │
        │   │  • Hidden <!--META:{...}--> output contract  │
        │   └─────────────────────────────────────────────┘
        │
        ▼
 Groq API → Llama 3.3 70B response
        │
        ├─► extract_meta()      → parse stage + sentiment + collected fields
        ├─► update_state()      → update session_state (stage, collected, sentiment)
        ├─► infer_stage()       → Python-side safety net (never rely solely on LLM)
        ├─► clean_display()     → strip <!--META:--> before rendering
        └─► render chat bubble  → display to user
                │
                ▼ (on wrap_up)
        save_candidate()  →  append to candidates.json
```

---

## ✍️ Prompt Design

### System Prompt Strategy

The system prompt uses four key techniques:

**1. Staged flow enforcement**
The prompt explicitly defines four ordered stages and instructs the LLM to follow them strictly, preventing topic drift or jumping ahead.

**2. Hidden metadata contract**
Every LLM reply must end with a hidden HTML comment:
```
<!--META:{"stage":"personal_info","sentiment":"confident","collected":{"name":"Selva","email":"","...}}-->
```
This lets Python track progress and update the UI without extra API calls. The comment is stripped before display using `clean_display()`.

**3. Python-side safety net (`infer_stage`)**
Since LLMs occasionally skip the metadata block, a pure-Python function independently infers the stage from what has been collected. The stage only ever advances — never goes backwards.

**4. Sentiment awareness**
The LLM is instructed to detect and report the candidate's emotional tone each turn, and to adapt its response style accordingly (more reassuring for nervous candidates, energetic for enthusiastic ones).

### Technical Question Generation

When the tech stack is declared, the prompt instructs the LLM to:
- Summarise the declared stack back to confirm accuracy
- Generate 3–5 specific, progressively challenging questions per technology
- Ask one question at a time, waiting for each answer
- Acknowledge answers warmly without grading or revealing correct answers

---

## 🔒 Data Privacy & Security

| Concern | Approach |
|---------|----------|
| **Session data** | Stored in Streamlit `session_state` — cleared when tab closes or session resets |
| **Persistent storage** | `candidates.json` written locally only — never sent to third parties |
| **API key** | Hardcoded in `call_llm()` for local use — in production, use environment variables or a secrets manager |
| **Sensitive fields** | Email and phone collected only for recruitment purposes — not logged elsewhere |
| **GDPR note** | For production deployment, implement encrypted storage, data retention policies, and a consent mechanism |

> ⚠️ `candidates.json` is excluded from Git via `.gitignore` to prevent accidental exposure of candidate data.

---

## ⚠️ Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| LLM skipping metadata block | Added Python-side `infer_stage()` as a reliable fallback |
| Double submission on Enter key | Replaced `st.text_input + st.button` with `st.form + st.form_submit_button` |
| Stage going backwards on rerun | `infer_stage()` only advances stage — never decrements |
| Groq free tier rate limits | Added clear error guidance; architecture supports easy model swapping |
| Sentiment not adapting tone | Added explicit sentiment awareness section to system prompt |
| Candidate data not persisting | `save_candidate()` appends to `candidates.json` on session end |
| API key quota exhaustion | Migrated from Anthropic → Google Gemini → Groq (free, no card needed) |

---

## 🌟 Features Implemented

### Core Requirements ✅
- [x] Streamlit UI with clean, intuitive design
- [x] Greeting with purpose explanation
- [x] Full candidate info collection (7 fields)
- [x] Tech stack declaration
- [x] 3–5 technical questions per technology, asked one at a time
- [x] Multi-turn context handling (full message history sent each call)
- [x] Fallback/redirect for off-topic input
- [x] Exit keyword detection with graceful farewell
- [x] Candidate data saved to `candidates.json`

### Bonus Enhancements ✅
- [x] **Sentiment analysis** — live mood badge (Confident 💪 / Nervous 😰 / Confused 😕 / Enthusiastic 🚀 / Neutral 😐)
- [x] **Sentiment-adaptive responses** — Alex adjusts tone based on detected emotion
- [x] **Sentiment history** — dominant mood saved alongside candidate profile
- [x] **Real-time profile card** — fills in as candidate provides details
- [x] **5-stage visual progress tracker** with done/active/pending states
- [x] **Polished dark UI** — custom CSS, distinctive typography, animated chat bubbles
- [x] **Session reset** — clean restart without refreshing the page

---

## 📦 Dependencies

```
streamlit>=1.35.0
groq>=0.9.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 📄 License

MIT — free to use, modify, and distribute.

---

## 👤 Author

Built as part of the TalentScout AI/ML Internship Assignment.