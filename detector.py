import json
from groq import Groq

# Detects bugs in Python code using Groq Llama-3.1.
def detect_bugs(code: str, api_key: str) -> list:
    """
    Analyzes Python code for potential bugs using Groq's Llama-3.1-8b-instant.
    Returns a parsed list of dictionary items representing detected issues.
    """
    try:
        print("Debug: Initializing Groq client...")
        client = Groq(api_key=api_key)

        print("Debug: Constructing the prompt message...")
        system_prompt = "You are a senior Python code reviewer."
        user_message = (
            "Review this Python code and return ONLY a \n"
            "valid JSON array. No explanation. No markdown.\n"
            "Each item must have exactly these keys: \n"
            "line_number, bug_type, description, severity\n"
            "Severity must be: high, medium, or low\n\n"
            f"Code:\n{code}"
        )

        print("Debug: Sending request to Groq model 'llama-3.1-8b-instant'...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        print("Debug: Response received from Groq. Extracting content...")
        response_text = response.choices[0].message.content

        print("Debug: Clean-up response text by removing markdown wrappers if present...")
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        print("Debug: Parsing clean text using json.loads()...")
        parsed_list = json.loads(cleaned_text)

        print("Debug: Successfully parsed bug list. Returning results.")
        return parsed_list

    except Exception as e:
        print(f"Error during bug detection: {e}")
        return []
