from mem0 import Memory
from dotenv import load_dotenv
from openai import OpenAI
import json
load_dotenv()
OPENAI_API_KEY="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"
client=OpenAI(

)
config={
  "version":"v1.1",
  "embedder":{
    "provider":"openai",
    "config":{"api_key":OPENAI_API_KEY,"model":"text-embedding-3-small"}
  },
  "llm":{
    "provider":"openai",
    "config":{"api_key":OPENAI_API_KEY,"model":"gpt-4.1"}
  },
  "vector_store":{
    "provider":"qdrant",
    "config":{"host":"localhost","port":6333}
  }

}

memory_client=Memory.from_config(config)

while True:
  user_query=input("Enter the query : ")
  search_memory=memory_client.search(query=user_query,filters={"user_id":"prakhar"})
  memories=[
    f"ID:{mem.get('id')}\nMemory: {mem.get('memory')}" for mem in search_memory["results"] # results refers to the key inside the response dictionary that search_memory returns.
  ]
  print("Found memories",memories)

  SYSTEM_PROMPT = f"""
    Here is the context about the user:
    {json.dumps(memories)}
  """
  response=client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role":"system","content":SYSTEM_PROMPT},
              {"role":"user","content":user_query}]
  )

  ai_response=response.choices[0].message.content
  print("AI message: ",ai_response)

  memory_client.add(
    user_id="prakhar",
    messages=[
      {"role":"user","content":user_query},
      {"role":"assistant","content":ai_response}
    ]
    
  )

  print("Memory has been saved...")
