from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_response(prompt):

    fixed_prompt=f"""
Answer the following question in valid HTML only.

Requirements:
- Use <h2>, <h3> headings.
- Use <p> for paragraphs.
- Use <ul><li> for bullet points.
- Use <pre><code> for code.
- Do not use Markdown.
- Do not include <html>, <body>, or <head> tags.

Question:
{prompt}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": fixed_prompt}
        ]
    )

    return response.choices[0].message.content