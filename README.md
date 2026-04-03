# 🎯 TalentScout Hiring Assistant

An AI-powered chatbot that conducts initial candidate screening for technology roles — built with **Streamlit**.

---

## 📌 Project Overview

TalentScout Hiring Assistant is a conversational AI that:

- Greets candidates and explains the screening process
- Collects key personal & professional information (name, email, phone, experience, desired role, location, tech stack)
- Generates **3–5 tailored technical questions** per declared technology
- Maintains coherent multi-turn conversation context
- Ends gracefully on exit keywords or after wrap-up
- Displays a real-time **Candidate Profile** card as info is collected
- Shows a **stage progress tracker** (Greeting → Personal Info → Tech Stack → Tech Questions → Wrap-up)

---

## 🗂️ Repository Structure

```
talentscout/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com/)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/talentscout-hiring-assistant.git
cd talentscout-hiring-assistant

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."   # Windows: set ANTHROPIC_API_KEY=sk-ant-...

# 5. Run the app
streamlit run app.py
```

The app will open at **http://localhost:8501** in your browser.

---

## 🚀 Usage Guide

1. The chatbot **automatically greets** you when the page loads — no action needed.
2. **Respond naturally** in the text box at the bottom and press **Send** or hit Enter.
3. Watch the **progress pills** at the top update as you move through stages.
4. Your **Candidate Profile card** fills in automatically as information is collected.
5. Type `bye`, `exit`, `quit`, `done`, or `end` at any time to gracefully conclude the session.
6. After wrap-up, click **Start a New Session** to reset.

---

## 🛠️ Technical Details

| Item | Detail |
|------|--------|
| **Language** | Python 3.9+ |
| **Frontend** | Streamlit 1.35+ |
| **LLM** | Anthropic Claude claude-sonnet-4-20250514 |
| **SDK** | `anthropic` Python SDK |
| **Styling** | Custom CSS with Google Fonts (DM Serif Display, DM Mono, DM Sans) |
| **State** | Streamlit `session_state` (in-memory, no persistence) |

### Architecture

```
User Input
    │
    ▼
Streamlit UI (app.py)
    │  ┌─────────────────────────────┐
    ├─►│  End-keyword detector        │──► Farewell + end screen
    │  └─────────────────────────────┘
    │
    ▼
Anthropic Messages API
    │   System prompt (SYSTEM_PROMPT constant)
    │   Full conversation history (messages list)
    │
    ▼
Claude claude-sonnet-4-20250514 response
    │
    ├─► Hidden <!--META:{...}--> block parsed for stage + collected fields
    └─► Cleaned text rendered as chat bubble
```

---

## ✍️ Prompt Design

### System Prompt Strategy

The system prompt (`SYSTEM_PROMPT` in `app.py`) uses three key techniques:

1. **Staged flow enforcement** — The prompt explicitly lists four ordered stages (Greeting → Personal Info → Tech Stack → Tech Questions → Wrap-up) and instructs Claude to follow them strictly, preventing the model from jumping ahead or going off-topic.

2. **Metadata injection** — Every reply must end with a hidden HTML comment containing a JSON object: `<!--META:{"stage":"...","collected":{...}}-->`. This lets the Python layer track progress and populate the profile card without any extra API calls.

3. **Guard rails** — Explicit rules prevent topic deviation, sensitive data leakage, and reward encouragement without revealing correct answers.

### Technical Question Generation

When the tech stack is declared, the prompt instructs Claude to:
- Reflect the stack back to confirm accuracy
- Generate questions that are specific and progressively challenging
- Ask one question at a time, waiting for each answer
- Acknowledge answers warmly without grading them

---

## 🔒 Data Privacy

- **No persistence** — all data lives in Streamlit's `session_state` and is lost when the browser tab closes or the session resets.
- **No logging** — candidate data is not written to disk or sent anywhere beyond the Anthropic API call.
- **API key** — loaded from environment variables only; never hard-coded.
- For production use, consider: encrypted storage, GDPR-compliant data handling, and access controls.

---

## ⚠️ Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Tracking conversation stage without extra API calls | Embedded hidden JSON metadata in every LLM response |
| Profile card populating incrementally | Merge strategy: only overwrite collected fields if the new value is non-empty |
| Preventing topic drift | Strict system prompt rules + redirect instruction |
| Auto-starting conversation | Seeded first turn in `session_state` initialisation block |
| Clean display vs raw API content | `clean_display()` strips the `<!--META:...-->` comment before rendering |

---

## 🌟 Optional Enhancements (Implemented)

- **Real-time profile card** — fills in as the candidate provides details
- **Stage progress tracker** — visual pills showing current position in the flow
- **Polished dark UI** — custom CSS with distinctive typography and colour palette
- **Session reset** — "Start a New Session" button on the end screen

---

## 📄 License

MIT — free to use, modify, and distribute.