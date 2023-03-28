import time
import traceback
import pickle
import requests

from filelock import Timeout, FileLock

from twitter_bot_class import TwitterDriver
from pierre_logger import p_logger
from get_tweet_gpt import TweetGetterGPT
from pw import U, P

# MAIN
# This is the main file that gets kicked off to send a tweet from PierreThePeanut account.

# 22 hours
SLEEP_TIME = 79200


# Gathers options via api, especially wether or not in test mode.
def getOptions():
    for i in range(3):
        try:
            options_response = requests.get(
                "http://sameermehra.com/assets/api/options.json"
            )
            options = options_response.json()
            if options:
                p_logger.info("Got options.")
                return options
        except TypeError:
            p_logger.info("Options - Connection error, trying again...")
    return {"testing": True}


# Returns true if we cannot tweet now, it has not been enough time.
def cannotTweet():
    # First we make sure that it has been at least 22 hours since our last tweet
    last_tweet_time = 0
    try:
        with open("last_tweet.pkl", "rb") as f:
            last_tweet_time = pickle.load(f)
    except EOFError as e:
        p_logger.error(str(e))
        return True

    time_diff = time.time() - last_tweet_time
    if time_diff < (SLEEP_TIME):
        p_logger.error(
            "Cannot tweet now, it has only been " + str(time_diff / 60) + " mins."
        )
        return True
    return False


# Post a tweet
def postTweetLoop(testing, openaiOptions):
    mode = "TEST" if testing else "LIVE"

    # Sleep to allow ChromeDriver ports to set up or smtg....
    p_logger.info("Executing post_tweet script mode = " + mode)

    if not testing:
        if cannotTweet():
            return 0

    pj = None
    while True:
        try:
            p_logger.info("Attempting to tweet! Obtaining tweet...")
            tweetBody = TweetGetterGPT.getTweet(testing, openaiOptions)
            p_logger.info("Obtained tweet: " + tweetBody)
            pj = TwitterDriver(U, P, testing)
            pj.login()
            pj.post_tweet(tweetBody)
            if (pj.driver):
                pj.quit()
            with open("last_tweet.pkl", "wb") as f:
                pickle.dump(time.time(), f)
        except Exception as e:
            p_logger.error(e)
            p_logger.error(traceback.format_exc())
            if pj:
                pj.quit()
            return 0

        # With smart plug, simply exit.
        return 0

        # Without smart plug, sleep for 6 hours
        # p_logger.info("Sleeping...")
        # time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    lock = FileLock("lock.lock", timeout=1)
    try:
        with lock:
            p_logger.info("################################")
            time.sleep(60)
            options = getOptions()
            testing = options["testing"]
            openaiOptions = options["openaiCompletionParams"]
            code = postTweetLoop(testing=testing, openaiOptions=openaiOptions)
            p_logger.info("exiting.")
            exit(code)
    except TimeoutError as e:
        print("Process is already running.")
        exit(0)
    
