# Login to websites
# some websites have saved autofill in cache
# others need programmatic entry

import reader
import os

def login_website(website_name, url):
    print('\n===Login Website===\n')

    usr_key = website_name.upper() + '_USR'
    pwd_key = website_name.upper() + '_PWD'

    usr = os.environ[usr_key]
    pwd = os.environ[pwd_key]

    # open website
    driver = reader.open_react_website(url)

    # driver.find_element_by_xpath('//input[@node-type="searchInput"]')
    login_btn = driver.find_element('xpath', '//input[@data-testid="signin"]')
    print('login_btn: ' + login_btn.get_attribute('innerHTML'))



website_name = 'betmgm'
url = 'https://sports.ny.betmgm.com/en/sports/baseball-23/betting/usa-9/mlb-75'
login_website(website_name, url)