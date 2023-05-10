import sys
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not len(OPENAI_API_KEY):
    print("Please set OPENAI_API_KEY environment variable. Exiting.")
    sys.exit(1)

profanityError = "Input sentence is against the content policy."
error503 = "OpenAI server is busy, try again later"
promptPrefix = ""
openai_model = "gpt-3.5-turbo"
max_responses = 1
temperature = 0.7
max_tokens = 512
