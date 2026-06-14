from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing. Check your .env file.")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": "Say: Nerdbot API connection is working."}
    ],
)

print(response.choices[0].message.content)