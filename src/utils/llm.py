import os

from openai import OpenAI


class LLM:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def get_answer(self, question):
        response = self.openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content
