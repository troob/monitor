# monitor-client.py
# monitor-client is exactly same as monitor
# but monitor slack instead of oddsview

import reader
import time

# open GUI

# open chromedriver to slack ev/arb channels

def monitor_client(client_url):
    print('\n===Monitor Client===\n')

    # click open in browser
    # get by parent element: class p-ssb_redirect__loading_messages > <a>
    # OR direct: data-qa="ssb_redirect_open_in_browser"

    # read slack channel by api. no webdriver
    # but keep betrivers window open
    website = reader.open_dynamic_website(client_url)
    driver = website[0]

    prev_last_list_item = None # get from saved log last run

    # keep looping waiting for change
    while True:

        print('Monitor Client')
        #time.sleep(100)

        # Read EV Data
        # jump to new messages
        # class="c-button-unstyled c-message_list__day_divider__label__pill"

        # list of messages
        # class="c-virtual_list__item"
        list_items = driver.find_elements('class name', 'c-virtual_list__item')
        print('num list_items: ' + str(len(list_items)))

        last_list_item = list_items[-1]
        print('last_list_item: ' + last_list_item.get_attribute('innerHTML'))

        # Message Content
        # div role="presentation" class="c-message_kit__gutter__right" data-qa="message_content"

        

        # Monitor New Picks
        if last_list_item != prev_last_list_item:
            print('New Pick')

        prev_last_list_item = last_list_item

        # Send Test New Pick

        time.sleep(3)


# href="https://ball-aep6514.slack.com/"
# https://ball-aep6514.slack.com/ssb/redirect
# links to workspace but asks for desktop
# client_url = 'https://join.slack.com/t/ball-aep6514/shared_invite/zt-2s5k1emwh-tB~QR4nEGCasjxx6Q6DR3A'
# goes direct to browser app
#client_url = 'https://ball-aep6514.slack.com/'
# client = slack
# monitors all channels
# given workspace token
# token saved as environment variable
# must be encrypted to prevent sharing
# need to save environment variable on internet server
# but for test just code into app
# and check code encrypted when compiled
monitor_client()




# Profit Counter
# later add button for profit breakdown by time and source

# No need for start/stop buttons 
# bc as soon as account logged in it will start working

# INIT
# No Sportsbook Accounts Yet

# Add As Many Sportsbook Accounts As Possible to get the best prices
# Add Sportsbook Account Button
# -add account will open browser window to login page
# -instruct to save info in cache

# list of accounts logged in


# Progress Output Screen
# terminal output



