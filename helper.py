from pydantic import BaseModel, Field
import openai
import config


openai.api_key = config.OPENAI_API_KEY


def moderate_text(sent):
    # If against policy, return True
    try:
        response = openai.Moderation.create(sent)
        return response["results"][0]["flagged"]

    except Exception as e:
        print("Moderate Text Error: " + str(e))
        return 500


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
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
    except Exception as e:
        print("Error in creating campaigns from openAI:", str(e))
        return 503
    try:
        for chunk in response:
            current_content = chunk["choices"][0]["delta"].get("content", "").replace("\n", "").replace('"', "")
            yield current_content
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503


class OverloadError(BaseModel):
    detail: str = Field(default=config.error503)


class ProfanityError(BaseModel):
    detail: str = Field(default=config.profanityError)
