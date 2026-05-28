from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
client=OpenAI()

response=client.chat.completions.create(
  model="gpt-4.1-mini",
  messages=[
    {
      "role":"user",
      "content":[
        {"type":"text","text":"Generate a caption for this image iin 50 words and also tell me the breed of dogs in the image"},
        {"type":"image_url","image_url":{"url":"https://d.newsweek.com/en/full/1784323/rarest-dog-breeds-us.jpg"}}
      ]
    }
  ]

)
print("Response:", response.choices[0].message.content)