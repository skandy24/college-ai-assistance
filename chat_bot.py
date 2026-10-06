import time
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# 1. Read the college information
with open("college_info.txt", "r", encoding="utf-8") as f:
    college_info = f.read()

# 2. The "system instruction" tells Gemini who it is and how to behave
SYSTEM_PROMPT = f"""
You are a friendly AI assistant for students of our college.
Answer ONLY using the college information below.
If the answer is not in the information, say you don't have that
detail and suggest contacting the college office. Never invent facts.
Keep answers short, clear and polite.

COLLEGE INFORMATION:
{college_info}
"""

# 3. A chat session remembers earlier messages automatically
chat = client.chats.create(
    model=MODEL,
    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
)

print("College AI Assistant (type 'quit' to exit)")


def ask(chat, text, retries=4):
    for attempt in range(retries):
        try:
            return chat.send_message(text).text
        except Exception as e:
            busy = "503" in str(e) or "UNAVAILABLE" in str(e)
            if busy and attempt < retries - 1:
                wait = 2 ** (attempt + 1)   # waits 2s, 4s, 8s
                print(f"Server busy, retrying in {wait} seconds...")
                time.sleep(wait)
            else:
                raise
while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() in ("quit", "exit"):
        print("Goodbye!")
        break
    if not user_input:
        continue
    try:
        print("Assistant:", ask(chat, user_input))
    except Exception as e:
        print("Something went wrong:", e)