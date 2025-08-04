
import requests
import os

def generate_speech(text):
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")

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
    if response.status_code == 200 and response.content and len(response.content) > 1000:
        with open(filename, "wb") as f:
            f.write(response.content)
        return f"https://{hostname}/{filename}"
    else:
        print("❌ Failed to generate audio from ElevenLabs")
        return None
