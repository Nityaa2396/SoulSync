# SoulSync: An Agentic Emotional Intelligence Framework

**One-liner:** A modular, multi-agent system for reflective, ethical, and personalized emotional support.  
**Status:** Week 1 scaffold (MVP-ready foundation).

---

## 🚀 Why SoulSync
Most “AI therapist” projects are a single LLM behind a chat box. SoulSync is a **system**:
- Multi‑agent orchestration (Listener → Cognitive → Mindfulness → Supervisor)
- **Emotional Memory Graphs** tracked over time
- **Reflection loops** (agents self‑evaluate & improve)
- **Safety & Ethics** layer (transparent, non-clinical, escalation ready)
- **Emotions-as-plugins** (anxiety, anger, motivation) for easy extension

---

## 🧭 4‑Week Builder Roadmap

### Week 1 — MVP Agent Loop
**Goal:** Single-user chat with 4 agents and Supervisor merge; session memory; safety checks.
- [ ] Implement `ListenerAgent`, `CognitiveAgent`, `MindfulnessAgent`, `SupervisorAgent`
- [ ] In-memory vector store stub + JSON session store
- [ ] SafetyAgent for risk phrases; transparent disclaimer
- [ ] Streamlit chat UI (local run)
- [ ] Unit tests for agent contracts

**Deliverable:** Local Streamlit app with an end‑to‑end turn.

### Week 2 — Emotional Memory Graphs
**Goal:** Persist states + visualize trends.
- [ ] Sentiment/emotion extraction per message
- [ ] Save to `data/metrics.jsonl`
- [ ] Plot weekly trends (Plotly chart)
- [ ] “Weekly Reflection Summary” auto-generation

**Deliverable:** Trends chart + weekly summary button.

### Week 3 — Reflection & Personalization
**Goal:** Agents rate themselves post‑session and adapt prompts.
- [ ] Reflection prompts & critic scores saved per agent
- [ ] Prompt-weight tuning (e.g., empathy vs. structure)
- [ ] User profile & preferences (tone, goals, topics)
- [ ] Emotions-as-plugins (e.g., `anxiety_agent.py`)

**Deliverable:** Noticeably improved responses over multiple sessions.

### Week 4 — Polish & Deploy
**Goal:** Make it portfolio-ready.
- [ ] README architecture diagram + demo video link
- [ ] Config via `.env` + provider switch (OpenAI/Anthropic/AWS Bedrock)
- [ ] Basic telemetry (token usage, latency)
- [ ] Deploy to Hugging Face Spaces or Render

**Deliverable:** Public demo + clean repo.

---

## 🧩 Architecture (MVP)

```
User ──▶ ListenerAgent ──┐
                         ├─▶ SupervisorAgent ──▶ Response
CognitiveAgent ──────────┤
MindfulnessAgent ────────┘
            │
     SafetyAgent (guard)
            │
   Memory (short/long)
```

- **Agents**: small, single‑purpose modules exposing `plan()` and `respond()`.
- **Supervisor**: merges and moderates outputs; ensures style/tone & ethics.
- **Memory**: JSON + vector embeddings; Week 2 adds graphs & plots.
- **Safety**: explicit non‑clinical disclaimer + keyword/risk detection.

---

## ▶️ Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run src/ui/streamlit_app.py
```

Create `.env` from `.env.example` and add your API keys if using cloud LLMs.

---

## 🧪 Tests

```bash
pytest -q
```

---

## ⚖️ Ethics & Disclaimer

SoulSync is **not** a licensed therapist and does not provide medical advice.  
It supports reflection and wellness practices and can escalate to human resources when risk is detected.

---

## 📂 Repo Layout

```
src/
  agents/ (listener, cognitive, mindfulness, supervisor, safety)
  core/   (llm, memory, reflection, router)
  emotions/ (plugins)
  ui/     (streamlit app)
prompts/  (system & reflection prompts)
data/     (local persistence)
tests/    (unit tests)
```

MIT License.
