import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid


def generate_session_id():
    session_id = uuid.uuid4()
    return str(session_id)

def handle_msg_submit():
    msg = {
        "role": "user",
        "content": st.session_state["input_msg"]
    }
    st.session_state.messages.append(msg)

def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                # common pattern: {"text": "..."}
                parts.append(item.get("text", ""))
        return "".join(parts)
    return ""
    
def ai_msg_generator():
    for chunk in chatbot.stream({
            "messages": [HumanMessage(content=input_msg)]
        }, config=config, stream_mode="messages", version="v2"):

        if chunk["type"] == "messages":
            message_chunk, metadata = chunk["data"]
            if message_chunk.content:
                content = extract_text(message_chunk.content)
                st.session_state.ai_msg += content
                yield content

def new_chat_handler():
    st.session_state["chat_history"][st.session_state.current_session] = st.session_state.messages

    new_session_id = generate_session_id()
    st.session_state["chat_history"][new_session_id] = []
    st.session_state.current_session = new_session_id
    st.session_state.messages = []

#implement 
def change_chat(new_session_id):
    print(f"Old session: {st.session_state.current_session}")
    st.session_state["chat_history"][st.session_state.current_session] = st.session_state.messages
    st.session_state.current_session = new_session_id
    st.session_state.messages = st.session_state["chat_history"][st.session_state.current_session] 
    print(f"New session: {new_session_id}")



if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_id()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {
        st.session_state.current_session : []
    }

st.title("Let the Learning Begin..", text_alignment="center")

with st.sidebar:
    st.title("Chatbot")
    st.button("New Chat", on_click=new_chat_handler)
    st.subheader("Our Conversations")
    for session_id in st.session_state["chat_history"]:
        st.button(session_id, key=session_id, on_click=change_chat, args=(session_id,))


if "messages" not in st.session_state:
    st.session_state.messages = st.session_state["chat_history"][st.session_state.current_session]

for msg in  st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

input_msg = st.chat_input("Type here...", on_submit=handle_msg_submit, key="input_msg")
config = {"configurable": {"thread_id": st.session_state.current_session}}

if input_msg:
    st.session_state.ai_msg = ""
    with st.chat_message("assistant"):
        st.write_stream(ai_msg_generator)
        
    st.session_state.messages.append({
        "role": "assistant",
        "content": st.session_state.ai_msg
    })
