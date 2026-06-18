from mem0 import Memory
OPENAI_API_KEY="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"

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



