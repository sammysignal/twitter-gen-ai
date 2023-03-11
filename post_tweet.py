import os, base64, time, traceback

from datetime import datetime

from twitter_bot_class import TwitterDriver
from pierre_logger import p_logger
from pw import U, P

# 6 hours
SLEEP_TIME = 21600

def getTweet():
    return "test"


# Post a tweet then
def postTweetLoop():
    pj = None
    while True:
        try:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            p_logger.info(dt_string)
            p_logger.info("Attempting to tweet...")
            tweetBody = getTweet()
            pj = TwitterDriver(U, P)
            pj.login()
            pj.post_tweet(tweetBody)
            p_logger.info("Tweeted: " + tweetBody)
            pj.quit()
        except Exception as e:
            p_logger.error(e)
            p_logger.error(traceback.format_exc())
            pj.quit()
            return 1
        p_logger.info("Sleeping...")
        
        # With smart plug, simply exit.
        return 0
        
        # Without smart plug, sleep for 6 hours
        # time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    exit(postTweetLoop())
    