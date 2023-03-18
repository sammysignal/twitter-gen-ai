import json, time, subprocess, random
import openai

from pw import OPEN_AI_API_KEY

# Set up the OpenAI API client
openai.api_key = OPEN_AI_API_KEY


class TweetGetterGPT:
    def getTweet():
        # Set the prompt for Pierre's tweet
        # prompt = 'Pierre the Peanut Man says:'
        prompt = "I'd like to tell you about a fictional character, and then you can generate some one-liners he might say. The character is a peanut man from Lyon, France. His name is Pierre. He is calm \
            and witty. He likes to say phrases out of context. He likes to talk about random \
                things. He likes to make up sayings, idioms, and expressions that don't exist. \
                    He does not have a filter. He is a nihilist. He smokes cigarettes, \
                        drinks coffee, and listens to jazz. He speaks in short sentences. \
                            He is bitter, but does enjoy making people laugh. He is \
                                self-deprecating, but he also likes to tease others. He has to do \
                                    it though, because he is French. \n Based on this information, please generate one-liners that Pierre might say."

        # Set the parameters for the OpenAI API request
        params = {
            'engine': 'davinci',
            'prompt': prompt,
            'temperature': 0.2,
            'max_tokens': 1712,
            'n': 1,
            'stop': '\n',
        }

        # Call the OpenAI API to generate the tweet
        response = openai.Completion.create(**params)
        for r in response.choices:
            print(r)
        tweet = response.choices[0].text.strip()

        # Return the generated tweet
        return tweet
