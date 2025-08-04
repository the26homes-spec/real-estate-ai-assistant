from flask import Flask, request, send_from_directory
import os
import openai
from elevenlabs import generate, set_api_key
from twilio.rest import Client

app = Flask(__name__)

# Enable static file serving for /static/reply.mp3
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

    # Get GPT reply
    chat_reply = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a friendly real estate assistant. Ask questions to qualify rental leads. Speak like a human."},
            {"role": "user", "content": speech_input}
        ]
    )["choices"][0]["message"]["content"]

    print("🤖 GPT reply:", chat_reply)

    # Generate voice
    os.makedirs("static", exist_ok=True)
    audio_path = os.path.join("static", "reply.mp3")
    audio = generate(text=chat_reply, voice="EXAVITQu4vr4xnSDxMaL")  # Rachel's voice ID

    # Save voice file
    with open(audio_path, "wb") as f:
        f.write(audio)

    print(f"✅ Voice saved to {audio_path}")
    print("📂 Folder contains:", os.listdir("static"))

    # Send WhatsApp lead notification
    body = f"📋 New Rental Lead:\nFrom: {caller}\nMessage: {speech_input}\nBot Reply: {chat_reply}"
    try:
        twilio_client.messages.create(
            body=body,
            from_=f"whatsapp:{TWILIO_WHATSAPP}",
            to=f"whatsapp:{WHATSAPP_TO}"
        )
        print("✅ WhatsApp message sent.")
    except Exception as e:
        print("❌ WhatsApp error:", e)

    # TwiML response to play voice
    response = f"""
    <Response>
        <Play>https://real-estate-ai-assistant-lo9h.onrender.com/static/reply.mp3</Play>
    </Response>
    """
    return response, 200, {"Content-Type": "text/xml"}

@app.route("/", methods=["GET"])
def index():
    return "Real Estate AI Assistant is running!", 200
