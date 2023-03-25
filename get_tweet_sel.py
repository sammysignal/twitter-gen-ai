from selenium import webdriver
from selenium import common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import logging
import requests
import random
import re

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
            prompts_response = requests.get(
                "http://sameermehra.com/assets/api/pierre-prompts.json")
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
        driver.get(
            "https://beta.character.ai/chat?char=lDUsZaTzDTCFq9oj2dovbQwFE5gx0Yb2zYYuXO4UAbY")

        time.sleep(10)
        # driver.execute_script('window.localStorage.setItem("@@auth0spajs@@::dyD3gE281MqgISG7FuIXYhL2WEknqZzv::https://auth0.character.ai/::openid profile email offline_access", \
        #                       "{\"body\":{\"access_token\":\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9.eyJpc3MiOiJodHRwczovL2NoYXJhY3Rlci1haS51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTMxNDYxNzU0OTc1MDQzOTc3MzgiLCJhdWQiOlsiaHR0cHM6Ly9hdXRoMC5jaGFyYWN0ZXIuYWkvIiwiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY3ODQxNTAxNiwiZXhwIjoxNjgxMDA3MDE2LCJhenAiOiJkeUQzZ0UyODFNcWdJU0c3RnVJWFloTDJXRWtucVp6diIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.YZxhFx2c5e-D9CuNVC8QirNjjC3vhWbr-D-YzZAYgVtoaSaqa94VBPAMuxo9iCXhLvxjKWtFh8uqHgslMBenfjq-dgUGzVhiX9TEY7F7Sqkc8qBiaA4BJ8hT8md6iZAAde2ofSGxPJcjSUb6BWVmhtpSWbuPsA73USpEfc9qvJw6Yw_LfWuZzmAG3jl2fyjKuMQ6n1j3kV30vP5F7DQQKWzOfjm4QRaMIohGYyvSSLC9C_pX-Bu4LEpXw_2qFRDKqW4-p4grBknBqQ2TK65_XGT2BB31C-BQD_iBsvPQAZNRXi2BPUg43mcRELXxuXfxRoAzcDOYVHBNjxXle196KA\",\"id_token\":\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9.eyJnaXZlbl9uYW1lIjoiU2FtZWVyIiwiZmFtaWx5X25hbWUiOiJNZWhyYSIsIm5pY2tuYW1lIjoic2FtbXlzaWduYWwiLCJuYW1lIjoiU2FtZWVyIE1laHJhIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FHTm15eGJkeUU5Mm52LTdmZnBFY1NUZEMtRjIyYktVbkpiN3RaS0FDTWNFPXM5Ni1jIiwibG9jYWxlIjoiZW4iLCJ1cGRhdGVkX2F0IjoiMjAyMy0wMy0xMFQwMjoyMzozNS4xNzZaIiwiZW1haWwiOiJzYW1teXNpZ25hbEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tLyIsImF1ZCI6ImR5RDNnRTI4MU1xZ0lTRzdGdUlYWWhMMldFa25xWnp2IiwiaWF0IjoxNjc4NDE1MDE2LCJleHAiOjE2ODIwMTUwMTYsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTEzMTQ2MTc1NDk3NTA0Mzk3NzM4Iiwic2lkIjoib19yTkU2Z1dKaGd0aEg0QzVJOFVqNjJ1aVNLMlBsQ3kiLCJub25jZSI6ImNIWklVVkpLUmtORE1HdFVZazVKUWpGRFYxcFVVblJLZmpSWGNrOWlPV0ZDWjFCUldtUk9aMEZ5Zmc9PSJ9.v7Xx03toskmDSOa9k-YWSjEigj5OItWaWb-7-uS7qc-6UIlG2OoAQyPQnOCTqo_EsXTRUVQcvHMKsfY1f2VFUbejpQk9yy6suoVfneJE-C7cj2gqo9RsMudKVxOd47entmjvXAV58KSBiDVv_UD8hiyYbqudk2rrwdE7PVZmOhUs8Z5vGdGgW8VZ0W8Ny6sDjwtQ9Z5WYhHTGV2lAkt0SV7h8FSWhhF9p3MUaDzJvzx7qGJq_NssMhcG97AyT6sFqwWVNLM0JqYskTIqARgeRrh_ZP4yX0BmUwsD1Kg6JPUM3SkD_9RpHVz-M58UEjkh3oQssDSSvZ72JtcsvWB4_Q\",\
        #                         \"scope\":\"openid profile email offline_access\",\"expires_in\":2592000,\"token_type\":\"Bearer\",\
        #                         \"decodedToken\":{\"encoded\":{\"header\":\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9\",\"payload\":\"eyJnaXZlbl9uYW1lIjoiU2FtZWVyIiwiZmFtaWx5X25hbWUiOiJNZWhyYSIsIm5pY2tuYW1lIjoic2FtbXlzaWduYWwiLCJuYW1lIjoiU2FtZWVyIE1laHJhIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FHTm15eGJkeUU5Mm52LTdmZnBFY1NUZEMtRjIyYktVbkpiN3RaS0FDTWNFPXM5Ni1jIiwibG9jYWxlIjoiZW4iLCJ1cGRhdGVkX2F0IjoiMjAyMy0wMy0xMFQwMjoyMzozNS4xNzZaIiwiZW1haWwiOiJzYW1teXNpZ25hbEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tLyIsImF1ZCI6ImR5RDNnRTI4MU1xZ0lTRzdGdUlYWWhMMldFa25xWnp2IiwiaWF0IjoxNjc4NDE1MDE2LCJleHAiOjE2ODIwMTUwMTYsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTEzMTQ2MTc1NDk3NTA0Mzk3NzM4Iiwic2lkIjoib19yTkU2Z1dKaGd0aEg0QzVJOFVqNjJ1aVNLMlBsQ3kiLCJub25jZSI6ImNIWklVVkpLUmtORE1HdFVZazVKUWpGRFYxcFVVblJLZmpSWGNrOWlPV0ZDWjFCUldtUk9aMEZ5Zmc9PSJ9\",\"signature\":\"v7Xx03toskmDSOa9k-YWSjEigj5OItWaWb-7-uS7qc-6UIlG2OoAQyPQnOCTqo_EsXTRUVQcvHMKsfY1f2VFUbejpQk9yy6suoVfneJE-C7cj2gqo9RsMudKVxOd47entmjvXAV58KSBiDVv_UD8hiyYbqudk2rrwdE7PVZmOhUs8Z5vGdGgW8VZ0W8Ny6sDjwtQ9Z5WYhHTGV2lAkt0SV7h8FSWhhF9p3MUaDzJvzx7qGJq_NssMhcG97AyT6sFqwWVNLM0JqYskTIqARgeRrh_ZP4yX0BmUwsD1Kg6JPUM3SkD_9RpHVz-M58UEjkh3oQssDSSvZ72JtcsvWB4_Q\"},\"header\":{\"alg\":\"RS256\",\"typ\":\"JWT\",\"kid\":\"EjblWRUBXDI_GC92Bkcuc\"},\"claims\":{\"__raw\":\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9.eyJnaXZlbl9uYW1lIjoiU2FtZWVyIiwiZmFtaWx5X25hbWUiOiJNZWhyYSIsIm5pY2tuYW1lIjoic2FtbXlzaWduYWwiLCJuYW1lIjoiU2FtZWVyIE1laHJhIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FHTm15eGJkeUU5Mm52LTdmZnBFY1NUZEMtRjIyYktVbkpiN3RaS0FDTWNFPXM5Ni1jIiwibG9jYWxlIjoiZW4iLCJ1cGRhdGVkX2F0IjoiMjAyMy0wMy0xMFQwMjoyMzozNS4xNzZaIiwiZW1haWwiOiJzYW1teXNpZ25hbEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tLyIsImF1ZCI6ImR5RDNnRTI4MU1xZ0lTRzdGdUlYWWhMMldFa25xWnp2IiwiaWF0IjoxNjc4NDE1MDE2LCJleHAiOjE2ODIwMTUwMTYsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTEzMTQ2MTc1NDk3NTA0Mzk3NzM4Iiwic2lkIjoib19yTkU2Z1dKaGd0aEg0QzVJOFVqNjJ1aVNLMlBsQ3kiLCJub25jZSI6ImNIWklVVkpLUmtORE1HdFVZazVKUWpGRFYxcFVVblJLZmpSWGNrOWlPV0ZDWjFCUldtUk9aMEZ5Zmc9PSJ9.v7Xx03toskmDSOa9k-YWSjEigj5OItWaWb-7-uS7qc-6UIlG2OoAQyPQnOCTqo_EsXTRUVQcvHMKsfY1f2VFUbejpQk9yy6suoVfneJE-C7cj2gqo9RsMudKVxOd47entmjvXAV58KSBiDVv_UD8hiyYbqudk2rrwdE7PVZmOhUs8Z5vGdGgW8VZ0W8Ny6sDjwtQ9Z5WYhHTGV2lAkt0SV7h8FSWhhF9p3MUaDzJvzx7qGJq_NssMhcG97AyT6sFqwWVNLM0JqYskTIqARgeRrh_ZP4yX0BmUwsD1Kg6JPUM3SkD_9RpHVz-M58UEjkh3oQssDSSvZ72JtcsvWB4_Q\",\"given_name\":\"Sameer\",\"family_name\":\"Mehra\",\"nickname\":\"sammysignal\",\"name\":\"Sameer Mehra\",\"picture\":\"https://lh3.googleusercontent.com/a/AGNmyxbdyE92nv-7ffpEcSTdC-F22bKUnJb7tZKACMcE=s96-c\",\"locale\":\"en\",\"updated_at\":\"2023-03-10T02:23:35.176Z\",\"email\":\"sammysignal@gmail.com\",\"email_verified\":true,\"iss\":\"https://character-ai.us.auth0.com/\",\"aud\":\"dyD3gE281MqgISG7FuIXYhL2WEknqZzv\",\"iat\":1678415016,\"exp\":1682015016,\"sub\":\"google-oauth2|113146175497504397738\",\"sid\":\"o_rNE6gWJhgthH4C5I8Uj62uiSK2PlCy\",\"nonce\":\"cHZIUVJKRkNDMGtUYk5JQjFDV1pUUnRKfjRXck9iOWFCZ1BRWmROZ0Fyfg==\"},\"user\":{\"given_name\":\"Sameer\",\"family_name\":\"Mehra\",\"nickname\":\"sammysignal\",\"name\":\"Sameer Mehra\",\"picture\":\"https://lh3.googleusercontent.com/a/AGNmyxbdyE92nv-7ffpEcSTdC-F22bKUnJb7tZKACMcE=s96-c\",\"locale\":\"en\",\"updated_at\":\"2023-03-10T02:23:35.176Z\",\"email\":\"sammysignal@gmail.com\",\"email_verified\":true,\"sub\":\"google-oauth2|113146175497504397738\"}},\"audience\":\"https://auth0.character.ai/\",\"oauthTokenScope\":\"openid profile email\",\"client_id\":\"dyD3gE281MqgISG7FuIXYhL2WEknqZzv\"},\"expiresAt\":1681007016}")')

        driver.execute_script('window.localStorage.setItem("@@auth0spajs@@::dyD3gE281MqgISG7FuIXYhL2WEknqZzv::https://auth0.character.ai/::openid profile email offline_access", \
                              "{\\"body\\":{\\"access_token\\":\\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9.eyJpc3MiOiJodHRwczovL2NoYXJhY3Rlci1haS51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTMxNDYxNzU0OTc1MDQzOTc3MzgiLCJhdWQiOlsiaHR0cHM6Ly9hdXRoMC5jaGFyYWN0ZXIuYWkvIiwiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY3ODQxNTAxNiwiZXhwIjoxNjgxMDA3MDE2LCJhenAiOiJkeUQzZ0UyODFNcWdJU0c3RnVJWFloTDJXRWtucVp6diIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.YZxhFx2c5e-D9CuNVC8QirNjjC3vhWbr-D-YzZAYgVtoaSaqa94VBPAMuxo9iCXhLvxjKWtFh8uqHgslMBenfjq-dgUGzVhiX9TEY7F7Sqkc8qBiaA4BJ8hT8md6iZAAde2ofSGxPJcjSUb6BWVmhtpSWbuPsA73USpEfc9qvJw6Yw_LfWuZzmAG3jl2fyjKuMQ6n1j3kV30vP5F7DQQKWzOfjm4QRaMIohGYyvSSLC9C_pX-Bu4LEpXw_2qFRDKqW4-p4grBknBqQ2TK65_XGT2BB31C-BQD_iBsvPQAZNRXi2BPUg43mcRELXxuXfxRoAzcDOYVHBNjxXle196KA\\",\\"id_token\\":\\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9.eyJnaXZlbl9uYW1lIjoiU2FtZWVyIiwiZmFtaWx5X25hbWUiOiJNZWhyYSIsIm5pY2tuYW1lIjoic2FtbXlzaWduYWwiLCJuYW1lIjoiU2FtZWVyIE1laHJhIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FHTm15eGJkeUU5Mm52LTdmZnBFY1NUZEMtRjIyYktVbkpiN3RaS0FDTWNFPXM5Ni1jIiwibG9jYWxlIjoiZW4iLCJ1cGRhdGVkX2F0IjoiMjAyMy0wMy0xMFQwMjoyMzozNS4xNzZaIiwiZW1haWwiOiJzYW1teXNpZ25hbEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tLyIsImF1ZCI6ImR5RDNnRTI4MU1xZ0lTRzdGdUlYWWhMMldFa25xWnp2IiwiaWF0IjoxNjc4NDE1MDE2LCJleHAiOjE2ODIwMTUwMTYsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTEzMTQ2MTc1NDk3NTA0Mzk3NzM4Iiwic2lkIjoib19yTkU2Z1dKaGd0aEg0QzVJOFVqNjJ1aVNLMlBsQ3kiLCJub25jZSI6ImNIWklVVkpLUmtORE1HdFVZazVKUWpGRFYxcFVVblJLZmpSWGNrOWlPV0ZDWjFCUldtUk9aMEZ5Zmc9PSJ9.v7Xx03toskmDSOa9k-YWSjEigj5OItWaWb-7-uS7qc-6UIlG2OoAQyPQnOCTqo_EsXTRUVQcvHMKsfY1f2VFUbejpQk9yy6suoVfneJE-C7cj2gqo9RsMudKVxOd47entmjvXAV58KSBiDVv_UD8hiyYbqudk2rrwdE7PVZmOhUs8Z5vGdGgW8VZ0W8Ny6sDjwtQ9Z5WYhHTGV2lAkt0SV7h8FSWhhF9p3MUaDzJvzx7qGJq_NssMhcG97AyT6sFqwWVNLM0JqYskTIqARgeRrh_ZP4yX0BmUwsD1Kg6JPUM3SkD_9RpHVz-M58UEjkh3oQssDSSvZ72JtcsvWB4_Q\\",\
                                \\"scope\\":\\"openid profile email offline_access\\",\\"expires_in\\":2592000,\\"token_type\\":\\"Bearer\\",\
                                \\"decodedToken\\":{\\"encoded\\":{\\"header\\":\\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9\\",\\"payload\\":\\"eyJnaXZlbl9uYW1lIjoiU2FtZWVyIiwiZmFtaWx5X25hbWUiOiJNZWhyYSIsIm5pY2tuYW1lIjoic2FtbXlzaWduYWwiLCJuYW1lIjoiU2FtZWVyIE1laHJhIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FHTm15eGJkeUU5Mm52LTdmZnBFY1NUZEMtRjIyYktVbkpiN3RaS0FDTWNFPXM5Ni1jIiwibG9jYWxlIjoiZW4iLCJ1cGRhdGVkX2F0IjoiMjAyMy0wMy0xMFQwMjoyMzozNS4xNzZaIiwiZW1haWwiOiJzYW1teXNpZ25hbEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tLyIsImF1ZCI6ImR5RDNnRTI4MU1xZ0lTRzdGdUlYWWhMMldFa25xWnp2IiwiaWF0IjoxNjc4NDE1MDE2LCJleHAiOjE2ODIwMTUwMTYsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTEzMTQ2MTc1NDk3NTA0Mzk3NzM4Iiwic2lkIjoib19yTkU2Z1dKaGd0aEg0QzVJOFVqNjJ1aVNLMlBsQ3kiLCJub25jZSI6ImNIWklVVkpLUmtORE1HdFVZazVKUWpGRFYxcFVVblJLZmpSWGNrOWlPV0ZDWjFCUldtUk9aMEZ5Zmc9PSJ9\\",\\"signature\\":\\"v7Xx03toskmDSOa9k-YWSjEigj5OItWaWb-7-uS7qc-6UIlG2OoAQyPQnOCTqo_EsXTRUVQcvHMKsfY1f2VFUbejpQk9yy6suoVfneJE-C7cj2gqo9RsMudKVxOd47entmjvXAV58KSBiDVv_UD8hiyYbqudk2rrwdE7PVZmOhUs8Z5vGdGgW8VZ0W8Ny6sDjwtQ9Z5WYhHTGV2lAkt0SV7h8FSWhhF9p3MUaDzJvzx7qGJq_NssMhcG97AyT6sFqwWVNLM0JqYskTIqARgeRrh_ZP4yX0BmUwsD1Kg6JPUM3SkD_9RpHVz-M58UEjkh3oQssDSSvZ72JtcsvWB4_Q\\"},\\"header\\":{\\"alg\\":\\"RS256\\",\\"typ\\":\\"JWT\\",\\"kid\\":\\"EjblWRUBXDI_GC92Bkcuc\\"},\\"claims\\":{\\"__raw\\":\\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9.eyJnaXZlbl9uYW1lIjoiU2FtZWVyIiwiZmFtaWx5X25hbWUiOiJNZWhyYSIsIm5pY2tuYW1lIjoic2FtbXlzaWduYWwiLCJuYW1lIjoiU2FtZWVyIE1laHJhIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FHTm15eGJkeUU5Mm52LTdmZnBFY1NUZEMtRjIyYktVbkpiN3RaS0FDTWNFPXM5Ni1jIiwibG9jYWxlIjoiZW4iLCJ1cGRhdGVkX2F0IjoiMjAyMy0wMy0xMFQwMjoyMzozNS4xNzZaIiwiZW1haWwiOiJzYW1teXNpZ25hbEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tLyIsImF1ZCI6ImR5RDNnRTI4MU1xZ0lTRzdGdUlYWWhMMldFa25xWnp2IiwiaWF0IjoxNjc4NDE1MDE2LCJleHAiOjE2ODIwMTUwMTYsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTEzMTQ2MTc1NDk3NTA0Mzk3NzM4Iiwic2lkIjoib19yTkU2Z1dKaGd0aEg0QzVJOFVqNjJ1aVNLMlBsQ3kiLCJub25jZSI6ImNIWklVVkpLUmtORE1HdFVZazVKUWpGRFYxcFVVblJLZmpSWGNrOWlPV0ZDWjFCUldtUk9aMEZ5Zmc9PSJ9.v7Xx03toskmDSOa9k-YWSjEigj5OItWaWb-7-uS7qc-6UIlG2OoAQyPQnOCTqo_EsXTRUVQcvHMKsfY1f2VFUbejpQk9yy6suoVfneJE-C7cj2gqo9RsMudKVxOd47entmjvXAV58KSBiDVv_UD8hiyYbqudk2rrwdE7PVZmOhUs8Z5vGdGgW8VZ0W8Ny6sDjwtQ9Z5WYhHTGV2lAkt0SV7h8FSWhhF9p3MUaDzJvzx7qGJq_NssMhcG97AyT6sFqwWVNLM0JqYskTIqARgeRrh_ZP4yX0BmUwsD1Kg6JPUM3SkD_9RpHVz-M58UEjkh3oQssDSSvZ72JtcsvWB4_Q\\",\\"given_name\\":\\"Sameer\\",\\"family_name\\":\\"Mehra\\",\\"nickname\\":\\"sammysignal\\",\\"name\\":\\"Sameer Mehra\\",\\"picture\\":\\"https://lh3.googleusercontent.com/a/AGNmyxbdyE92nv-7ffpEcSTdC-F22bKUnJb7tZKACMcE=s96-c\\",\\"locale\\":\\"en\\",\\"updated_at\\":\\"2023-03-10T02:23:35.176Z\\",\\"email\\":\\"sammysignal@gmail.com\\",\\"email_verified\\":true,\\"iss\\":\\"https://character-ai.us.auth0.com/\\",\\"aud\\":\\"dyD3gE281MqgISG7FuIXYhL2WEknqZzv\\",\\"iat\\":1678415016,\\"exp\\":1682015016,\\"sub\\":\\"google-oauth2|113146175497504397738\\",\\"sid\\":\\"o_rNE6gWJhgthH4C5I8Uj62uiSK2PlCy\\",\\"nonce\\":\\"cHZIUVJKRkNDMGtUYk5JQjFDV1pUUnRKfjRXck9iOWFCZ1BRWmROZ0Fyfg==\\"},\\"user\\":{\\"given_name\\":\\"Sameer\\",\\"family_name\\":\\"Mehra\\",\\"nickname\\":\\"sammysignal\\",\\"name\\":\\"Sameer Mehra\\",\\"picture\\":\\"https://lh3.googleusercontent.com/a/AGNmyxbdyE92nv-7ffpEcSTdC-F22bKUnJb7tZKACMcE=s96-c\\",\\"locale\\":\\"en\\",\\"updated_at\\":\\"2023-03-10T02:23:35.176Z\\",\\"email\\":\\"sammysignal@gmail.com\\",\\"email_verified\\":true,\\"sub\\":\\"google-oauth2|113146175497504397738\\"}},\\"audience\\":\\"https://auth0.character.ai/\\",\\"oauthTokenScope\\":\\"openid profile email\\",\\"client_id\\":\\"dyD3gE281MqgISG7FuIXYhL2WEknqZzv\\"},\\"expiresAt\\":1681007016}")')

        time.sleep(1)
        driver.get(
            "https://beta.character.ai/chat?char=lDUsZaTzDTCFq9oj2dovbQwFE5gx0Yb2zYYuXO4UAbY")
        time.sleep(15)
        # check if cookies are pickled, and if so adds them to browser
        # cookies = None
        # try:
        #     cookies = pickle.load(open("cookies_ai.pkl", "rb"))
        #     if cookies:
        #         print("Found " + str(len(cookies)) +
        #               " cookies, applying to browser")
        #         for cookie in cookies:
        #             driver.add_cookie(cookie)
        #         time.sleep(1)
        #     else:
        #         print("Could not read cookies.")
        # except EOFError as e:
        #     print(e)
        #     cookies = None

        # time.sleep(20)

        # If Welcome modal opens, dismiss it
        try:
            send_button = driver.find_element(
                By.CSS_SELECTOR, "[id='#AcceptButton']")
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

        send_button = driver.find_element(
            By.CSS_SELECTOR, ".input-group > button:nth-child(2)")

        print("found send button")
        send_button.click()

        # time.sleep(15)

        # Wait for three messages to be present.
        try:
            WebDriverWait(driver, 1000).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".msg-row:nth-child(4)"))
            )
            print("found 4th element!")
            time.sleep(8)
        finally:
            driver.quit()

        character_messages = driver.find_elements(
            By.CSS_SELECTOR, ".msg.char-msg:last-child")

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
                pickle.dump(
                    existing_tweets + [filtered_tweet], open("tweets_collection.pkl", "wb"))
            else:
                print("Could not read existing tweets.")
        except EOFError as e:
            print(e)


if __name__ == "__main__":
    TweetGetterSel.getTweet(GetDriver().getDriver())
    print("exiting.")
    exit(0)
