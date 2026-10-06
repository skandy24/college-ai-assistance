import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

COLLEGE_NAME = "RNS Institute of Technology"   
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

st.set_page_config(page_title=f"{COLLEGE_NAME} Assistant", page_icon="🎓")
st.title(f"🎓 {COLLEGE_NAME} AI Assistant")
st.caption("Ask me about timings, departments, events, rules and more.")



@st.cache_resource
def get_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


client = get_client()

with open("college_info.txt", "r", encoding="utf-8") as f:
    college_info = f.read()

SYSTEM_PROMPT = f"""
You are a friendly AI assistant for students of {COLLEGE_NAME}.
Answer ONLY using the college information below.
If the answer is not there, say you don't have that detail and
suggest contacting the college office. Never invent facts.
Keep answers short, clear and polite.

COLLEGE INFORMATION:
{college_info}
"""


def ask(chat, text, retries=4):
    for attempt in range(retries):
        try:
            return chat.send_message(text).text
        except Exception as e:
            busy = "503" in str(e) or "UNAVAILABLE" in str(e)
            if busy and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))   # waits 2s, 4s, 8s
            else:
                raise


if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                reply = ask(st.session_state.chat, prompt)
        except Exception as e:
            reply = f"Sorry, something went wrong: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})