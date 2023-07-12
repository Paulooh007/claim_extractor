import re
import os
from fastapi import FastAPI, UploadFile, File
import openai

app = FastAPI()


openai.api_key = os.environ.get("OPENAI_API_KEY")


def get_claims(text):
    sentences = re.split(r"(?<=[.!?])\s+", text)

    model = "ada:ft-personal-2023-05-17-17-03-33"

    results = []

    for i in range(len(sentences)):
        res = openai.Completion.create(
            model=model, prompt=sentences[i] + " ->", max_tokens=1, temperature=0
        )
        if res["choices"][0]["text"] == " True":
            results.append(sentences[i])

    return results


@app.post("/extract")
async def analyze_text(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode("latin-1")

        claims = get_claims(text)

        response = {"claims": claims}

        return response

    except Exception as e:
        error_message = {"error": str(e)}
        return error_message
