# test_connection.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.parser.models import ResumeSchema

load_dotenv()

def test_gemini_structured_output():
    # Initialize the client (auto-discovers GEMINI_API_KEY from environment variables)
    client = genai.Client()
    
    prompt = """
    Extract this fake information into a structured schema:
    John Doe, contact: john@example.com. He knows Python and Docker. 
    He worked at Acme Corp as a DevOps Engineer from Jan 2025 to Present, 
    where he optimized deployment pipelines and managed cloud infrastructure.
    """
    
    print("Sending request to Gemini...")
    
    # We use gemini-1.5-pro for complex structured reasoning tasks
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ResumeSchema,
            temperature=0.1,
        ),
    )
    
    print("\n--- Structured JSON Response Received ---")
    print(response.text)

if __name__ == "__main__":
    test_gemini_structured_output()