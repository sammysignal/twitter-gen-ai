import openai
import requests
import random
import re
import pickle
import copy

from textblob import TextBlob

from pw import OPEN_AI_API_KEY
from pierre_logger import p_logger

# Set up the OpenAI API client
openai.api_key = OPEN_AI_API_KEY


def randomListSelection(l):
    if len(l) == 0:
        return ""
    return random.choice(l)


"""
Gets a random prompt from the list of prompts to pass to pierre.
Within a prompt:
// n=0 means return full response.
// n>0 means return up to n sentences.
@returns Prompt instance with prompt and n values.
"""

prompts = None


# get prompt by making a request to my own api json file or default. do not include separator
# string. TODO in the future, select based on time or number of past tweets.
def get_prompt():
    # try three times
    prompts = None
    # prompt = "How are you on this fine day?"
    prompt = "Who are you?"
    for i in range(3):
        try:
            prompts_response = requests.get(
                "http://sameermehra.com/assets/api/pierre-prompts.json"
            )
            prompts = prompts_response.json()
            if prompts:
                p_logger.info("Got prompts.")
                prompt = randomListSelection(prompts["prompts"])["prompt"]
                break
        except TypeError:
            p_logger.info("Connection error, trying again...")
    p_logger.info(prompt)
    return prompt


def get_sentences(t):
    return re.findall(r"([^\.!\?]+[\.!\?]+)|([^\.!\?]+$)", t)


def choose_random_sentences(t, n):
    if n <= 0:
        return t
    sentences = [i[0] for i in get_sentences(t)]
    random_index = random.randint(0, len(sentences) - 1)
    result = ""
    for i in range(n):
        if random_index + i > len(sentences) - 1:
            return result
        result = result + sentences[random_index + i]
    return result.strip()


# Remove action text from character.ai actions.
def remove_actions(tweet):
    output = ""
    add = True
    last_was_space = False
    for i in range(len(tweet)):
        if tweet[i] == "*":
            add = not add
        else:
            if last_was_space and tweet[i] == " ":
                pass
            elif add:
                output = output + tweet[i]
                if tweet[i] == " ":
                    last_was_space = True
                else:
                    last_was_space = False
    return output.strip()


def charLimit(t):
    # Twitter limit is 280, but prefer shorter tweets from Pierre.
    if len(t) <= 200:
        return t
    return ""


# Filter which returns the full sentences before 280 chars.
def getSentencesBeforeLimit(t):
    result = copy.copy(t)
    sentences = [i[0] for i in get_sentences(result)]
    while len(result) > 280:
        sentences.pop()
        result = " ".join(sentences)
    return result


def filterTweet(t):
    return getSentencesBeforeLimit(t)


def tweetIsTooDepressing(t):
    # Create a TextBlob object
    blob = TextBlob(t)

    # Calculate sentiment polarity (-1 to 1)
    sentiment_polarity = blob.sentiment.polarity

    # Print the sentiment polarity
    p_logger.info("Sentiment: " + str(sentiment_polarity))

    if sentiment_polarity < -0.5:
        p_logger.error("Tweet is too depressing!")
        return True
    return False


# Use openai's moderation api to determine if the tweet is too offensive.
def tweetIsOffensive(t):
    moderation_resp = openai.Moderation.create(input=t)
    if moderation_resp:
        return moderation_resp["results"][0]["flagged"]
    p_logger.error("Tweet is too offensive!")
    return True


# Check if tweet has already been tweeted:
def tweetHasBeenTweetedBefore(t, past_tweets):
    if t in past_tweets:
        p_logger.error("Tweet has been tweeted before.")
        return True
    return False


# Is the tweet too negative, too offfensive, or simply has been tweeted before?
def moderateTweet(t, past_tweets):
    return (
        tweetIsTooDepressing(t)
        or tweetIsOffensive(t)
        or tweetHasBeenTweetedBefore(t, past_tweets)
    )


# Adapted from https://github.com/Prateek93a/selenium-twitter-bot
class TweetGetterGPT:
    def getTweet(testing, openaiOptions):
        # Get prompt:
        prompt = get_prompt() + " ->"

        p_logger.info("prompt: " + prompt)

        # Get options from request. Default options listed in __main__
        params = copy.copy(openaiOptions)
        params["prompt"] = prompt

        # Load past tweets
        past_tweets = []
        with open("past_tweets.pkl", "rb") as f:
            try:
                past_tweets = pickle.load(f)
            except EOFError:
                pass

        tweet = None
        for i in range(5):
            # Call the OpenAI API to generate the tweet
            p_logger.info("Making a request...")
            response = openai.Completion.create(**params)

            # Read the output
            tweet = response.choices[0].text.strip()

            p_logger.info("Unfiltered Tweet: " + tweet)

            # Apply limit filtration
            filteredTweet = filterTweet(tweet)

            p_logger.info("Filtered Tweet: " + filteredTweet)

            # Apply moderation
            if moderateTweet(filteredTweet, past_tweets):
                p_logger.error("Tweet was moderated.")
                continue

            if i == 4:
                raise Exception(
                    "Could not get unique tweet! They have all been tweeted or moderated..."
                )
            break

        # If tweet has not been tweeted, add to pickle file
        with open("past_tweets.pkl", "wb") as f:
            if not testing:
                pickle.dump(past_tweets + [tweet], f)

        p_logger.info("final tweet: " + tweet)

        # Return the generated tweet
        return tweet


if __name__ == "__main__":
    # Set the test parameters for the OpenAI API request
    params = {
        # v3
        "model": "davinci:ft-personal-2023-03-21-04-04-59",
        # v2
        # 'model': 'davinci:ft-personal-2023-03-19-22-27-12',
        # v1
        # 'model': 'davinci:ft-personal-2023-03-19-03-28-50',
        "prompt": "This is a test",
        "temperature": 0.7,
        # 'frequency_penalty': 0.5,
        # 'presence_penalty': 0.5,
        "max_tokens": 70,
        "n": 1,
        "stop": "\n",
    }

    t = TweetGetterGPT.getTweet(True, params)

    print(t)

    ## get 20 tweets
    # tweets = []
    # for i in range(20):
    #     tweets.append(TweetGetterGPT.getTweet(True))
    # for j in tweets:
    #     p_logger.info(j)

    exit(0)
