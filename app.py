import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from openai import OpenAI

from memory import add_message, get_history

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BOT_TAG = "@bot"

app = Flask(__name__)

@app.route("/incoming", methods=["POST"])
def incoming_message():
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From")
    convo_id = request.form.get("ConversationSid", from_number)  
    # Fallback: use phone # if no conversation thread ID

    # Record incoming user message
    add_message(convo_id, "user", incoming_msg)

    # Only reply when tagged
    if not incoming_msg.lower().startswith(BOT_TAG):
        return ("", 204)  # no reply

    # Remove tag to get user prompt
    user_prompt = incoming_msg[len(BOT_TAG):].strip()

    # Build context
    history = get_history(convo_id)

    # Construct message list in OpenAI format
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_prompt})

    # Ask the LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    bot_reply = response.choices[0].message["content"]

    # Save bot reply in history
    add_message(convo_id, "assistant", bot_reply)

    # Respond via Twilio
    twilio_response = MessagingResponse()
    twilio_response.message(bot_reply)

    return str(twilio_response)

@app.route("/", methods=["GET"])
def home():
    return "RCS bot running!"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
