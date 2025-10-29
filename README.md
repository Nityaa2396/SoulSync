# 💠 SoulSync: An Agentic Emotional Intelligence Framework

**One-liner:** A modular, multi-agent system for reflective, ethical, and personalized emotional support.  
**Status:** Week 2 — Context memory, emotional tagging, and journaling sidebar implemented.

---

## 🚀 Why SoulSync
Most “AI therapist” projects are just a single LLM behind a chat box.  
SoulSync is designed as a **system** — an evolving emotional-intelligence framework.

- 🤝 **Multi-agent orchestration** — Listener → Cognitive → Mindfulness → Supervisor  
- 🧠 **Emotional Memory Graphs** tracked over time  
- 🔄 **Reflection loops** — agents self-evaluate & adapt  
- 🛡 **Safety & Ethics layer** — transparent, non-clinical, escalation-ready  
- 💎 **Emotions-as-plugins** — anxiety, anger, motivation → easily extendable modules  

---

## 🔹 Current Implementation (Week 2)

SoulSync now runs as a local **Streamlit** web app that provides gentle, emotionally-aware conversation and tracks reflections privately on your device.

### ✨ Features Live
- 🧠 **Multi-Agent System:** Listener, Cognitive, Mindfulness, Supervisor  
- 💬 **Contextual Memory:** last few conversation turns remembered  
- 💗 **Emotional Tagger:** detects & logs themes (loneliness, shame, panic, anger etc.)  
- 🧾 **Session Logging:** every turn stored locally in `data/sessions.jsonl`  
- 🌿 **Safety Layer:** detects crisis phrases and adds non-clinical disclaimer  
- 📖 **Sidebar Journal:** view recent reflections inside the UI  
- 💾 **Local Only Memory:** data stays on your machine — never shared or used to train others  

### 🖥 UI Preview
💠 SoulSync — you're not alone here
[ chat interface ]
📖 Sidebar — shows recent reflections


### 💬 Example Conversation
> **User:** I don't have many friends; people just tolerate me.  
> **SoulSync:**  
> It sounds like you’ve been feeling left out and unwanted lately.  
> That can really hurt — when you care deeply but worry others don’t feel the same. 💗  
> It makes sense you’d wonder why people act that way; sometimes loneliness carries self-blame too.  
> If it feels okay, we can talk about which part of that feels heaviest right now. 🤍  

### ⚖️ Ethical Note
SoulSync never claims to be a therapist.  
It reflects, listens, and supports gently.  
If crisis language is detected, a clear message encourages the user to reach out to real human help.

---

## 🧭 4-Week Builder Roadmap

### Week 1 — MVP Agent Loop
**Goal:** single-user chat with 4 agents and Supervisor merge; session memory; safety checks.
- [x] Implement `ListenerAgent`, `CognitiveAgent`, `MindfulnessAgent`, `SupervisorAgent`
- [x] In-memory JSON session store
- [x] Safety Agent for risk phrases + disclaimer
- [x] Streamlit chat UI (local run)
- [x] Basic unit tests for agent contracts  
**Deliverable:** Local Streamlit app with end-to-end conversation.

### Week 2 — Emotional Memory Graphs
**Goal:** Persist emotions + visualize trends.
- [x] Emotion tagging per message  
- [x] Save to `data/emotions.jsonl`  
- [ ] Plot weekly trends (Plotly chart)  
- [ ] Auto-generate “Weekly Reflection Summary”  
**Deliverable:** Trend chart + summary button (coming soon).

### Week 3 — Reflection & Personalization
**Goal:** Agents self-rate and adapt prompts.
- [ ] Reflection prompts & critic scores per agent  
- [ ] Prompt-weight tuning (e.g., empathy vs structure)  
- [ ] User profile & preferences (tone, goals, topics)  
- [ ] Emotions-as-plugins (e.g. `anxiety_agent.py`)  
**Deliverable:** Improved responses over sessions.

### Week 4 — Polish & Deploy
**Goal:** Portfolio-ready demo.
- [ ] README diagram + video link  
- [ ] Config via `.env` + provider switch (OpenAI/Anthropic/Bedrock)  
- [ ] Basic telemetry (token usage, latency)  
- [ ] Deploy to Hugging Face Spaces or Render  
**Deliverable:** Public demo + clean repo.

---

## 🧩 Architecture (MVP)

User ──▶ ListenerAgent ──┐
├─▶ SupervisorAgent ──▶ Response
CognitiveAgent ──────────┤
MindfulnessAgent ────────┘
│
SafetyAgent (guard)
│
Memory (short/long)


- **Agents:** small single-purpose modules exposing `respond()`  
- **Supervisor:** merges and moderates outputs for style & safety  
- **Memory:** JSON persistence; Week 2 adds emotion graphing  
- **Safety:** keyword detection + explicit non-clinical disclaimer  

---

## ▶️ Quickstart

``bash
# create & activate env
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
pip install openai

# run the Streamlit app
streamlit run src/ui/streamlit_app.py


- **Agents:** small single-purpose modules exposing `respond()`  
- **Supervisor:** merges and moderates outputs for style & safety  
- **Memory:** JSON persistence; Week 2 adds emotion graphing  
- **Safety:** keyword detection + explicit non-clinical disclaimer  

---

## ▶️ Quickstart

``bash
# create & activate env
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
pip install openai

# run the Streamlit app
streamlit run src/ui/streamlit_app.py

Create a .env file from .env.example and add your API key:
PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

🧪 Tests
pytest -q

⚖️ Ethics & Disclaimer

SoulSync is not a licensed therapist and does not provide medical advice.
It supports reflection and well-being but cannot replace professional care.
If you ever feel unsafe or in crisis, please contact a trusted person or local emergency services.

📂 Repo Layout
src/
  agents/        (listener, cognitive, mindfulness, supervisor, safety)
  core/          (llm, memory, router)
  ui/            (streamlit app)
  prompts/       (system and reflection prompts)
  data/             (local logs and emotions)
  tests/            (unit tests)


MIT License © 2025


---

✅ **What this gives you:**
- A clear top-section for **recruiters/investors** (“Why SoulSync”)
- A “Current Implementation” for **demo viewers**
- A concrete roadmap for **technical credibility**
- A short example chat that *feels real and human*
- Clean quickstart instructions for anyone cloning the repo

---
