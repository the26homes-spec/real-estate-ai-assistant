import os
from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Play
import openai
from elevenlabs import generate, set_api_key

app = Flask(__name__, static_folder="static")
openai.api_key = os.getenv("OPENAI_API_KEY")
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

os.makedirs("static", exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return "Real Estate AI Assistant is running."

@app.route("/voice", methods=["POST"])
def voice():
    print("📞 Incoming call from:", request.form.get("From"))

    user_input = request.form.get("SpeechResult", "") or ""
    print("🗣 User said:", user_input)

    try:
        chat_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful real estate assistant."},
                {"role": "user", "content": user_input},
            ]
        )
        reply_text = chat_response["choices"][0]["message"]["content"]
        print("🤖 GPT reply:", reply_text)
    except Exception as e:
        reply_text = "Sorry, something went wrong."
        print("❌ OpenAI error:", e)

    try:
        audio = generate(text=reply_text, voice="Rachel")
        with open("static/reply.mp3", "wb") as f:
            f.write(audio)
        print("✅ Audio saved at: static/reply.mp3")
    except Exception as e:
        print("❌ ElevenLabs error:", e)
        reply_text = "Sorry, the voice service is unavailable."

    response = VoiceResponse()
    response.play(url=request.host_url + "static/reply.mp3")
    return str(response)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)