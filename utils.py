
import os
from twilio.rest import Client

def summarize_lead_and_send(call_sid, data):
    summary = f"""
📞 New Rental Inquiry:
Call ID: {call_sid}
Name: {data.get('Caller')}
Apartment Type: {data.get('SpeechResult')}
Budget: Unknown
Move-in Date: Unknown
"""

    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    client.messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
        to=os.getenv("MY_WHATSAPP_NUMBER"),
        body=summary
    )
