"""Green Design Assistant — Streamlit frontend.

Works with the existing backend.py, which exports a compiled LangGraph
`chatbot` with a messages state and thread_id-based checkpointer.
"""

import uuid

import streamlit as st
from langchain_core.messages import HumanMessage

from backend import chatbot


st.set_page_config(
    page_title="Learn Green Design with Prithiv",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# The CSS styles only the Streamlit interface; no external assets or packages.
st.markdown(
    """
    <style>
    :root {
        --bg: #0a1511;
        --sidebar: #0e1f18;
        --surface: #14271d;
        --surface-raised: #1b3327;
        --surface-hover: #254333;
        --accent: #77dfa3;
        --accent-hover: #a0efbd;
        --text: #eef8f0;
        --muted: #b4cabc;
        --border: #335342;
    }

    /* Dark foundation. The Streamlit config also uses base=dark, so native
       widgets and controls agree with the custom CSS. */
    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: var(--bg) !important;
        color: var(--text) !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stMainBlockContainer"] {
        max-width: 970px;
        padding-top: 2rem;
        padding-bottom: 7rem;
    }
    [data-testid="stMain"] p,
    [data-testid="stMain"] li,
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 { color: var(--text); }

    /* Sidebar and conversation navigation */
    section[data-testid="stSidebar"] {
        background: var(--sidebar) !important;
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--text);
    }
    section[data-testid="stSidebar"] .stButton button {
        background: #1a3125 !important;
        color: var(--text) !important;
        border: 1px solid #3d5e49 !important;
        border-radius: 12px;
        text-align: left;
        justify-content: flex-start;
        padding: 0.72rem 0.9rem;
        transition: background 120ms ease, border-color 120ms ease;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: var(--surface-hover) !important;
        border-color: var(--accent) !important;
    }
    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: var(--accent) !important;
        color: #092116 !important;
        border-color: var(--accent) !important;
        font-weight: 750;
    }
    section[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
        background: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
        color: #092116 !important;
    }
    section[data-testid="stSidebar"] .stButton button p,
    section[data-testid="stSidebar"] .stButton button span {
        color: inherit !important;
    }
    .brand { padding: 0.35rem 0.2rem 1.15rem; }
    .brand-mark {
        display: inline-grid;
        place-items: center;
        width: 43px;
        height: 43px;
        background: #244b36;
        border: 1px solid #3c7651;
        border-radius: 13px;
        font-size: 1.4rem;
        vertical-align: middle;
        margin-right: 0.55rem;
    }
    .brand-name {
        color: var(--text);
        font-size: 1.2rem;
        font-weight: 780;
        letter-spacing: -0.035em;
        vertical-align: middle;
    }
    .brand-tagline {
        color: var(--muted);
        font-size: 0.86rem;
        margin: 0.75rem 0 0;
    }
    .sidebar-heading {
        font-size: 0.69rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        color: var(--muted);
        margin: 1.3rem 0 0.75rem;
    }
    .sidebar-footer {
        margin-top: 2rem;
        padding-top: 0.9rem;
        border-top: 1px solid var(--border);
        color: var(--muted);
        font-size: 0.77rem;
        line-height: 1.6;
    }

    /* Compact welcome screen */
    .topline {
        color: var(--accent);
        font-size: 0.73rem;
        font-weight: 750;
        letter-spacing: 0.14em;
        margin-bottom: 0.85rem;
    }
    .hero {
        background: linear-gradient(135deg, #183326 0%, #11271c 75%, #122c20 100%);
        border: 1px solid #3a6149;
        border-radius: 22px;
        padding: 2.2rem 2.3rem;
        margin: 0.3rem 0 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .hero-copy { position: relative; z-index: 1; }
    .hero h1 {
        color: var(--text) !important;
        font-size: clamp(1.85rem, 4vw, 2.8rem);
        letter-spacing: -0.05em;
        line-height: 1.14;
        margin: 0 0 0.7rem;
        font-weight: 780;
    }
    .hero h1 span { color: var(--accent) !important; }
    .hero p {
        color: var(--muted) !important;
        font-size: 0.98rem;
        line-height: 1.55;
        margin: 0;
    }
    .section-title {
        color: var(--text);
        font-size: 1rem;
        font-weight: 700;
        margin: 1.1rem 0 0.75rem;
    }

    /* Suggested prompts: intentionally higher contrast than the background */
    [data-testid="stMain"] .stButton button {
        background: var(--surface-raised) !important;
        color: var(--text) !important;
        border: 1px solid #4f765b !important;
        border-radius: 14px;
        min-height: 70px;
        padding: 0.9rem 1rem;
        text-align: left;
        justify-content: flex-start;
        white-space: normal;
        font-weight: 650;
    }
    [data-testid="stMain"] .stButton button:hover,
    [data-testid="stMain"] .stButton button:focus-visible {
        background: var(--surface-hover) !important;
        border-color: var(--accent) !important;
        color: #ffffff !important;
    }
    [data-testid="stMain"] .stButton button p,
    [data-testid="stMain"] .stButton button span { color: inherit !important; }
    .stButton button:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }

    /* Messages and input */
    [data-testid="stChatMessage"] {
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.7rem;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li { color: var(--text) !important; line-height: 1.65; }
    [data-testid="stChatInput"] {
        background: var(--surface-raised) !important;
        border: 1px solid #4f765b !important;
        border-radius: 15px;
    }
    [data-testid="stChatInput"]:focus-within { border-color: var(--accent) !important; }
    [data-testid="stChatInput"] textarea { color: var(--text) !important; }
    [data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; opacity: 1; }

    @media (max-width: 720px) {
        [data-testid="stMainBlockContainer"] { padding-top: 1.1rem; }
        .hero { padding: 1.8rem 1.4rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def generate_session_id() -> str:
    return str(uuid.uuid4())


def init_session_state() -> None:
    if "current_session" not in st.session_state:
        st.session_state.current_session = generate_session_id()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {st.session_state.current_session: []}
    if st.session_state.current_session not in st.session_state.chat_history:
        st.session_state.chat_history[st.session_state.current_session] = []
    if "messages" not in st.session_state:
        st.session_state.messages = st.session_state.chat_history[st.session_state.current_session]


def save_current_chat() -> None:
    st.session_state.chat_history[st.session_state.current_session] = st.session_state.messages


def new_chat_handler() -> None:
    save_current_chat()
    # Reuse the current empty conversation instead of creating duplicate blank chats.
    if not st.session_state.messages:
        return
    new_session_id = generate_session_id()
    st.session_state.chat_history[new_session_id] = []
    st.session_state.current_session = new_session_id
    st.session_state.messages = st.session_state.chat_history[new_session_id]


def change_chat(new_session_id: str) -> None:
    if new_session_id == st.session_state.current_session:
        return
    save_current_chat()
    st.session_state.current_session = new_session_id
    st.session_state.messages = st.session_state.chat_history[new_session_id]


def chat_title(messages: list[dict]) -> str:
    """Derive a readable title from the first user question."""
    first_user = next((m["content"] for m in messages if m["role"] == "user"), None)
    if not first_user:
        return "New conversation"
    title = " ".join(first_user.split())
    return title if len(title) <= 31 else title[:28].rstrip() + "..."


def extract_text(content) -> str:
    """Support plain strings and Gemini/LangChain text content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
        return "".join(parts)
    return ""


def stream_assistant_reply(prompt: str):
    config = {"configurable": {"thread_id": st.session_state.current_session}}
    for chunk in chatbot.stream(
        {"messages": [HumanMessage(content=prompt)]},
        config=config,
        stream_mode="messages",
        version="v2",
    ):
        # Compatible with the v2 dict event shape in the original app.
        if not isinstance(chunk, dict) or chunk.get("type") != "messages":
            continue
        message_chunk, _metadata = chunk["data"]
        text = extract_text(message_chunk.content)
        if text:
            yield text


init_session_state()

# Sidebar: clear branding + human-friendly conversation names.
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <span class="brand-mark">🌿</span>
            <span class="brand-name">Green Design</span>
            <p class="brand-tagline">Learn with Prithiv</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "＋  New conversation",
        key="new_chat",
        on_click=new_chat_handler,
        use_container_width=True,
        type="primary",
    )
    st.markdown('<div class="sidebar-heading">YOUR CONVERSATIONS</div>', unsafe_allow_html=True)
    for session_id, saved_messages in reversed(list(st.session_state.chat_history.items())):
        is_active = session_id == st.session_state.current_session
        name = chat_title(saved_messages)
        label = f"●  {name}" if is_active else f"    {name}"
        st.button(
            label,
            key=f"conversation_{session_id}",
            on_click=change_chat,
            args=(session_id,),
            use_container_width=True,
        )
    st.markdown(
        '<div class="sidebar-footer">GREEN DESIGN ASSISTANT<br>'
        'Sustainability · Materials · Energy</div>',
        unsafe_allow_html=True,
    )

messages = st.session_state.messages
suggested_prompt = None

if not messages:
    st.markdown(
        """
        <div class="topline">YOUR GREEN DESIGN ASSISTANT</div>
        <div class="hero">
            <div class="hero-copy">
                <h1>Learn <span>Green Design</span> with Prithiv</h1>
                <p>Explore sustainable ideas, materials, and greener spaces.</p>
            </div>
        </div>
        <div class="section-title">Try a question</div>
        """,
        unsafe_allow_html=True,
    )
    starters = [
        ("🌿  What is green design?", "Explain green design principles with examples."),
        ("🏡  Sustainable buildings", "How can I design an energy-efficient, sustainable home?"),
        ("♻️  Eco-friendly materials", "What are some eco-friendly alternatives to common building materials?"),
    ]
    for column, (label, question) in zip(st.columns(3, gap="medium"), starters):
        if column.button(label, use_container_width=True, key=f"starter_{label}"):
            suggested_prompt = question
else:
    st.markdown(
        '<div class="topline">GREEN DESIGN / CONVERSATION</div>',
        unsafe_allow_html=True,
    )

# Re-render prior messages. st.markdown supports formatted AI responses.
for message in messages:
    with st.chat_message(message["role"], avatar="🌿" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

entered_prompt = st.chat_input("Ask about green design and sustainability...")
prompt = entered_prompt or suggested_prompt

if prompt:
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    save_current_chat()
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🌿"):
        try:
            answer = st.write_stream(stream_assistant_reply(prompt))
        except Exception:
            # Details stay in server logs; avoid showing internal API errors to visitors.
            st.error("I couldn't respond just now. Please try again.")
        else:
            if not answer:
                answer = "I couldn't generate a response. Please try asking that another way."
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            save_current_chat()
