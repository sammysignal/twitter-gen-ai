import os, base64, time, logging
logging.basicConfig(filename='pierre.log', encoding='utf-8', level=logging.DEBUG)

from datetime import datetime

from twitter_bot_class import TwitterDriver
from pw import U, P

# 6 hours
SLEEP_TIME = 21600

def getTweet():
    return "test"


# Post a tweet then
def postTweetLoop():
    while True:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        logging.info(dt_string)
        logging.info("Tweetng...")
        try:
            tweetBody = getTweet()
            pj = TwitterDriver(U, P)
            pj.login()
            pj.post_tweet(tweetBody)
            logging.info("Tweeted: " + tweetBody)
            pj.quit()
        except EOFError as e:
            logging.error(e)
        logging.info("Sleeping...")
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    postTweetLoop()