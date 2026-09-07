import json

from groq import Groq

from app.config import GROQ_API_KEY
from app.prompts.analysis_prompt import ANALYSIS_PROMPT


client = Groq(api_key=GROQ_API_KEY)


async def analyze_text(text: str):

    prompt = ANALYSIS_PROMPT.format(text=text)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    return json.loads(content)
