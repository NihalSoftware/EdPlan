import os
import json
from groq import Groq
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def extract_user_intent(user_input: str) -> dict:
    try:
        system_prompt = """
        You are an intelligent data extractor for an Education Planning system.
        Extract information from the user's input. They might provide a program/subject, time constraints, or both.
        
        CRITICAL RULES: 
        1. If the user's input is a casual greeting ("Hi"), a general question ("How are you"), or completely unrelated to education/subjects/scheduling (e.g., "Write a poem"), set "is_relevant" to false.
        2. If they mention ANY academic subject, career, or program (e.g., "art", "nursing", "math", "computer"), it IS relevant ("is_relevant": true).
        3. If they only mention days or times (e.g., "I am busy on Monday"), it IS relevant.

        Return ONLY a valid JSON object.
        
        {
          "is_relevant": true or false,
          "selectedProgram": "Extracted subject/program name. Empty string if not found.",
          "busyDays": {"Mon": true, "Tue": true} (Map mentioned unavailable days. Keys: Mon, Tue, Wed, Thu, Fri),
          "busyTimes": {"morning": true} (Map mentioned unavailable times. Keys: morning, afternoon, evening)
        }
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}, 
            temperature=0.1, 
        )

        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        print(f"Groq API Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process text via AI")