import os
import base64
from twitter_bot_class import TwitterDriver

if __name__ == "__main__":
    try:
        pj = TwitterDriver(U, P)
        pj.login()
        # pj.post_tweet("My bot's first tweet!")
        pj.logout()
    except Exception as e:
        pj.logout()
        print(e)
