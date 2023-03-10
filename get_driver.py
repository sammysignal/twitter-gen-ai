from selenium import webdriver
from selenium import common

# driver for chromium local mac

#def getDriver():
#    options = webdriver.ChromeOptions()
#    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
#    chrome_driver_binary = "/Users/sammymehra/Downloads/chromedriver_mac64/chromedriver-new"
#    driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

# driver for raspberry pi
HEADLESS = False

class GetDriver:
    def getDriver():
        if HEADLESS:
            from pyvirtualdisplay import Display
            display = Display(visible=0, size=(1500, 1100))
            display.start()
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
        return driver