import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from src.agents.listener import ListenerAgent
from src.agents.cognitive import CognitiveAgent
from src.agents.mindfulness import MindfulnessAgent
from src.agents.supervisor import SupervisorAgent
from src.agents.safety import safety_check
from src.core.memory import save_session_turn
from src.agents.emotion_tagger import EmotionTaggerAgent
from src.core.memory import save_emotion


st.set_page_config(page_title="SoulSync", page_icon="💠")

# Header / disclaimer
st.title("💠 SoulSync — you're not alone here")
st.caption(
    "I'm here to sit with you and help you feel understood. "
    "I'm not a licensed therapist or crisis resource. "
    "If you're in immediate danger or thinking about self-harm, "
    "please reach out to someone you trust or local emergency services right now."
)

# Initialize session history
if "history" not in st.session_state:
    st.session_state.history = []

# 1. Render previous chat history
for role, msg in st.session_state.history:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(msg if isinstance(msg, str) else str(msg))

# 2. Get new user message
user_text = st.chat_input("What's on your mind?")

tagger = EmotionTaggerAgent()
emo = tagger.tag_latest(user_text)
save_emotion(emo.get("tag","UNKNOWN"), emo.get("summary",""))


# 3. Only run the agent pipeline if user_text is not None / not empty
if user_text:
    # Add user's message to memory and immediately render it
    st.session_state.history.append(("user", user_text))
    with st.chat_message("user"):
        st.write(user_text)

    # Show spinner while generating response
    with st.spinner("💠 SoulSync is thinking with you... you can take a breath here 🌿"):
        # Safety scan (crisis / escalation messaging)
        disclaimer = safety_check(user_text or "")

        # Build short context window from recent chat history
        # We take last ~4 messages (user/assistant pairs) to give the model emotional continuity
        recent_dialog = []
        for role, msg in st.session_state.history[-4:]:
            # Map to OpenAI-style roles
            if role == "user":
                recent_dialog.append(("user", msg))
            else:
                recent_dialog.append(("assistant", msg))

        # Add the new user message at the end (current turn)
        recent_dialog.append(("user", user_text))

        # Call each agent with context
        listener = ListenerAgent().respond_with_context(recent_dialog)
        cognitive = CognitiveAgent().respond_with_context(recent_dialog)
        mindfulness = MindfulnessAgent().respond_with_context(recent_dialog)

        # Merge all drafts into final, context-aware response
        supervisor = SupervisorAgent()
        final = supervisor.merge({
            "listener": listener,
            "cognitive": cognitive,
            "mindfulness": mindfulness
        }, user_text)

    # Show assistant final message
    with st.chat_message("assistant"):
        st.write(final)

    # Add assistant reply to history
    st.session_state.history.append(("assistant", final))

    # Persist this turn to disk
    save_session_turn(user_text, final, {"disclaimer": disclaimer})

    # Re-render whole page to show full convo cleanly without duplicates
    st.rerun()
