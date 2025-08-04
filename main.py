
from flask import Flask, request, jsonify
import openai, os
from elevenlabs import generate, set_api_key
from twilio.rest import Client

app = Flask(__name__)

# Load API keys from env
openai.api_key = os.getenv("OPENAI_API_KEY")
set_api_key(os.getenv("ELEVENLABS_API_KEY"))
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")
twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

questions = [
    "What’s your name?",
    "What kind of apartment are you looking for?",
    "How many bedrooms do you need?",
    "What’s your ideal move-in date?",
    "What’s your monthly budget?",
    "Do you have pets or a housing voucher?"
]

@app.route("/voice", methods=["POST"])
def handle_voice():
    caller = request.form.get("From")
    speech_input = request.form.get("SpeechResult", "")

    chat_reply = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a friendly real estate assistant. Ask the caller one question at a time to qualify them as a rental lead. Let them ask you things too."},
            {"role": "user", "content": speech_input}
        ]
    )["choices"][0]["message"]["content"]

    os.makedirs("static", exist_ok=True)
    audio = generate(text=chat_reply, voice="EXAVITQu4vr4xnSDxMaL")  # Rachel's voice ID
    audio_path = "static/reply.mp3"
    with open(audio_path, "wb") as f:
        f.write(audio)

    response = f'''
    <Response>
        <Play>https://yourdomain.com/static/reply.mp3</Play>
    </Response>
    '''
    return response, 200, {"Content-Type": "text/xml"}

@app.route("/send-lead", methods=["POST"])
def send_lead():
    data = request.json
    body = "📋 New Rental Lead:\n\n" + "\n".join([f"{k}: {v}" for k, v in data.items()])
    twilio_client.messages.create(
        body=body,
        from_=TWILIO_WHATSAPP,
        to=WHATSAPP_TO
    )
    return jsonify({"status": "sent"}), 200

if __name__ == "__main__":
    app.run(debug=True)
