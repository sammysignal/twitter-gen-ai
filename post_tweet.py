import time
import traceback
import pickle
from twitter_bot_class import TwitterDriver
from pierre_logger import p_logger
from get_tweet_gpt import TweetGetterGPT
from pw import U, P

# MAIN
# This is the main file that gets kicked off to send a tweet from PierreThePeanut account.

# 6 hours
SLEEP_TIME = 21600

# False indicates production state
TESTING = True


def cannotTweet():
    # First we make sure that it has been at least 5.5 hours since our last tweet
    last_tweet_time = 0
    try:
        with open("last_tweet.pkl", "rb") as f:
            last_tweet_time = pickle.load(f)
    except EOFError as e:
        p_logger.error(str(e))
        return True

    time_diff = time.time() - last_tweet_time
    if time_diff < (SLEEP_TIME * 0.95):
        p_logger.error("Cannot tweet now, it has only been " +
                       str(time_diff / 60) + " mins.")
        return True
    return False

# Post a tweet then


def postTweetLoop(testing):
    mode = "TEST" if TESTING else "LIVE"

    # Sleep to allow ChromeDriver ports to set up or smtg....
    p_logger.info("Executing post_tweet script mode = " + mode)

    time.sleep(60)

    if not testing:
        if cannotTweet():
            return (0)

    pj = None
    while True:
        try:
            p_logger.info("Attempting to tweet! Obtaining tweet...")
            tweetBody = TweetGetterGPT.getTweet(testing)
            p_logger.info("Obtained tweet: " + tweetBody)
            pj = TwitterDriver(U, P, testing)
            pj.login()
            pj.post_tweet(tweetBody)
            pj.quit()
            with open("last_tweet.pkl", "wb") as f:
                pickle.dump(time.time(), f)
        except Exception as e:
            p_logger.error(e)
            p_logger.error(traceback.format_exc())
            pj.quit()
            return 0

        # With smart plug, simply exit.
        return 0

        # Without smart plug, sleep for 6 hours
        # p_logger.info("Sleeping...")
        # time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    p_logger.info("######################")
    code = postTweetLoop(testing=TESTING)
    p_logger.info("exiting.")
    exit(code)
