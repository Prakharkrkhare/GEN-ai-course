from dotenv import load_dotenv
load_dotenv()
import speech_recognition as sr
import asyncio
from openai import OpenAI, AsyncOpenAI
from openai.helpers import LocalAudioPlayer


client=OpenAI()
async_client=AsyncOpenAI()

async def tts(speech:str):
  async with async_client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="onyx",
    instructions="Always speak in a cheerful manner, with the full of delight and happy. ",
    input=speech,
    response_format="pcm",
  ) as response:
      await LocalAudioPlayer().play(response)



def main():
  r=sr.Recognizer() # Speech to text 
  with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)
    r.pause_threshold=2

    SYSTEM_PROMPT=f"""
      You are an expert voice agent. You are given the transcript of what user has said using voice.
      You need to output as if you are a voice agent, and whatever you speak will be converted back to audio using AI and played back to user. 
    """
    messages=[{"role":"system","content":SYSTEM_PROMPT}]

    while True:
      print("Hey user, please speak something... ")
      audio=r.listen(source)
      print("Processing Audio... (STT)")
      stt=r.recognize_google(audio)

      print("You Said:",stt)
      messages.append({"role":"user","content":stt})
      response=client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
      )
      print("AI Response :",response.choices[0].message.content)
      ai_response=response.choices[0].message.content
      asyncio.run(tts(speech=response.choices[0].message.content))
      messages.append({"role":"assistant","content": ai_response})
      

main()
