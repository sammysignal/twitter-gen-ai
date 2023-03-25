import openai
import requests
import random
import re
import pickle

from pw import OPEN_AI_API_KEY

# Set up the OpenAI API client
openai.api_key = OPEN_AI_API_KEY


def main():
    prompt = "What is the meaning of life?"

    # Set the parameters for the OpenAI API request
    params = {
        'model': 'gpt-4',
        'prompt': prompt,
        'temperature': 0.9,
        # 'frequency_penalty': 1.99,
        # 'presence_penalty': 1,
        'max_tokens': 70,
        'n': 1,
        # 'stop': '\n',
    }

    # Call the OpenAI API to generate the tweet
    print("Making a request...")
    response = openai.ChatCompletion.create(**params)
    for r in response.choices:
        print(r)
    tweet = response.choices[0].text.strip()

    return tweet


if __name__ == "__main__":
    main()
    print("exiting.")
    exit(0)
