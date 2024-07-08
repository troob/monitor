# webdriver tests
# For profile to work with webdriver
# Need to close all other chrome windows
# Cannot even use other windows in diff profile
# bc otherwise webdriver assumes chrome crashed bc confused
# ideally would make code understand what is happening but that is more work

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

#create chromeoptions instance
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
# options.add_argument("--no-sandbox")

#provide location where chrome stores profiles
# maybe /home/username/.config/google-chrome???
# /Users/m/Library/Application Support/Google/Chrome
options.add_argument(r"--user-data-dir=/Users/m/Library/Application Support/Google/Chrome")

#provide the profile name with which we want to open browser
options.add_argument(r'--profile-directory=Default')

#specify where your chrome driver present in your pc
# export PATH=$PATH:/opt/homebrew/bin/chromedriver
#chromedriver = '/opt/homebrew/bin/'
driver = webdriver.Chrome(options=options)

#provide website url here
driver.get("https://omayo.blogspot.com/")

#find element using its id
print(driver.find_element("id","home").text)

time.sleep(100)