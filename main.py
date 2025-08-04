from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
from elevenlabs_helper import generate_speech
from utils import summarize_lead_and_send
import os

app = Flask(__name__)
calls = {}
responses = {}

@app.route("/voice", methods=['POST'])
def voice():
    call_sid = request.form['CallSid']
    speech_result = request.form.get("SpeechResult")
    digits = request.form.get("Digits")

    response = VoiceResponse()

    # Initialize responses dict if needed
    if call_sid not in responses:
        responses[call_sid] = {}

    # Handle response from previous step
    if call_sid in calls and calls[call_sid] > 0 and (speech_result or digits):
        step = calls[call_sid] - 1
        responses[call_sid][f"q{step+1}"] = speech_result or digits or "No response"

    # Questions to ask
    questions = [
        "Welcome! Are you calling about renting an apartment? Please say yes or no.",
        "What is your full name?",
        "What type of apartment are you looking for?",
        "What is your desired monthly budget?",
        "When would you like to move in?",
        "Thank you! We'll contact you shortly on WhatsApp."
    ]

    step = calls.get(call_sid, 0)

    # Handle final step
    if step >= len(questions):
        summarize_lead_and_send(call_sid, responses[call_sid])
        response.say("We have received your information. Goodbye!")
        calls.pop(call_sid, None)
        responses.pop(call_sid, None)
        return str(response)

    # Generate next question audio
    speech_url = generate_speech(questions[step])

    # Gather for speech or keypad, fallback if no input
    gather = response.gather(
        input='speech dtmf',
        timeout=6,
        num_digits=1,
        action='/voice',
        method='POST'
    )
    gather.play(speech_url)

    # Update step for next time
    calls[call_sid] = step + 1

    return str(response)

@app.route('/<filename>')
def serve_audio(filename):
    return send_from_directory('.', filename)

if __name__ == "__main__":
    app.run(debug=True)
