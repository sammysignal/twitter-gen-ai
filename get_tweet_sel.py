from selenium import webdriver
from selenium import common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time, pickle, logging, requests, random, re

# logging.basicConfig(filename='pierre.log', encoding='utf-8', level=logging.DEBUG)

from get_driver import GetDriver

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
def get_prompt():
    # try three times
    prompts = None
    for i in range(3):
        try:
            prompts_response = requests.get("http://sameermehra.com/assets/api/pierre-prompts.json")
            prompts = prompts_response.json()
            if prompts:
                print("Got prompts.")
                break
        except TypeError:
            print("Connection error, trying again...")
    p = randomListSelection(prompts["prompts"])
    print(p)
    return p

def get_sentences(t):
    return re.findall(r'([^\.!\?]+[\.!\?]+)|([^\.!\?]+$)', t)

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

def filterTweet(t, p):
  t1 = remove_actions(t)
  t2 = choose_random_sentences(t1, p["n"])
  t3 = charLimit(t2)
  return t3

# Adapted from https://github.com/Prateek93a/selenium-twitter-bot
class TweetGetterSel:
    def getTweet(driver):
        print("start")
        driver.get("https://beta.character.ai/chat?char=lDUsZaTzDTCFq9oj2dovbQwFE5gx0Yb2zYYuXO4UAbY")
        time.sleep(20)

        # If Welcome modal opens, dismiss it
        try:
            send_button = driver.find_element(By.CSS_SELECTOR, "[id='#AcceptButton']")
            if send_button:
                time.sleep(1)
                send_button.click()
                time.sleep(1)
            else:
                print("Could not find accept button.")
        except common.exceptions.NoSuchElementException as e:
            print(e)

        user_input_el = driver.find_element(By.CSS_SELECTOR, "#user-input")

        print("got input el")
        prompt = get_prompt()

        print("got prompt: " + str(prompt))

        user_input_el.send_keys(prompt["prompt"])

        time.sleep(1)

        # Get send button

        send_button = driver.find_element(By.CSS_SELECTOR, ".input-group > button:nth-child(2)")

        print("found send button")
        send_button.click()

        time.sleep(15)

        character_messages = driver.find_elements(By.CSS_SELECTOR, ".msg.char-msg:last-child")


        print("got character_messages: " + str(character_messages))
        last_message = character_messages[-1]

        character_output = last_message.get_attribute("innerText")

        print("character_output: " + str(character_output))

        driver.quit()

        filtered_tweet = filterTweet(character_output)

        # Add to tweets pkl
        try:
            existing_tweets = pickle.load(open("tweets_collection.pkl", "rb"))
            if existing_tweets:
                pickle.dump(existing_tweets + [filtered_tweet], open("tweets_collection.pkl","wb"))
            else:
                print("Could not read existing tweets.")
        except EOFError as e:
            print(e)

if __name__ == "__main__":
    TweetGetterSel.getTweet(GetDriver().getDriver())
    print("exiting.")
    exit(0)
