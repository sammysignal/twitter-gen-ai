import os, base64, time, traceback, pickle

from datetime import datetime

from twitter_bot_class import TwitterDriver
from pierre_logger import p_logger
from pw import U, P

# 6 hours
SLEEP_TIME = 21600

def getTweet():
    return "test"

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
        p_logger.error("Cannot tweet now, it has only been " + str(time_diff / 60) + " mins.")
        return True
    return False

# Post a tweet then
def postTweetLoop(override=False):
    # Sleep to allow ChromeDriver ports to set up or smtg....
    time.sleep(20)
    
    if cannotTweet() and not override:
        return(0)

    pj = None
    while True:
        try:
            p_logger.info("######################")
            p_logger.info("Attempting to tweet...")
            tweetBody = getTweet()
            pj = TwitterDriver(U, P, headless=True)
            pj.login()
            pj.post_tweet(tweetBody)
            p_logger.info("Tweeted: " + tweetBody)
            pj.quit()
            with open("last_tweet.pkl","wb") as f:
                pickle.dump(time.time(), f)
        except Exception as e:
            p_logger.error(e)
            p_logger.error(traceback.format_exc())
            pj.quit()
            return 0
        p_logger.info("Sleeping...")
        
        # With smart plug, simply exit.
        return 0
        
        # Without smart plug, sleep for 6 hours
        # time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    exit(postTweetLoop(override=False))
    