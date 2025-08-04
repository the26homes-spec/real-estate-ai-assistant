import os
import time
from flask import Flask, request, send_file
from twilio.twiml.voice_response import VoiceResponse, Play
from openai import OpenAI
from elevenlabs import generate, set_api_key
from twilio.rest import Client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Set ElevenLabs and OpenAI API keys
set_api_key(os.getenv("ELEVENLABS_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ensure static folder exists
os.makedirs("static", exist_ok=True)

@app.route("/")
def index():
    return "AI Assistant is live!"

@app.route("/voice", methods=["POST"])
def handle_voice():
    from_number = request.form.get("From", "Unknown")
    print(f"📞 Incoming call from: {from_number}")

    # Get transcription or fallback
    user_input = request.form.get("SpeechResult", "")
    print(f"🗣 User said: {user_input}")

    if not user_input.strip():
        user_input = "Hello, I'd like help finding an apartment."

    # Generate GPT response
    chat_reply = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a real estate assistant helping users find rental apartments."},
            {"role": "user", "content": user_input}
        ]
    ).choices[0].message.content

    print(f"🤖 GPT reply: {chat_reply}")

    # Generate voice from ElevenLabs
    audio = generate(text=chat_reply, voice="EXAVITQu4vr4xnSDxMaL")  # Rachel

    audio_path = os.path.join("static", "reply.mp3")
    with open(audio_path, "wb") as f:
        f.write(audio)
        f.flush()
        os.fsync(f.fileno())

    time.sleep(1.5)  # Ensure file is fully written

    print(f"📏 reply.mp3 size: {os.path.getsize(audio_path)} bytes")

    # Send WhatsApp lead (optional)
    try:
        twilio_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH"))
        twilio_client.messages.create(
            body=f"New lead from {from_number}\nMessage: {user_input}",
            from_=os.getenv("TWILIO_WHATSAPP"),
            to=os.getenv("MY_WHATSAPP")
        )
    except Exception as e:
        print(f"❌ WhatsApp error: {e}")

    # Respond with TwiML to play audio
    response = VoiceResponse()
    response.play(url=f"{request.host_url}static/reply.mp3")
    return str(response)

@app.route("/static/reply.mp3")
def serve_audio():
    audio_path = os.path.join("static", "reply.mp3")
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype="audio/mpeg", as_attachment=False)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=10000)
