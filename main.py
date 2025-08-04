import os
import logging
from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Play
from elevenlabs import generate, set_api_key
import openai
from dotenv import load_dotenv

# Load .env if running locally
load_dotenv()

# Setup
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# API keys from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
set_api_key(os.getenv("ELEVEN_API_KEY"))

# Ensure static folder exists
os.makedirs("static", exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return "✅ Real Estate AI Assistant is Live!"

@app.route("/voice", methods=["POST"])
def handle_voice():
    try:
        logging.info("📞 Incoming call from: %s", request.form.get("From"))

        # Get voice transcription input (if available)
        user_input = request.form.get("SpeechResult", "").strip()
        logging.info("🗣 User said: %s", user_input)

        # Fallback prompt if input is empty
        if not user_input:
            user_input = "Hello"

        # OpenAI prompt
        prompt = f"""You are a friendly real estate rental assistant. 
A client said: {user_input}
Reply as a helpful assistant: """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        reply = response["choices"][0]["message"]["content"].strip()
        logging.info("🤖 GPT reply: %s", reply)

        # Generate voice from reply
        audio = generate(text=reply, voice="Rachel")  # Or use ID like "EXAVITQu4vr4xnSDxMaL"
        mp3_path = "static/reply.mp3"
        with open(mp3_path, "wb") as f:
            f.write(audio)
        logging.info("✅ Audio saved at: %s", mp3_path)

        # Respond via Twilio with MP3
        twiml = VoiceResponse()
        twiml.play(url=request.url_root + "static/reply.mp3")

        return str(twiml)

    except Exception as e:
        logging.error("❌ Error in /voice: %s", str(e))
        return str(VoiceResponse().say("Sorry, something went wrong."))

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
