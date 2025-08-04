
from flask import Flask, request, send_file
from twilio.twiml.voice_response import VoiceResponse, Play
from elevenlabs_helper import generate_speech
from utils import summarize_lead_and_send

app = Flask(__name__)
calls = {}

@app.route("/voice", methods=['POST'])
def voice():
    call_sid = request.form['CallSid']
    response = VoiceResponse()

    questions = [
        "Welcome! Are you calling about renting an apartment? Please say yes or no.",
        "What is your full name?",
        "What type of apartment are you looking for?",
        "What is your desired monthly budget?",
        "When would you like to move in?",
        "Thank you! We'll contact you shortly on WhatsApp."
    ]

    step = calls.get(call_sid, 0)
    if step < len(questions):
        speech_file = generate_speech(questions[step])
        response.play(speech_file)
        calls[call_sid] = step + 1
    else:
        gather_data = {key: request.form.get(key) for key in request.form}
        summarize_lead_and_send(call_sid, gather_data)
        response.say("We have received your information. Goodbye!")
        calls.pop(call_sid, None)

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
