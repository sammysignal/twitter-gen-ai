from selenium import webdriver
from selenium import common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time, pickle, logging

# logging.basicConfig(filename='pierre.log', encoding='utf-8', level=logging.DEBUG)

from get_driver import GetDriver
from pierre_logger import p_logger


# Adapted from https://github.com/Prateek93a/selenium-twitter-bot
class TwitterDriver:

    """
    A driver class that provide features of:
        - Logging into your Twitter account
        - Liking tweets of your homepage
        - Searching for some keyword or hashtag
        - Liking tweets of the search results
        - Posting tweets
        - Logging out of your account

    ........

    Attributes
    ----------
    email : str
        user email for Twitter account
    password : str
        user password for Twitter account
    driver : WebDriver
        webdriver that carry out the automation tasks
    is_logged_in : bool
        boolean to check if the user is logged in or not

    Methods
    -------
    login()
        logs user in based on email and password provided during initialisation
    logout()
        logs user out
    search(query: str)
        searches for the provided query string
    like_tweets(cycles: int)
        loops over number of cycles provided, scrolls the page down and likes the available tweets on the page in each loop pass
    """

    def __init__(self, email, password):
        #options = webdriver.ChromeOptions()
        #options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        #chrome_driver_binary = "/Users/sammymehra/Downloads/chromedriver_mac64/chromedriver-new"
        #driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
        driver = GetDriver.getDriver()
        # Wait 10 seconds for any find to succeed, or fail
        driver.implicitly_wait(10)

        self.email = email
        self.password = password
        self.driver = driver
        self.is_logged_in = False

    # Logs in and redirects to homepage
    def login(self):
        driver = self.driver

        self.getHome()

        # check if cookies are pickled, and if so adds them to browser
        cookies = None
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
            if cookies:
                p_logger.info("Found " + str(len(cookies)) + " cookies, applying to browser")
                for cookie in cookies:
                    driver.add_cookie(cookie)
                time.sleep(2)
            else:
                p_logger.info("Could not read cookies.")
        except EOFError as e:
            p_logger.error(e)
            cookies = None

        self.getHome()
        time.sleep(10)

        if self.is_logged_in:
            return
        else:
            # Log in
            p_logger.info("Logging in with username and pass...")
            try:
                email = driver.find_element(By.CSS_SELECTOR, "[autocomplete='username']")
            except common.exceptions.NoSuchElementException:
                time.sleep(10)
                email = driver.find_element(By.CSS_SELECTOR, "[autocomplete='username']")

            email.clear()
            email.send_keys(self.email)
            time.sleep(1)
            email.send_keys(Keys.RETURN)
            p_logger.info("Waiting for password screen...")
            time.sleep(10)

            try:
                password = driver.find_element(By.CSS_SELECTOR, "[name='password']")
            except common.exceptions.NoSuchElementException:
                time.sleep(10)
                password = driver.find_element(By.CSS_SELECTOR, "[name='password']")

            p_logger.info("Entering password...")
            password.send_keys(self.password)
            time.sleep(1)
            password.send_keys(Keys.RETURN)

            time.sleep(20)

        # Try to get home again
        self.getHome()

        if not self.is_logged_in:
            raise Exception("Error logging in")
        else:
            p_logger.info("Logged in successfully")

    # Attempts to get to homepage, and if successful saves cookies. Updates is_logged_in flag.
    def getHome(self):
        self.driver.get("https://twitter.com/home")
        time.sleep(20)
        if "twitter.com/home" in self.driver.current_url:
            self.is_logged_in = True
            pickle.dump(self.driver.get_cookies(), open("cookies.pkl","wb"))
            p_logger.info("Updated cookie pickle file.")
            return
        self.is_logged_in = False


    def post_tweet(self, tweetBody):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        p_logger.info("Posting tweet...")
        driver = self.driver

        try:
            driver.find_element(By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(5)
            driver.find_element(By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']").click()
        p_logger.info("Opened tweet modal")
        time.sleep(5)
        p_logger.info("Inputting tweet...")

        try:
            driver.find_element(By.XPATH, "//div[@role='textbox']").send_keys(tweetBody)
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            driver.find_element(By.XPATH, "//div[@role='textbox']").send_keys(tweetBody)

        time.sleep(4)
        driver.find_element(By.CLASS_NAME, "notranslate").send_keys(Keys.ENTER)
        time.sleep(4)
        # driver.find_element(By.XPATH,"//div[@data-testid='tweetButton']").click()
        p_logger.info("Tweeted!")
        time.sleep(10)

    def quit(self):
        return self.driver.quit()


    ############################################
    ### Other maybe useful methods, untested ###
    ############################################

    def logout(self):
        if not self.is_logged_in:
            return

        driver = self.driver
        driver.get('https://twitter.com/home')
        time.sleep(4)

        try:
            driver.find_element(By.XPATH,
                                "//div[@data-testid='SideNav_AccountSwitcher_Button']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            driver.find_element(By.XPATH, "//div[@data-testid='SideNav_AccountSwitcher_Button']").click()

        time.sleep(1)

        try:
            driver.find_element(By.XPATH, "//a[@data-testid='AccountSwitcher_Logout_Button']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(2)
            driver.find_element(By.XPATH, "//a[@data-testid='AccountSwitcher_Logout_Button']").click()

        time.sleep(3)

        try:
            driver.find_element(By.XPATH, "//div[@data-testid='confirmationSheetConfirm']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            driver.find_element(By.XPATH, "//div[@data-testid='confirmationSheetConfirm']").click()

        time.sleep(3)
        self.is_logged_in = False

    def search(self, query=''):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        driver = self.driver

        try:
            searchbox = driver.find_element(By.XPATH, "//input[@data-testid='SearchBox_Search_Input']")
        except common.exceptions.NoSuchElementException:
            time.sleep(2)
            searchbox = driver.find_element(By.XPATH, "//input[@data-testid='SearchBox_Search_Input']")

        searchbox.clear()
        searchbox.send_keys(query)
        searchbox.send_keys(Keys.RETURN)
        time.sleep(10)

    def like_tweets(self, cycles=10):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        driver = self.driver

        for i in range(cycles):
            try:
                driver.find_element(By.XPATH,
                    "//div[@data-testid='like']").click()
            except common.exceptions.NoSuchElementException:
                time.sleep(3)
                driver.execute_script(
                    'window.scrollTo(0,document.body.scrollHeight/1.5)')
                time.sleep(3)
                driver.find_element(By.XPATH,
                    "//div[@data-testid='like']").click()

            time.sleep(1)
            driver.execute_script(
                'window.scrollTo(0,document.body.scrollHeight/1.5)')
            time.sleep(5)