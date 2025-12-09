import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from streamlit.components.v1 import html
from dotenv import load_dotenv
import time
from pathlib import Path
import base64
import hashlib
import json

load_dotenv()

from src.agents.listener import ListenerAgent
from src.agents.cognitive import CognitiveAgent
from src.agents.mindfulness import MindfulnessAgent
from src.agents.supervisor import SupervisorAgent
from src.agents.safety import safety_check
from src.agents.emotion_tagger import EmotionTaggerAgent
from src.agents.memory_helper import MemoryHelper
from components.emotion_charts import render_emotion_dashboard

try:
    from src.agents.specialists.family_conflict_agent import FamilyConflictAgent
    FAMILY_AGENT_AVAILABLE = True
except ImportError:
    FAMILY_AGENT_AVAILABLE = False

from src.core.memory import save_session_turn, save_emotion, load_sessions, load_emotions, export_user_data


# ══════════════════════════════════════════════════════════════
# AUTHENTICATION SYSTEM
# ══════════════════════════════════════════════════════════════

class SimpleAuth:
    """Simple authentication system with JSON storage"""
    
    def __init__(self):
        self.users_file = Path(__file__).parent.parent.parent / "data" / "users.json"
        self.users_file.parent.mkdir(exist_ok=True)
        self._load_users()
    
    def _load_users(self):
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {}
            self._save_users()
    
    def _save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email: str, password: str) -> tuple[bool, str]:
        email = email.strip().lower()
        
        if '@' not in email:
            return False, "Please enter a valid email address"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        if email in self.users:
            return False, "Email already registered. Please log in."
        
        self.users[email] = {
            "password_hash": self._hash_password(password),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_users()
        return True, "Account created successfully!"
    
    def login_user(self, email: str, password: str) -> tuple[bool, str]:
        email = email.strip().lower()
        if email not in self.users:
            return False, "Invalid email or password"
        
        password_hash = self._hash_password(password)
        if self.users[email]["password_hash"] != password_hash:
            return False, "Invalid email or password"
        
        return True, "Login successful!"
    
    def user_exists(self, email: str) -> bool:
        return email.strip().lower() in self.users


auth = SimpleAuth()


# ══════════════════════════════════════════════════════════════
# AUTO-SCROLL HELPER
# ══════════════════════════════════════════════════════════════

def scroll_to_id(element_id: str, nonce: int):
    """
    Works across Streamlit versions that don't support key= in components.html.
    We force re-execution by changing the HTML content using `nonce`.
    """
    html(
        f"""
        <!-- nonce:{nonce} -->
        <script>
        (function scroll_{nonce}() {{
          const id = "{element_id}";
          const maxTries = 120;
          let tries = 0;

          function attempt() {{
            tries++;
            const doc = window.parent.document;
            const el = doc.getElementById(id);

            if (!el) {{
              if (tries < maxTries) requestAnimationFrame(attempt);
              return;
            }}

            el.scrollIntoView({{ behavior: "smooth", block: "start" }});

            // focus first input after scroll
            setTimeout(() => {{
              const input =
                doc.querySelector('input[type="email"]') ||
                doc.querySelector('input[aria-label="Email"]') ||
                doc.querySelector('input');
              if (input) input.focus();
            }}, 350);
          }}

          requestAnimationFrame(attempt);
        }})();
        </script>
        """,
        height=0,
    )

# ══════════════════════════════════════════════════════════════
# CSS LOADER & HERO LOGO
# ══════════════════════════════════════════════════════════════

def load_css(css_file: str):
    """Load CSS file from src/ui/css/ directory"""
    css_path = Path(__file__).parent / "css" / css_file
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found: {css_file}")


def inject_hero_logo_css():
    """
    Reads src/ui/assets/banner1.png, encodes to base64, injects CSS for .hero-section background
    """
    image_path = Path(__file__).parent / "assets" / "banner1.png"
    if not image_path.exists():
        # Try fallback to ss-logo.png
        image_path = Path(__file__).parent / "assets" / "ss-logo.png"
        if not image_path.exists():
            return

    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    css = f"""
    <style>
    .hero-section {{
      position: relative !important;
      width: 100% !important;
      min-height: 45vh !important;
      display: flex !important;
      flex-direction: column !important;
      justify-content: center !important;
      align-items: center !important;
      text-align: center !important;
      padding: 8rem 2rem !important;
      box-sizing: border-box !important;

      background:
        radial-gradient(
          circle at center,
          rgba(15, 23, 42, 0.20),
          rgba(15, 23, 42, 0.70)
        ),
        url("data:image/png;base64,{data}") center center / cover no-repeat !important;
    }}

    .hero-section .hero-title {{
      color: #e5f2ff !important;
    }}

    .hero-section .hero-subtitle,
    .hero-section .hero-tagline {{
      color: #cbd5f5 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="SoulSync",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"  # ✅ Start sidebar CLOSED
)

load_css("styles.css")

    # ═══════════════════════════════════════════════════════
    # MOBILE CSS FIXES
    # ═══════════════════════════════════════════════════════

# ✅ STRONGER MOBILE CSS
st.markdown("""
<style>
    /* Force hide ALL sidebar elements on mobile */
    @media (max-width: 768px) {
        /* Nuclear option - hide everything in sidebar initially */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Only show when explicitly opened */
        section[data-testid="stSidebar"][aria-expanded="true"] {
            display: block !important;
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            height: 100vh !important;
            z-index: 999999 !important;
            background: white !important;
        }
        
        /* Hide sidebar toggle text */
        button[kind="header"] p {
            display: none !important;
        }
        
        /* Force scroll to top */
        .main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Buttons must be touch-friendly */
        button, .stButton button {
            min-height: 48px !important;
            font-size: 16px !important;
            padding: 0.75rem 1rem !important;
        }
        
        /* Remove any top padding/margin */
        section.main {
            padding-top: 0 !important;
        }
        
        .element-container {
            margin-top: 0 !important;
        }
    }
    
    /* Force immediate scroll on page load */
    html, body {
        scroll-behavior: auto !important;
    }
</style>

<script>
    // Force scroll to top immediately
    if (window.parent.document.querySelector('section.main')) {
        window.parent.document.querySelector('section.main').scrollTop = 0;
    }
</script>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ROOM CONFIGS
# ══════════════════════════════════════════════════════════════

THERAPY_ROOMS = {
    "emotional_wellness": {
        "title": "Emotional Wellness",
        "icon": "🌿",
        "description": "Support for depression, anxiety, loneliness, and daily stress",
        "agent_config": {"listener_weight": 0.5, "cognitive_weight": 0.3, "mindfulness_weight": 0.2},
        "prompt_style": "empathetic",
        "status": "ready"
    },
    "relationship_issues": {
        "title": "Relationship Support",
        "icon": "💝",
        "description": "Navigate heartbreak, conflict, and communication challenges",
        "agent_config": {"listener_weight": 0.4, "cognitive_weight": 0.4, "mindfulness_weight": 0.2},
        "prompt_style": "relationship_focused",
        "status": "ready"
    },
    "family_dynamics": {
        "title": "Family Dynamics",
        "icon": "🏠",
        "description": "Parent conflicts, sibling relationships, and family tension",
        "agent_config": {"listener_weight": 0.4, "cognitive_weight": 0.4, "mindfulness_weight": 0.2},
        "prompt_style": "systemic",
        "status": "coming_soon"
    },
    "loss_bereavement": {
        "title": "Loss & Grief",
        "icon": "🕊️",
        "description": "Compassionate support through death, loss, and endings",
        "agent_config": {"listener_weight": 0.7, "cognitive_weight": 0.1, "mindfulness_weight": 0.2},
        "prompt_style": "grief_focused",
        "status": "coming_soon"
    },
    "trauma_recovery": {
        "title": "Trauma Support",
        "icon": "🛡️",
        "description": "Gentle, trauma-informed care for healing from past harm",
        "agent_config": {"listener_weight": 0.6, "cognitive_weight": 0.2, "mindfulness_weight": 0.2},
        "prompt_style": "trauma_informed",
        "status": "coming_soon"
    },
    "crisis_support": {
        "title": "Crisis Support",
        "icon": "🆘",
        "description": "Immediate support for urgent distress and safety concerns",
        "agent_config": {"listener_weight": 0.6, "cognitive_weight": 0.3, "mindfulness_weight": 0.1},
        "prompt_style": "crisis",
        "status": "coming_soon"
    }
}


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def generate_chat_id():
    return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]


def generate_chat_title(first_message: str, max_words: int = 4) -> str:
    text = first_message.strip().lower()
    title_patterns = {
        ("boyfriend", "cheated"): "Relationship betrayal",
        ("broke up", "breakup"): "Recent breakup",
        ("no friends", "alone"): "Social isolation",
        ("bully", "bullying"): "School bullying",
        ("everyone hates"): "Feeling rejected",
        ("depressed", "depression"): "Depression support",
        ("heartbroken", "heartbreak"): "Heartbreak"
    }
    for keywords, title in title_patterns.items():
        if any(kw in text for kw in keywords):
            return title
    filler = {"i", "im", "i'm", "my", "me", "the", "a", "an", "and", "but", "so", "very", "really", "just"}
    words = [w for w in text.split() if w not in filler and len(w) > 2]
    if words:
        return " ".join(word.capitalize() for word in words[:max_words])
    return "New conversation"


def load_chat_history(user_id: str, chat_id: str) -> list:
    try:
        sessions = load_sessions(user_id, limit=1000)
        chat_messages = []
        for session in sessions:
            if session.get("chat_id") == chat_id:
                if session.get("user"):
                    chat_messages.append(("user", session["user"]))
                if session.get("agent"):
                    chat_messages.append(("assistant", session["agent"]))
        return chat_messages
    except:
        return []


def get_all_chats(user_id: str) -> list:
    try:
        sessions = load_sessions(user_id, limit=1000)
        chats = {}
        for session in sessions:
            chat_id = session.get("chat_id", "default")
            if chat_id not in chats:
                chats[chat_id] = {
                    "chat_id": chat_id,
                    "title": session.get("chat_title", "Untitled"),
                    "timestamp": session.get("ts", time.time()),
                    "room_type": session.get("room_type", "emotional_wellness")
                }
        return sorted(chats.values(), key=lambda x: x["timestamp"], reverse=True)
    except:
        return []


def extract_context_from_response(user_message: str):
    msg_lower = user_message.lower()
    if any(word in msg_lower for word in ["school", "class", "teacher", "homework"]):
        st.session_state.user_setting = "school"
    elif any(word in msg_lower for word in ["work", "job", "boss", "office", "colleague"]):
        st.session_state.user_setting = "work"
    if any(word in msg_lower for word in ["school", "class", "homework", "teacher"]):
        st.session_state.user_age_range = "teen"
    elif any(word in msg_lower for word in ["college", "university"]):
        st.session_state.user_age_range = "young_adult"
    elif any(word in msg_lower for word in ["work", "job", "career"]):
        st.session_state.user_age_range = "adult"
    if any(word in msg_lower for word in ["friend", "mom", "dad", "sister", "brother", "counselor"]):
        st.session_state.has_support = True
    elif "no one" in msg_lower or "alone" in msg_lower:
        st.session_state.has_support = False


# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════

for key, default in [
    ("user_id", None),
    ("current_chat_id", None),
    ("current_chat_title", "New conversation"),
    ("history", []),
    ("room_type", None),
    ("room_selected", False),
    ("user_setting", None),
    ("user_age_range", None),
    ("has_support", None),
    ("saved_insights", []),
    ("pending_insight_save", None),
    ("show_login_form", False),
    ("show_signup_form", False),
    ("scroll_target", None),
    ("scroll_nonce", 0),
    ("authenticated", False),
    ("show_dashboard", False),
    ("scroll_to_top", False)
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════
# LOGIN / LANDING PAGE
# ══════════════════════════════════════════════════════════════

if not st.session_state.get("authenticated", False):
    load_css("landing.css")
    inject_hero_logo_css()

    if st.session_state.get("scroll_to_top", False):
        st.markdown("""
        <script>
            window.parent.document.querySelector('section.main').scrollTo({
                top: 0,
                behavior: 'instant'
            });
        </script>
        """, unsafe_allow_html=True)
        st.session_state.scroll_to_top = False


    # Header
    col1, col2, col3 = st.columns([3, 6, 3])
    with col1:
        st.markdown(
            '<p style="font-size: 1.8rem; font-weight: 700; color: #000000; margin: 0; padding: 1rem 0;">Soulsync</p>',
            unsafe_allow_html=True
        )

    with col3:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Log In", key="header_login", type="secondary"):
                st.session_state.show_login_form = True
                st.session_state.show_signup_form = False
                st.session_state.scroll_target = "auth-section"
                st.session_state.scroll_nonce += 1
                st.rerun()
        with c2:
            if st.button("Sign Up", key="header_signup", type="secondary"):
                st.session_state.show_signup_form = True
                st.session_state.show_login_form = False
                st.session_state.scroll_target = "auth-section"
                st.session_state.scroll_nonce += 1
                st.rerun()

    st.markdown('<hr style="margin: 0; border: 0; border-top: 1px solid #e5e7eb;">', unsafe_allow_html=True)

    # Hero
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">Emotional support,<br>made accessible</h1>
                <p class="hero-subtitle">AI-powered compassionate care, available 24/7</p>
                <p class="hero-tagline">💙 Free, private, and judgment-free</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Trust section
    st.markdown(
        """
        <div style="background: white; padding: 4rem 2rem; text-align: center;">
            <h2 style="font-size: 2rem; font-weight: 600; color: #1f2937; margin: 0;">
                A safe space for your well-being
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Anchor for scroll
    st.markdown('<div id="auth-section"></div>', unsafe_allow_html=True)

    # AUTH AREA (login/signup)
    if st.session_state.get("show_login_form") or st.session_state.get("show_signup_form"):
        _, mid, _ = st.columns([1, 1.25, 1])
        with mid:
            st.markdown("## 🔐 Access SoulSync")

            if st.session_state.get("show_login_form"):
                st.markdown("### Welcome back")

                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="you@example.com", key="login_email")
                    password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_pass")

                    c1, c2 = st.columns(2)
                    with c1:
                        submitted = st.form_submit_button("Log In", use_container_width=True, type="primary")
                    with c2:
                        cancel = st.form_submit_button("Cancel", use_container_width=True, type="secondary")

                    if submitted:
                        if email.strip() and password:
                            success, message = auth.login_user(email, password)
                            if success:
                                st.session_state.user_id = email.strip().lower()
                                st.session_state.authenticated = True
                                st.session_state.show_login_form = False
                                st.session_state.show_signup_form = False
                                st.session_state.scroll_to_top = True
                                st.rerun()
                            else:
                                st.error("❌ " + message)
                        else:
                            st.warning("⚠️ Please enter both email and password")

                    if cancel:
                        st.session_state.show_login_form = False
                        st.rerun()

                st.caption("Don't have an account?")
                if st.button("Create Account", key="switch_to_signup", use_container_width=True):
                    st.session_state.show_login_form = False
                    st.session_state.show_signup_form = True
                    st.session_state.scroll_target = "auth-section"
                    st.session_state.scroll_nonce += 1
                    st.rerun()

            if st.session_state.get("show_signup_form"):
                st.markdown("### Create your SoulSync account")

                with st.form("signup_form"):
                    email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                    password = st.text_input("Password", placeholder="Choose a password (min 6 characters)", type="password", key="signup_pass")
                    confirm_password = st.text_input("Confirm Password", placeholder="Re-enter your password", type="password", key="signup_confirm")

                    c1, c2 = st.columns(2)
                    with c1:
                        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                    with c2:
                        cancel = st.form_submit_button("Cancel", use_container_width=True, type="secondary")

                    if submitted:
                        if email.strip() and password and confirm_password:
                            if password != confirm_password:
                                st.error("❌ Passwords don't match!")
                            else:
                                success, message = auth.register_user(email, password)
                                if success:
                                    st.success("✅ Account created! Please log in.")
                                    time.sleep(1)
                                    st.session_state.show_signup_form = False
                                    st.session_state.show_login_form = True
                                    st.session_state.scroll_to_top = True
                                    st.session_state.scroll_target = "auth-section"
                                    st.session_state.scroll_nonce += 1
                                    st.rerun()
                                else:
                                    st.error("❌ " + message)
                        else:
                            st.warning("⚠️ Please fill in all fields")

                    if cancel:
                        st.session_state.show_signup_form = False
                        st.rerun()

                st.caption("Already have an account?")
                if st.button("Log In", key="switch_to_login", use_container_width=True):
                    st.session_state.show_signup_form = False
                    st.session_state.show_login_form = True
                    st.session_state.scroll_target = "auth-section"
                    st.session_state.scroll_nonce += 1
                    st.rerun()

    # ✅ Do scroll AFTER the target exists
    if st.session_state.get("scroll_target"):
        scroll_to_id(st.session_state.scroll_target, st.session_state.scroll_nonce)
        st.session_state.scroll_target = None

    st.info("💡 **Not a replacement for licensed therapy.** If you're in crisis, contact emergency services or call 988.")
    st.stop()


# ══════════════════════════════════════════════════════════════
# AUTHENTICATED - STYLE NATIVE SIDEBAR BUTTON
# ══════════════════════════════════════════════════════════════

# ✅ Use Streamlit's NATIVE sidebar toggle (no custom JavaScript)
st.markdown("""
<style>
    /* Position Streamlit's built-in toggle button on LEFT */
    button[kind="header"] {
        position: fixed !important;
        left: 1rem !important;
        top: 1rem !important;
        z-index: 1001 !important;
        background: white !important;
        border: 2px solid #76b2bf !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    button[kind="header"]:hover {
        background: #76b2bf !important;
        color: white !important;
    }
    
    /* Hide the "Toggle sidebar" text, show only icon */
    button[kind="header"] p {
        display: none !important;
    }
    
    /* Style the sidebar */
    section[data-testid="stSidebar"] {
        background: #f9fafb !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ROOM SELECTION
# ══════════════════════════════════════════════════════════════

if not st.session_state.room_selected:
    st.markdown('<div class="logo-header">💠 SoulSync</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Choose Your Support Space</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Select the type of support that resonates with you</div>', unsafe_allow_html=True)
    
    cols = st.columns(2)
    for idx, (room_key, room) in enumerate(THERAPY_ROOMS.items()):
        with cols[idx % 2]:
            st.markdown(f'<h3 style="color: #1f2937 !important; font-weight: 600;">{room["icon"]} {room["title"]}</h3>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #4b5563 !important;">{room["description"]}</p>', unsafe_allow_html=True)
            
            if room['status'] == 'ready':
                st.success("✓ Available Now", icon="✅")
                if st.button(f"Enter {room['title']}", key=room_key, use_container_width=True):
                    st.session_state.room_type = room_key
                    st.session_state.room_selected = True
                    st.session_state.current_chat_id = generate_chat_id()
                    st.rerun()
            else:
                st.warning("Coming Soon", icon="🚧")
                st.button("In Development", key=room_key, disabled=True, use_container_width=True)
            st.write("")
    
    st.info("💡 Additional specialized support spaces are being developed with therapeutic expertise.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# EMOTIONAL DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════

if st.session_state.get("show_dashboard", False):
    render_emotion_dashboard(st.session_state.user_id)
    
    # Back button centered
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("← Back to Chat", use_container_width=True):
            st.session_state.show_dashboard = False
            st.rerun()
    
    st.stop()  # Don't show chat interface


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 💠 SoulSync")
    st.caption(f"**{st.session_state.user_id}**")
    st.divider()
    
    current_room = THERAPY_ROOMS[st.session_state.room_type]
    st.markdown(f"**{current_room['icon']} {current_room['title']}**")
    st.caption(current_room['description'])

    
    
    if st.button("🔄 Change Room", use_container_width=True):
        st.session_state.room_selected = False
        st.session_state.history = []
        st.rerun()
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_chat_id = generate_chat_id()
        st.session_state.current_chat_title = "New conversation"
        st.session_state.history = []
        st.rerun()
    
    st.divider()
    st.markdown("**Recent Chats**")
    
    chats = [c for c in get_all_chats(st.session_state.user_id) 
             if c.get("room_type") == st.session_state.room_type][:10]
    
    if chats:
        for chat in chats:
            if chat["chat_id"] == st.session_state.current_chat_id:
                st.markdown(f"**▸ {chat['title']}**")
            else:
                if st.button(chat['title'], key=f"c_{chat['chat_id']}", use_container_width=True):
                    st.session_state.current_chat_id = chat["chat_id"]
                    st.session_state.current_chat_title = chat["title"]
                    st.session_state.history = load_chat_history(st.session_state.user_id, chat["chat_id"])
                    st.rerun()
    else:
        st.caption("No chats yet")
    
    st.divider()
    st.markdown("**💭 Saved Insights**")
    
    saved_insights = st.session_state.get("saved_insights", [])
    if saved_insights:
        for idx, insight_data in enumerate(saved_insights[-5:]):
            with st.expander(f"Insight {len(saved_insights) - idx}", expanded=False):
                st.caption(insight_data["insight"])
                timestamp = time.strftime("%b %d, %H:%M", time.localtime(insight_data["timestamp"]))
                st.caption(f"🕐 {timestamp}")
    else:
        st.caption("No insights saved yet")
    
    st.divider()
    if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ══════════════════════════════════════════════════════════════
# CHAT
# ══════════════════════════════════════════════════════════════

st.title(f"{current_room['icon']} {st.session_state.current_chat_title}")
st.caption(current_room['description'])

if st.session_state.room_type == "crisis_support":
    st.error("⚠️ **Crisis Support**: Not a crisis counselor. **In danger?** Call 988 or 911")
else:
    st.caption("💙 Here to help you feel understood. Not a replacement for therapy.")

st.divider()

for role, msg in st.session_state.history:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(msg)

user_text = st.chat_input("What's on your mind?")

if user_text:
    if st.session_state.get("pending_insight_save"):
        if user_text.lower().strip() in ["yes", "y", "sure", "ok", "okay", "yeah"]:
            insight = st.session_state.pending_insight_save
            st.session_state.saved_insights.append({
                "insight": insight,
                "timestamp": time.time()
            })
            st.session_state.pending_insight_save = None
            
            with st.chat_message("user"):
                st.write(user_text)
            with st.chat_message("assistant"):
                st.write("✓ Saved to your journal. You can review it anytime in the sidebar.")
            
            st.session_state.history.append(("user", user_text))
            st.session_state.history.append(("assistant", "✓ Saved to your journal. You can review it anytime in the sidebar."))
            st.rerun()
            
        elif user_text.lower().strip() in ["no", "n", "nah", "nope"]:
            st.session_state.pending_insight_save = None
    
    extract_context_from_response(user_text)
    
    st.session_state.history.append(("user", user_text))
    with st.chat_message("user"):
        st.write(user_text)
    
    if len(st.session_state.history) == 1:
        st.session_state.current_chat_title = generate_chat_title(user_text)
    
    with st.spinner("💭 Thinking..."):
        tagger = EmotionTaggerAgent()
        emo = tagger.tag_latest(user_text)
        emotion_tag = emo.get("tag", "UNKNOWN")
        
        save_emotion(
            user_id=st.session_state.user_id,
            emotion=emotion_tag,
            intensity=7,
            message_preview=user_text[:100]
        )
        
        recent_dialog = st.session_state.history[-6:]
        room_config = current_room["agent_config"]
        
        if st.session_state.room_type == "family_dynamics" and FAMILY_AGENT_AVAILABLE:
            listener = FamilyConflictAgent().respond_with_context(recent_dialog)
        else:
            listener = ListenerAgent().respond_with_context(recent_dialog)
        
        cognitive = CognitiveAgent().respond_with_context(recent_dialog)
        mindfulness = MindfulnessAgent().respond_with_context(recent_dialog)
        
        context = {
            "setting": st.session_state.get("user_setting"),
            "age_range": st.session_state.get("user_age_range"),
            "has_support": st.session_state.get("has_support"),
        }
        
        supervisor = SupervisorAgent()
        final = supervisor.merge_with_safety_first(
            agent_outputs={
                "listener": (listener, room_config.get("listener_weight", 0.5)),
                "cognitive": (cognitive, room_config.get("cognitive_weight", 0.3)),
                "mindfulness": (mindfulness, room_config.get("mindfulness_weight", 0.2))
            },
            user_message=user_text,
            emotion_tag=emotion_tag,
            room_style=current_room["prompt_style"],
            context=context
        )
    
    turn_number = len(st.session_state.history) // 2
    
    if MemoryHelper.should_offer_save(user_text, final, turn_number):
        insight = MemoryHelper.extract_insight(final, user_text)
        save_offer = MemoryHelper.generate_save_offer(insight)
        final = final + save_offer
        st.session_state.pending_insight_save = insight
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        displayed = ""
        for char in final:
            displayed += char
            placeholder.markdown(displayed + "▌")
            time.sleep(0.015)
        placeholder.markdown(displayed)
    
    st.session_state.history.append(("assistant", final))
    
    save_session_turn(
        st.session_state.user_id,
        user_text, 
        final,
        chat_id=st.session_state.current_chat_id,
        emotion=emo.get("tag"),
        room_type=st.session_state.room_type,
        chat_title=st.session_state.current_chat_title
    )
    
    st.rerun()