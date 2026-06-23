from google import genai
import os


def analyze_report(report):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "GEMINI_API_KEY not found"

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
You are a website monitoring expert.

Analyze this report:

Status Code:
{report['status_code']}

Response Time:
{report['response_time']} seconds

Console Errors:
{report['console_errors']}

Issues:
{report['issues']}

Provide:
1. Overall Health
2. Problems Found
3. Recommendations
4. Severity
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text