from selenium import webdriver
from selenium import common


# driver for raspberry pi
class GetDriver:
    def getDriver(headless):
        driver = None
        # For now always use headless, since no issues with twitter part
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
            "/usr/lib/chromium-browser/chromedriver", chrome_options=options
        )

        driver.implicitly_wait(10)  # seconds

        # if headless:
        #    options = webdriver.ChromeOptions();
        #    options.add_argument('--headless')
        #    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=options)
        # else:
        #    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')

        return driver
