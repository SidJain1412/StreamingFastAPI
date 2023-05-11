from fastapi import FastAPI, HTTPException, Query
import openai
import os
import sys
from pydantic import BaseModel, Field

# Getting OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not len(OPENAI_API_KEY):
    print("Please set OPENAI_API_KEY environment variable. Exiting.")
    sys.exit(1)

openai.api_key = OPENAI_API_KEY

# Parameters for OpenAI
openai_model = "gpt-3.5-turbo"
max_responses = 1
temperature = 0.7
max_tokens = 512

# Defining the FastAPI app and metadata
app = FastAPI(
    title="Streaming API",
    description="""### API specifications\n
To test out the Streaming API `campaign_stream`, fire a sample query, then use the Curl command in your terminal to see it stream in real time\n
This doc does not support streaming outputs, but curl does.
              """,
    version=1.0,
)

# Defining error in case of 503 from OpenAI
error503 = "OpenAI server is busy, try again later"


# Pydantic class for 503 error
class OverloadError(BaseModel):
    detail: str = Field(default=error503)


def get_response_openai(prompt):
    try:
        prompt = prompt
        response = openai.ChatCompletion.create(
            model=openai_model,
            temperature=temperature,
            max_tokens=max_tokens,
            n=max_responses,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            messages=[
                {"role": "system", "content": "You are an expert creative marketer. Create a campaign for the brand the user enters."},
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as e:
        print("Error in creating campaigns from openAI:", str(e))
        return 503
    return response["choices"][0]["message"]["content"]


@app.get(
    "/campaign/",
    tags=["APIs"],
    response_model=str,
    responses={503: {"model": OverloadError}},
)
def campaign(prompt: str = Query(..., max_length=20)):
    return get_response_openai(prompt)
