# Here we are building a structured agent which wioll not give output in the specified json format but will follow the steps of START, PLAN, TOOL, OBSERVE and OUTPUT.

import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
from openai.types.chat import ChatCompletionMessageParam,ChatCompletionAssistantMessageParam
from pydantic import BaseModel, Field
import subprocess

load_dotenv()
client=OpenAI()

def run_cmd(cmd: str):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    return f"""
STDOUT:
{result.stdout}

STDERR:
{result.stderr}

RETURN CODE:
{result.returncode}
"""

def get_weather(city:str):
    url =f"https://wttr.in/{city.lower()}?format=%C+%t"
    response=requests.get(url)

    if response.status_code==200:
        return f"The weather in the {city} is {response.text}"
    
    return "Sorry couldn't fetch the weather for the city you mentioned."

available_tools={
  "get_weather":get_weather,
  "run_cmd":run_cmd
}
system_prompt="""
You're an expert ai assistant in resolving user queries using chain of thought.
you work on START, PLAN, and OUTPUT steps.
you need to first PLAN what needs to be done. the PLAN can be multiple steps.
Once you think enough PLAN has been done ,finally you can give an OUTPUT.
You can also call a tool if required from the list of available tools.
Every tool call wait for the observe step, which is the output for the called tool

Rule:
-Strictly follow the output in JSON output format
-Only run one step at a time.
-The sequence of steps is START (where user gives an input), PLAN (That can be multiple times)
and finally OUTPUT(which is going to be displayed to the user).

Output JSON format:
{"step":"START"|"PLAN"|"OUTPUT"|"TOOL","content":"string","tool":"string","input":"string"}

Available Tools:
- get_weather(city:str): Takes city name as an input string and returns the weather as a string. 
- run_cmd(cmd:str): Takes a command as an input string and executes it in the terminal.

Example 1:
START: What is the weather in New York?
PLAN:{"step": "PLAN","content": "Seema like user is interested i getting weather of Delhi in India"}
PLAN:{"step": "PLAN","content": "Let's see if we have any available tool from  the list of available tools. "}
PLAN:{"step": "PLAN","content": "Great. we have get_weather tool available for this query"}
PLAN:{"step": "PLAN","content": "I need to call the get_weather tool for Delhi as input for the city. "}
PLAN:{"step":"TOOL", "tool": "get_weather", "input":"Delhi"}
PLAN:{"step":"OBSERVE","tool":"get_weather","output":"The temp of delhi is cloudy with 30 degree celsius."}
PLAN:{"step":"PLAN","content":"Great, I got the weather info about delhi"}
OUTPUT:{"step":"OUTPUT","content":"The weather in Delhi is cloudy with 30 degree celsius."}
"""
print("\n\n\n")

class OutputFormat(BaseModel):
   step:str=Field(...,description="This ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
   content:Optional[str]=Field(None,description="This is the content for the step. It can be the reasoning for PLAN step or final answer for OUTPUT step")
   tool:Optional[str]=Field(None,description="This is the name of the tool to be called in case of TOOL step")
   input:Optional[str]=Field(None,description="This is the input for the tool in case of TOOL step")
   

message_history:list[ChatCompletionMessageParam]=[
  {"role":"system","content":system_prompt},
# This tells Pylance: “This list contains proper OpenAI message objects,” so it stops complaining about the system and user messages.
]

while True:
  user_query=input("👉🏻")
  message_history.append({"role":"user","content":user_query})
  # Assistant messages have slightly different rules (content can sometimes be more complex). Using the special assistant class fixes the last error about str | None and bytes.

  while True:
      response=client.beta.chat.completions.parse(
          model="gpt-4.1",
          response_format=OutputFormat,#{"type":"json_object"}
          messages=message_history
      )
      
      raw_result=response.choices[0].message.content or ""
      message_history.append(
        ChatCompletionAssistantMessageParam(role="assistant",content=raw_result)
      )
      # parsed_result=json.loads(raw_result)
      parsed_result=response.choices[0].message.parsed

      # if parsed_result.get("step")=="START":
      if parsed_result.step == "START":
        print("🔥",parsed_result.content)
        continue
      if parsed_result.step=="TOOL":
        tool_to_call=parsed_result.tool
        tool_input=parsed_result.input
        print(f"Calling tool {tool_to_call} with input {tool_input}")

        tool_response=available_tools[tool_to_call](tool_input)
        print(f"Tool {tool_to_call} ({tool_input}): {tool_response}")
        message_history.append({
          "role":"developer","content":json.dumps({
            "step":"OBSERVE","tool":tool_to_call,"output":tool_response}
          )
        })
        continue
          

      if parsed_result.step=="PLAN":
        print("🧠",parsed_result.content)
        continue
      
      if parsed_result.step=="OUTPUT":
        print("✅",parsed_result.content)
        break
      # print("\n\n\n")
