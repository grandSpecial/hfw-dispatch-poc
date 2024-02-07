from fastapi import FastAPI, Request
from twilio.twiml.voice_response import VoiceResponse
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),)

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")

app = FastAPI()

@app.post("/incoming_call")
async def handle_incoming_call():
    response = VoiceResponse()

    response.say("""
        Welcome to the Dietician Help Line! I\'m here to assist you 
        with any questions or concerns you have about diet and nutrition. 
        Let\'s discuss your dietary goals and needs. 
        How can I assist you today?
        """,voice='Polly.Matthew-Neural')

    response.gather(
        input='speech',
        speech_timeout='auto',
        speech_model="phone_call",
        action="/respond",
        method="POST"
    )

    return Response(content=str(response), media_type="application/xml")

@app.post("/transcribe")
async def handle_incoming_call():
    response = VoiceResponse()
    response.gather(
        input='speech',
        speech_timeout='auto',
        speech_model="phone_call",
        action="/respond",
        method="POST"
    )

    return Response(content=str(response), media_type="application/xml")

@app.post("/respond")
async def handle_response(request: Request):
    form_data = await request.form()
    transcription = form_data.get('SpeechResult', '')

    # Process the transcription with GPT-4 or any other logic you have
    # For example, send it to GPT-4 and get a response
    gpt_response = await generate_response(transcription)  # Assuming this function is defined elsewhere

    # Respond back to the caller with GPT-4's response
    response = VoiceResponse()
    response.say(gpt_response, voice='alice')
    
    # Optionally, you might want to gather more input based on the conversation context
    response.gather(
        input='speech',
        speech_timeout='auto',
        speech_model="phone_call",
        action="/transcribe",
        method="POST"
    )

    return Response(content=str(response), media_type="application/xml")

