import os, base64, time
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
        print(dt_string)
        print("Tweetng...")
        try:
            tweetBody = getTweet()
            pj = TwitterDriver(U, P)
            pj.login()
            pj.post_tweet(tweetBody)
            print("Tweeted: " + tweetBody)
            pj.quit()
        except EOFError as e:
            print(e)
        print("Sleeping...")  
        time.sleep(SLEEP_TIME)
        

if __name__ == "__main__":
    postTweetLoop()