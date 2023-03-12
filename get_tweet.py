import json, time, subprocess

class TweetGetter:
    def getTweet():
        # 1. Initiate node process
        time.sleep(1)
        process = subprocess.Popen(["node", "twitter-character-node/index.js"], stdout=subprocess.PIPE)
        output, error = process.communicate()
        print("Done with process.")

        # 2. wait
        time.sleep(10)

        # 3. read from output file
        # Opening JSON file
        with open('twitter-character-node/tweet_copy.json') as f:
            # returns JSON object as a dictionary
            data = json.load(f)
            t = data['tweet']
            f.close()
            return t
