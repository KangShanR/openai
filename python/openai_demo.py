import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

print(openai.api_key)

# print(openai.__version__)
chat_completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content':'Hello, how are you?'}])

chat_completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role':'user','content':'hello'}])
