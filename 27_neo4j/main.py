import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from mem0 import Memory
from dotenv import load_dotenv
from openai import OpenAI
import json
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embedding-3-small"}
    },
    "llm": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4o"}
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "neo4j+s://2b529fd6.databases.neo4j.io",  # ✅ back to +s://
            "username": os.getenv("NEO4J_USERNAME"),
            "password": os.getenv("NEO4J_PASSWORD"),
            "database": os.getenv("NEO4J_DATABASE")
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333}
    },
    "enable_graph": True
}

memory_client = Memory.from_config(config)
USER_ID = "prakhar"

while True:
    user_query = input("Enter the query: ")

    search_memory = memory_client.search(query=user_query, user_id=USER_ID)
    memories = [
        f"ID:{mem.get('id')}\nMemory: {mem.get('memory')}"
        for mem in search_memory["results"]
    ]
    print("Found memories:", memories)

    SYSTEM_PROMPT = f"""
    Here is the context about the user:
    {json.dumps(memories)}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
    )

    ai_response = response.choices[0].message.content
    print("AI message:", ai_response)

    memory_client.add(
        messages=[
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": ai_response}
        ],
        user_id=USER_ID
    )

    print("Memory saved.")