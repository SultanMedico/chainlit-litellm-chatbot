import os
import json
from dotenv import load_dotenv
import chainlit as cl
from litellm import completion

# ─────────────────────────────────────────────
# 🔐 Load API Key from Environment Variables
# ─────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing in .env file.")

# ─────────────────────────────────────────────
# 💬 Chat Start Event
# ─────────────────────────────────────────────
@cl.on_chat_start
async def start_chat():
    """Initialize user session when chat starts."""
    cl.user_session.set("chat_history", [])
    await cl.Message(
        content="✨ Welcome to the **Sultan's AI Assistant** — your intelligent companion! How can I assist you today?"
    ).send()


# ─────────────────────────────────────────────
# 📩 Message Handler
# ─────────────────────────────────────────────
@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming user messages and generate AI responses."""
    
    # Temporary "thinking..." response
    msg = cl.Message(content="🤖 Thinking...")
    await msg.send()

    # Get chat history
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})

    try:
        # Generate response using LiteLLM
        response = completion(
            model="gemini/gemini-2.0-flash",
            api_key=GEMINI_API_KEY,
            messages=history
        )

        # Extract content
        assistant_reply = response.choices[0].message.content

        # Update message and history
        msg.content = assistant_reply
        await msg.update()
        history.append({"role": "assistant", "content": assistant_reply})
        cl.user_session.set("chat_history", history)

        # Log for debugging
        print(f"🧑‍💻 User: {message.content}")
        print(f"🤖 Assistant: {assistant_reply}")

    except Exception as e:
        msg.content = f"⚠️ Error: {str(e)}"
        await msg.update()
        print(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────
# 🛑 Chat End Event
# ─────────────────────────────────────────────
@cl.on_chat_end
async def save_chat_history():
    """Save the chat history to a file at the end of the session."""
    history = cl.user_session.get("chat_history") or []
    with open("chat_history.json", "w") as f:
        json.dump(history, f, indent=2)
    print("✅ Chat history saved to chat_history.json")