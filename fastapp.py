from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import config
from helper import *
import time

app = FastAPI(
    title="Streaming API",
    description="""### API specifications\n
To test out the Streaming API `campaign_stream`, fire a sample query, then use the Curl command in your terminal to see it stream in real time\n
This doc does not support streaming outputs, but curl does.
              """,
    version=1.0,
)


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


@app.get(
    "/campaign_stream/",
    tags=["APIs"],
    response_model=str,
    responses={503: {"model": OverloadError}, 406: {"model": ProfanityError}},
)
def campaign_stream(prompt: str = Query(..., max_length=20)):
    if moderate_handler(prompt):
        return StreamingResponse(get_streaming_response_openai(prompt), media_type="text/event-stream")
