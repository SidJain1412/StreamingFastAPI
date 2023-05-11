from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import config
from helper import *
import openai
import config


openai.api_key = config.OPENAI_API_KEY

app = FastAPI(
    title="Streaming API",
    description="""### API specifications\n
To test out the Streaming API `campaign_stream`, fire a sample query, then use the Curl command in your terminal to see it stream in real time\n
This doc does not support streaming outputs, but curl does.
              """,
    version=1.0,
)


def moderate_text(sent):
    # If against policy, return True
    try:
        response = openai.Moderation.create(sent)
        return response["results"][0]["flagged"]

    except Exception as e:
        print("Moderate Text Error: " + str(e))
        return 500


def moderate_handler(s):
    """
    If no issue, returns True
    If goes against policy, raise 406 error
    If some internal error, raise 500 error
    """
    ContentPolicyBreach = moderate_text(s)

    if ContentPolicyBreach == 500:
        # Error from OpenAI side, so assuming no policy breach
        return True
        # raise HTTPException(status_code=503, detail=config.error503)
        # return False
    elif ContentPolicyBreach:
        result = config.profanityError
        raise HTTPException(status_code=406, detail=result)

    return True


def get_streaming_response_openai(prompt):
    try:
        prompt = prompt
        response = openai.ChatCompletion.create(
            model=config.openai_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            n=config.max_responses,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            messages=[
                {"role": "system", "content": "You are an expert creative marketer. Create a campaign for the brand the user enters."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )
    except Exception as e:
        print("Error in creating campaigns from openAI:", str(e))
        return 503
    try:
        for chunk in response:
            current_content = chunk["choices"][0]["delta"].get("content", "")
            yield current_content
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503


@app.get(
    "/campaign_stream/",
    tags=["APIs"],
    response_model=str,
    responses={503: {"model": OverloadError}, 406: {"model": ProfanityError}},
)
def campaign_stream(prompt: str = Query(..., max_length=20)):
    if moderate_handler(prompt):
        return StreamingResponse(get_streaming_response_openai(prompt), media_type="text/event-stream")
