import os
import requests

ds_api_key = os.getenv("ds_api_key")
print(f'KEY:{ds_api_key}')


url = "https://api.deepseek.com/models"
payload={}
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {ds_api_key}'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(f"model list:{response.text}")


# query balance
bl_url = "https://api.deepseek.com/user/balance"

payload={}
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {ds_api_key}'
}

response = requests.request("GET", bl_url, headers=headers, data=payload)

print(f'balance:{response.text}')


import requests
import json

url = "https://api.deepseek.com/chat/completions"

payload = json.dumps({
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "frequency_penalty": 0,
  "max_tokens": 2048,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": None,
  "stream": False,
  "stream_options": None,
  "temperature": 1,
  "top_p": 1,
  "tools": None,
  "tool_choice": "none",
  "logprobs": False,
  "top_logprobs": None
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer <TOKEN>'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)