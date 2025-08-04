
from flask import Flask, request, send_from_directory
import os
import time
import openai
from elevenlabs import generate, set_api_key
from twilio.rest import Client

app = Flask(__name__)

# Serve static files
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

@app.route("/voice", methods=["POST"])
def handle_voice():
    caller = request.form.get("From")
    speech_input = request.form.get("SpeechResult", "")

    print("📞 Incoming call from:", caller)
    print("🗣 User said:", speech_input)

    try:
        chat_reply = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a friendly real estate assistant. Ask qualifying questions for rentals."},
                {"role": "user", "content": speech_input}
            ]
        )["choices"][0]["message"]["content"]
        print("🤖 GPT reply:", chat_reply)
    except Exception as e:
        print("❌ OpenAI error:", e)
        return "<Response><Say>Sorry, there was a problem processing your request.</Say></Response>", 200, {"Content-Type": "text/xml"}

    try:
        os.makedirs("static", exist_ok=True)
        audio_path = os.path.join("static", "reply.mp3")
        audio = generate(text=chat_reply, voice="EXAVITQu4vr4xnSDxMaL")

        with open(audio_path, "wb") as f:
            f.write(audio)

        print(f"✅ Audio saved at: {audio_path}")
        print("📂 Static folder contains:", os.listdir("static"))
    except Exception as e:
        print("❌ ElevenLabs error:", e)
        return "<Response><Say>Sorry, voice generation failed.</Say></Response>", 200, {"Content-Type": "text/xml"}

    try:
        twilio_client.messages.create(
            body=f"📋 New Lead from {caller}\nInput: {speech_input}\nBot: {chat_reply}",
            from_=f"whatsapp:{TWILIO_WHATSAPP}",
            to=f"whatsapp:{WHATSAPP_TO}"
        )
        print("✅ WhatsApp message sent.")
    except Exception as e:
        print("❌ WhatsApp error:", e)

    time.sleep(1)  # Give file system a moment to flush

    response = f"""
    <Response>
        <Play>https://real-estate-ai-assistant-lo9h.onrender.com/static/reply.mp3</Play>
    </Response>
    """
    return response, 200, {"Content-Type": "text/xml"}

@app.route("/", methods=["GET"])
def index():
    return "Real Estate AI Assistant is running!", 200
