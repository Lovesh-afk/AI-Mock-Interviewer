from google import genai

client = genai.Client(api_key="AIzaSyCZJeaiIQMFuNgb6sX2mc8Fj-8DcyXuegA")

response = client.models.generate_content(
    model="models/gemini-2.5-flash-lite",
    contents="Give me 3 interview questions for a Python Backend Developer role"
)

print(response.text)