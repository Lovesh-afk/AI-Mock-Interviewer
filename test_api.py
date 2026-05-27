from google import genai
import os 
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="models/gemini-2.5-flash-lite",
    contents="Give me 3 interview questions for a Python Backend Developer role"
)

print(response.text)