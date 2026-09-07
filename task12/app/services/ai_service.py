from groq import AsyncGroq

from app.config import GROQ_API_KEY


client = AsyncGroq(
    api_key=GROQ_API_KEY
)


async def generate_ai_response(prompt):

    response = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant.",
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content