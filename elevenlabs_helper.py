
import requests
import os

def generate_speech(text):
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    api_key = os.getenv("ELEVENLABS_API_KEY")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    response = requests.post(
        url,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json={"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.7}}
    )

    filename = f"audio_{hash(text)}.mp3"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename
