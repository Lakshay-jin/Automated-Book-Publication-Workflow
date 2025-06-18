import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
# Load API key from environment or hard-code it here (NOT RECOMMENDED for production)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")

# Configure the API
genai.configure(api_key=GEMINI_API_KEY)

# Call Gemini API
def call_gemini(prompt: str, model: str = "gemini-2.0-flash") -> str:
    try:
        model = genai.GenerativeModel(model)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Error while calling Gemini:", e)
        return "Error generating content."
