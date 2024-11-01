#writer.py
# display data

# === Standard External Libraries ===
import csv # save player and game espn ID's so we do not have to request each run

import json # for team players

import pandas as pd # write spreadsheets from lists to dataframes

from datetime import datetime # add date to filename

import numpy as np # mean, median to display over time
import os
import re # see if string contains stat and player of interest to display

#import string # to format workbook column wrap

from tabulate import tabulate # display output, eg consistent stat vals


import determiner # determine source limit to place bet
#import sorter # sort players outcomes so we see conditions grouped by type and other useful visuals

import converter, reader # convert dicts to lists AND number formats
# import remover

import time

from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC


def display_dict_items(dict):
    print('\nDict Items:')

    for key, val in dict.items():
        print(key + ': ' + val)

    print('\n==========\n')

def display_bet_details(bet_dict):
    print('\nBet Details:')

    for key, val in bet_dict.items():
        print(key + ': ' + str(val))

# also idle popup
def close_logged_out_popup(driver):
    print('\n===Close Logged Out Popup===\n')

    closed_popup = False

    # class modal-window
    # data-modal-name="POST_LOGOUT_POPUP_CLIENT_TIMEOUT"
    # class btn-modal-close
    if reader.check_logged_out_popup(driver):
        try:
            close_popup_btn = driver.find_element('class name', 'close-modal-button') #driver.find_element('class name', 'modal-window').find_element('class name', 'btn-modal-close')
            print('Found Close Popup Btn')
            close_popup_btn.click()
            time.sleep(0.5)
            print('Closed Logged Out Popup')
            closed_popup = True
        except Exception as e:
            print('Error Closing Logged Out Popup')

    # else:

    #     # try refreshing page
    #       need to refresh outcome btn too
    #       so place in click outcome btn fcn
    #     driver.refresh()
    #     time.sleep(1)

    return closed_popup


# input EV or Arb with side num
# if window idx None then we cannot find the outcome anymore
# which means the odds changed so move on
# we detect window if we can find same source and outcome button
# if window not detected then close windows and move on
# if window not detected, then how do we know which windows to close?
# if manual enabled, wait for input to continue and then close all extra windows
def switch_to_bet_window(bet_dict, driver, test, side_num=1):
    print('\n===Switch to Bet Window===\n')
    print('side_num: ' + str(side_num))
    print('bet_dict: ' + str(bet_dict) + '\n')

    window_idx = None

    # Default window idx unless extra windows open
    num_monitor_windows = 2
    if test:
        num_monitor_windows = 1
    window_idx = num_monitor_windows # 1 or 2 currently based on desired manual testing setup we add 1 window on top of main monitor window
    if side_num == 2 and bet_dict['actual odds1'] != '':
        window_idx = num_monitor_windows + 1

    window_key = 'window' + str(side_num)
    window_handle = bet_dict[window_key]

    print('\nSwitch to Window Idx: ' + str(window_idx) + '\n')
    driver.switch_to.window(window_handle)

    # we have what window idx is supposed to be
    # if no other windows open,
    # so if error getting final outcome 
    # could be wrong window or stale element
    # problem is if we have a window open manually 
    # then we do not want to risk opening multiple windows of same source 
    # to avoid bot detection
    # so if extra windows open, wait for manual command input to continue
    # default_window_idx = window_idx

    # source = bet_dict['source1']
    # if side_num == 2:
    #     source = bet_dict['source2']

    # init_num_windows = len(driver.window_handles)

    # found_window = False
    # while not found_window:

    #     if window_idx == init_num_windows:
    #         window_idx = default_window_idx
    #         print('Failed to Find Window. Use Default Window Idx: ' + str(window_idx))
    #         break

    #     print('Switch to Window Idx: ' + str(window_idx))
    #     driver.switch_to.window(driver.window_handles[window_idx])
        
    #     # see if window has correct outcome element
    #     # check outcome element saved in bet dict
    #     outcome_key = 'outcome' + str(side_num)
    #     outcome_element = bet_dict[outcome_key]
    #     try:
    #         outcome_element_html = outcome_element.get_attribute('innerHTML')
    #         print('outcome_element_html: ' + outcome_element_html)
    #         print('Found Outcome Element so Found Window')
    #         found_window = True
    #     except:
    #         print('Failed to find outcome element')
    #         # if page has different source than bet we know wrong page
    #         # so try next window idx

    #         try:

    #             found_source_window = False
    #             if source == 'betmgm':
    #                 driver.find_element('tag name', 'vn-app')
    #             elif source == 'betrivers':
    #                 driver.find_element('id', 'rsi-top-navigation')
                    
    #             else:
    #                 print('Unkown Source. Need to add source: ' + source)
    #                 window_idx = default_window_idx
    #                 print('Failed to Find Window. Use Default Window Idx: ' + str(window_idx))
    #                 break

    #             # if source window but no outcome element
    #             # check for other open windows with same source which might have outcome element
    #             # simpler to close all extra windows before opening bet windows
    #             # so we know always 2 bet windows and which idx they are
    #             print('Found Source Window but no Outcome Element')

    #         except:
    #             print('Not ' + source.title() + ' Window ' + str(window_idx))
    #             window_idx += 1
    #             print('Change to Window ' + str(window_idx))


        # try:

        #     found_source_window = True
        #     if source == 'betmgm':
        #         driver.find_element('tag name', 'vn-app')

        #     elif source == 'betrivers':
        #         driver.find_element('id', 'rsi-top-navigation')

        #     else:
        #         print('Unkown Source. Need to add source: ' + source)
        #         found_source_window = False
                
        #     if found_source_window:
        #         print('Found ' + source.title() + ' Window')
        #         print('Check for Outcome Element')

        #         # check outcome element saved in bet dict
        #         outcome_key = 'outcome' + str(side_num)
        #         outcome_element = bet_dict[outcome_key]
        #         try:
        #             outcome_element_html = outcome_element.get_attribute('innerHTML')
        #             print('outcome_element_html: ' + outcome_element_html)
        #             print('Found Outcome Element so Found Window')
        #             found_window = True
        #         except:
        #             print('Failed to find outcome element')
        #             # if na then refind outcome element from scratch
                    
        #             # if source == 'betmgm':
        #             # elif source == 'betrivers':
        #             #     driver.find_element('id', 'rsi-top-navigation')

                
                
        # except:
        #     print('Not ' + source.title() + ' Window ' + str(window_idx))
        #     window_idx += 1
        #     print('Change to Window ' + str(window_idx))

        

    print('\nSwitched to Window Idx ' + str(window_idx) + '\n')
    return window_idx

def remove_old_bets(driver, website_name):
    print('\n===Remove Old Bets===\n')
    print('website_name: ' + website_name + '\n')

    if website_name == 'betrivers':
        remove_bet_btns = driver.find_elements('class name', 'mod-KambiBC-betslip-outcome__close-btn')
    elif website_name == 'betmgm':
        remove_bet_btns = driver.find_elements('tag name', 'bs-digital-pick-remove-button')
    else:
        print('\nWebsite NA: ' + website_name + '\n')
        return
    
    if len(remove_bet_btns) > 1:
        # remove old bets
        num_old_bets = len(remove_bet_btns) - 1
        #print('\nnum_old_bets: ' + str(num_old_bets) + '\n')
        remove_bets = remove_bet_btns[:-1]
        #print('remove_bets: ' + str(remove_bets))
        print('\nRemove Old Bets: ' + str(len(remove_bets)) + '\n')
        for btn in remove_bets:
            btn.click()
            time.sleep(1)
            #print('Removed Bet')
    else:
        print('\nNo Old Bets\n')

# def remove_old_picks(driver, website_name):
#     print('\n===Remove Old Picks===\n')

#     if website_name == 'betrivers':
#         # remove all but bottom last pick bc most recent new pick
#         try:
#             remove_pick_btns = driver.find_elements('class name', 'mod-KambiBC-betslip-outcome__close-btn')
        
#             if len(remove_pick_btns) > 1:
#                 for remove_pick_btn in remove_pick_btns[:-2]:
#                     remove_pick_btn.click()
#                     print('Removed Pick')
#             else:
#                 print('Only 1 Pick in Betslip')
#         except:
#             print('Betslip Empty')

# if ev, just close 1 window
# if arb side 1, just close 1 window
# if arb side 2, close both windows
# then relinquish control back to main monitor window
# test has only 1 monitor window
# COPY TO CLIENT
def close_bet_windows(driver, side_num=1, test=False, bet_dict={}):
    print('\n===Close Bet Windows===\n')
    print('side_num: ' + str(side_num) + '\n')
    #print('bet_dict: ' + str(bet_dict))

    # get total num windows before closing first window
    # need to know how many monitor windows to know how many arb windows
    # so assume 2 monitor windows: 1 auto, 1 manual
    windows = driver.window_handles
    init_num_windows = len(windows)
    #print('init num_windows: ' + str(init_num_windows))

    num_monitor_windows = 2
    if test:
        num_monitor_windows = 1

    if init_num_windows == num_monitor_windows:
        print('No Bet Windows Open')
        return
    
    # if not always open window, like betrivers
    # close window 1 or 2
    source_key  = 'source'
    if 'source1' in bet_dict.keys(): # side 1 arb
        source_key += str(side_num)

    source = ''
    if source_key in bet_dict.keys():
        source = bet_dict[source_key]
        
    if source != 'betrivers':
    #if driver.current_window_handle != betrivers_window_handle:
        try:
            driver.close()
        except Exception as e:
            print('\nWindow Already Closed\n', e)

    #print('Closed Last Bet Window')
    updated_windows = driver.window_handles
    #print('updated num_windows: ' + str(len(updated_windows)))

   
    num_full_auto_windows = num_monitor_windows + 2
    #print('num_full_auto_windows: ' + str(num_full_auto_windows))
    #print('init num_windows: ' + str(init_num_windows))

    # if side 2, both windows open
    # so also close side 1 window
    # check if both window idxs given in arb dict
    if 'window1' in bet_dict.keys() and 'window2' in bet_dict.keys():
        if side_num == 2:
            source_key  = 'source1'
            source = bet_dict[source_key]
            print('Close Side 1 Window')
            if source != 'betrivers':
                try:
                    driver.switch_to.window(bet_dict['window1']) # idx 2 usually but depends on other windows
                    driver.close()
                    print('Closed Side 1 Window')
                except Exception as e:
                    print('Window 1 Already Closed', e)
            
        
        # if side 1 dictates invalid arb
        # we closed side 1 already
        # so also close side 2
        else: # side 1 first, so side 2 second
            source_key  = 'source2'
            source = bet_dict[source_key]
            print('Close Side 2 Window')
            if source != 'betrivers':
                try:
                    driver.switch_to.window(bet_dict['window2']) # idx 2 usually but depends on other windows
                    driver.close()
                    print('Closed Side 2 Window')
                except Exception as e:
                    print('Window 2 Already Closed', e)
            

    
    # send back to main window
    driver.switch_to.window(driver.window_handles[0])

    #print('\n===Closed Bet Windows===\n')


# ALTER FOR CLIENT
# Assume already on webpage
def login_website(website_name, driver, cookies_file='', saved_cookies=[], url=''):
    print('\n===Login Website===\n')
    print('Input: website_name: ' + website_name)
    #print('\nOutput: Logged In\n')

    email = os.environ['EMAIL']
    token = ''
    if website_name.upper() in os.environ.keys():
        token = os.environ[website_name.upper()]

    
    logged_in = False

    if website_name == 'slack':

        try:
            driver.find_element('class name', 'p-account_switcher')
            print('\nAlready Logged In Slack\n')
            return
        except:
            print('\nLogin Slack\n')

        # starts on login page
        # wait for tester to submit email
        submitted = False
        while not submitted: 
            
            # check not submitted if email field
            try:
                driver.find_element('id','signup_email')
            except:
                print('Submitted Email')
                submitted = True

        #time.sleep(1000)

        # if still loading, not logged in
        logged_in = opened_slack = False
        while not logged_in:

            # 1. Account Btn
            try:
                # logged in if account bbtn or messages?
                driver.find_element('class name', 'p-account_switcher')
                logged_in = True
                print('\nLogin Success\n')
            except:
                print('Loading Login...')
                
                # either slack link OR account btn
                # 2. Slack Link
                # may encounter open slack link
                if not opened_slack:
                    try:
                        open_slack_link = driver.find_element('xpath', '//a[@data-qa="ssb_redirect_open_in_browser"]')
                        print('Click Open Slack Link')
                        open_slack_link.click()
                        print('Clicked Open Slack Link')
                        opened_slack = True
                    except:
                        print('Loading Open Slack Link...')



    elif website_name == 'betrivers':

        login_retries = 0
        max_retries = 3
        while login_retries < max_retries:
            # look for my account menu btn
            # betrivers always requires login new window so may not need this for betrivers
            # unless leave open window for certain predefined time period
            # such as 5 min bc if haven't seen prop in 5min then probably not for a while???
            # not necessarily so maybe dont keep open at all unless already have more props in queue
            try:
                driver.find_element('xpath', '//div[@data-target="menu-user-account"]')
                print('\nAlready Logged In Betrivers\n')
                return
            except:
                print('\nLogin Betrivers\n')
                # login_betrivers()

            # keep looking for login page
            # OR just click login btn once???
            # problem is if not loaded yet then will move on before login
            login_page = False
            login_page_retries = 0
            while not login_page and login_page_retries < max_retries:
                # class = sc-gHLcSH cnmSeS
                # id=rsi-top-navigation
                # div
                # second div
                # button
                # goes to login page
                try:
                    login_btn = driver.find_element('id', 'rsi-top-navigation').find_element('tag name', 'div').find_element('xpath', 'div[2]').find_element('tag name', 'button')   # .find_element('class name', 'sc-gHLcSH')
                    print('login_btn: ' + login_btn.get_attribute('innerHTML'))
                    login_btn.click()
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    print('Exit')
                    exit()
                except Exception as e:
                    print('No Login Button\n', e)

                    try:
                        driver.find_element('xpath', '//div[@data-target="menu-user-account"]')
                        print('\nAlready Logged In Betrivers\n')
                        return
                    except:
                        print('\nLogin Betrivers\n')

                        # try close popups
                        close_popups(driver, website_name)

                try:
                    usr_field_input = driver.find_element('id', 'login-form-modal-email')
                    usr_field_html = usr_field_input.get_attribute('outerHTML')
                    print('usr_field_html: ' + usr_field_html)

                    login_page = True
                except KeyboardInterrupt:
                    print('Exit')
                    exit()
                except:
                    print('Not Login Page')
                    login_page_retries += 1

                    if login_page_retries == max_retries:
                        print('\nFailed to Login Automatially\n')
                        return 'fail'


            # it adds class validation-ok if valid email entered
            if not re.search('valid', usr_field_html):
                usr_field_input.send_keys(email)

            # login-form-modal-password
            pwd_field_input = driver.find_element('id', 'login-form-modal-password')
            pwd_field_html = pwd_field_input.get_attribute('outerHTML')
            print('pwd_field_html: ' + pwd_field_html)
            if not re.search('valid', pwd_field_html):
                pwd_field_input.send_keys(token)

            # id = login-form-modal-submit
            submit_btn = driver.find_element('id', 'login-form-modal-submit') #('xpath', '//button[@class="login w-100 btn btn-primary"]')
            print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
            submit_btn.click()
            time.sleep(1)

            popups = main_popup = boost_popup = loc_popup = True
            while popups:
                try:
                    # class = close-modal-button-container
                    close_popup_btn = driver.find_element('xpath', '//div[@class="close-modal-button"]')
                    print('close_popup_btn: ' + close_popup_btn.get_attribute('innerHTML'))
                    close_popup_btn.click()
                    time.sleep(0.5)

                    print('\nClosed Main Popup\n')
                    main_popup = False

                # First time login each day shows profit boost popup instead
                except:
                    print('No Main Popup Yet')

                print('\nCheck If Profit Boost Popup\n')
                # 'data-translate="BTN_CLOSE_TITLE"'
                try:
                    close_boost_btn = driver.find_element('xpath', '//a[@data-translate="BTN_CLOSE_TITLE"]')
                    close_boost_btn.click()
                    print('\nClosed Profit Boost\n')
                    boost_popup = False
                except:
                    print('No Profit Boost')

                    if main_popup == False:
                        boost_popup = False

                print('\nCheck If Location Popup\n')
                try:
                    # close location popup
                    # 'data-testid="alert"'
                    # > tag button or aria-label="Close"
                    close_loc_btn = driver.find_element('xpath', '//div[@data-testid="alert"]').find_element('tag name', 'button')
                    print('close_loc_btn: ' + close_loc_btn.get_attribute('outerHTML'))
                    close_loc_btn.click()
                    print('\nClosed Location Popup\n')
                    loc_popup = False
                except:
                    print('No Location Popup')

                    if main_popup == False:
                        loc_popup = False


                # check login fail
                # data-modal-name="LOGIN_FAILED"
                # close btn: class="btn btn-primary btn-modal-close w-120", data-translate="BTN_CLOSE_OK"
                # if no main popup, then closed so login success
                # so no need to check login fail
                if main_popup: # main popup default true means not logged in
                    print('\nCheck If Login Fail Popup\n')
                    try:
                        close_fail_btn = driver.find_element('class name', 'btn-modal-close')
                        close_fail_btn.click()
                        print('\nClosed Fail Popup. Refresh and Try Again.\n')
                        # try login again
                        driver.refresh()
                        time.sleep(1)
                        login_retries += 1
                        if login_retries == max_retries:
                            print('\nFailed to Login Automatially\n')
                            return 'fail'
                        break
                    except:
                        print('No Fail Popup')

                
                if not main_popup and not boost_popup and not loc_popup:
                    popups = False

            logged_in = True

    elif website_name == 'betmgm':
        # check if logged in by top right corner menu
        # if it says login then not logged in
        # if it says account name then logged in
        # if not logged in, then go direct to login url
        # no need to click btn unless easier
        # example: driver.find_element_by_xpath('//input[@node-type="searchInput"]')
        # login_btn = driver.find_element('xpath', '//vn-menu-item-text-content[@data-testid="signin"]')
        # print('login_btn: ' + login_btn.get_attribute('innerHTML'))
        # login_btn.click()
        # time.sleep(1)

        # url: 
        # https://www.ny.betmgm.com/en/labelhost/login
        # session expired url: 
        # ny url seems to work but sports.ny fails 
        # now both urls fail!!! after a day of working ok
        # login_url = 'https://www.ny.betmgm.com/en/labelhost/login'#'https://sports.ny.betmgm.com/en/labelhost/login' #?rurl=https:%2F%2Fsports.ny.betmgm.com%2Fen%2Fsports%2Fevents%2Farizona-diamondbacks-at-san-francisco-giants-16215229%3Fmarket%3DPlayers:Batting
        # login_url2 = 'https://sports.ny.betmgm.com/en/labelhost/login'
        # Check if already logged in
        # Check if need to login

        
        need_login = True
        # check session expired by login duration Nan
        try:
            login_duration = driver.find_element('class name', 'login-duration-time').get_attribute('innerHTML')
            print('login_duration: ' + login_duration)
            if login_duration != 'NaN:NaN:NaN':
                print('Found Valid Login duration: ' + login_duration)
                need_login = False
        except:
            print('No login duration, so log in.')


        if need_login:
            try:
                print('Go to Login Page')
                # OPTION 1
                # driver.get(login_url) 
                
                # OPTION 2
                login_btn = driver.find_element('xpath', '//vn-menu-item-text-content[@data-testid="signin"]')
                print('login_btn: ' + login_btn.get_attribute('innerHTML'))
                login_btn.click()

                #time.sleep(3)  
            except:
                print('\nAlready Logged In BetMGM\n')
                return
        else:
            print('\nAlready Logged In BetMGM\n')
            return
        
        # try to simply login with dialog
        # even tho expected error
        # sometimes works
        login_page = False
        while not login_page:
            try:
                # .find_element('class name', 'login')#
                submit_btn = driver.find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
                print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
                login_page = True
            except KeyboardInterrupt:
                print('\nKeyboardInterrupt in Login')
                print('Exit')
                exit()
            except:
                print('Loading Login Page...')
                time.sleep(1)
        
        submitted_login = False
        try:
            submit_btn.click()
            time.sleep(1) 
            submitted_login = True
        except:
            print('Error: Failed to click submit btn!')

        if submitted_login:

            # if error, try backup login method
            pwd_msg = ''
            loading = True
            while loading and not logged_in:
                try:
                    pwd_msg = driver.find_element('class name', 'm2-validation-message').get_attribute('innerHTML').lower()
                    print('pwd_msg: ' + pwd_msg)
                    loading = False
                    print('Done Loading')
                except KeyboardInterrupt:
                    print('\nKeyboardInterrupt in Login')
                    print('Exit')
                    exit()
                except:
                    print('Loading...')

                    try:
                        pwd_field = driver.find_element('name', 'password')
                    except:
                        logged_in = True
                        print('\nLogin Success\n')


            # glitch error
            if pwd_msg != '':
            
                # Need to click register>login to avoid tech glitch
                login_page = False
                while not login_page:
                    try:
                        reg_link = driver.find_element('class name', 'registration-link')
                        login_page = True
                    except:
                        print('Loading Login Page...')
                        time.sleep(1)
                    
                reg_link.click() # goes to signup page
                time.sleep(1)

                # error not found sometimes???
                # loop until found, but timeout after 60 seconds
                loading = True
                while loading:
                    try:
                        login_link = driver.find_element('class name', 'conversation-textalign').find_element('tag name', 'a')
                        print('Done loading signup page')
                        loading = False
                        login_link.click() # goes to login page
                        time.sleep(1) 
                    except KeyboardInterrupt:
                        #loading = False
                        print('Exit')
                        exit()
                    except:
                        print('Loading signup page...')
                        time.sleep(1)

                # path_to_btn = [('class','conversation-textalign'), ('tag','a')]
                # click_after_load(driver, path_to_btn)

                loading = True
                while loading:
                    try:
                        submit_btn = driver.find_element('xpath', '//button[@class="login w-100 btn btn-primary"]') 
                        print('Done loading login page')
                        loading = False
                        time.sleep(1) 
                    except KeyboardInterrupt:
                        #loading = False
                        print('Exit')
                        exit()
                    except:
                        print('Loading login page...')
                        time.sleep(1)


                try:

                    usr_field_html = driver.find_element('id', 'username').get_attribute('innerHTML')
                    if re.search('ng-untouched', usr_field_html):
                        print('Enter Username')
                        usr_field = driver.find_element('id', 'userId')
                        usr_field.send_keys(email)
                        time.sleep(1)

                    # pwd input element
                    pwd_field = driver.find_element('name', 'password')
                    pwd_field_html = pwd_field.get_attribute('outerHTML')
                    print('pwd_field_html: ' + pwd_field_html)
                    if re.search('ng-untouched', pwd_field_html):
                        print('Enter Password')
                        #pwd_field = driver.find_element('name', 'password')
                        pwd_field.clear()
                        time.sleep(1)
                        pwd_field.send_keys(token)
                        time.sleep(3)

                    #.find_element('class name', 'login')#find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
                    # error with just using login class, other btn would receive click
                    submit_btn = driver.find_element('xpath', '//button[@class="login w-100 btn btn-primary"]') 
                    print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
                    submit_btn.click()
                    time.sleep(3) 


                    # If Error, click sign up > log in again
                    pwd_msg = ''
                    try:
                        pwd_msg = driver.find_element('class name', 'm2-validation-message').get_attribute('innerHTML').lower()
                        print('pwd_msg: ' + pwd_msg)
                    except:
                        print('Loading...')

                    # glitch error
                    if pwd_msg != '':
                        signup_btn = driver.find_element('xpath', '//vn-menu-item-text-content[@data-testid="registerbutton"]')
                        signup_btn.click()
                        time.sleep(3)

                        login_link = driver.find_element('class name', 'conversation-textalign').find_element('tag name', 'a')
                        login_link.click()
                        time.sleep(3) 

                        submit_btn = driver.find_element('class name', 'login')#find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
                        print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
                        submit_btn.click()
                        time.sleep(3) 

                except:
                    print('\nFailed to Login Automatially\n')
                    return 'fail'




        # if still loading, not logged in
        while not logged_in:
            try:
                pwd_field = driver.find_element('name', 'password')
            except KeyboardInterrupt:
                print('\nKeyboardInterrupt in Login')
                print('Exit')
                exit()
            except:
                logged_in = True
                print('\nLogin Success\n')


    elif website_name == 'draftkings':
        print('Login DK')

        login_btn = None
        need_login = True
        # check logged in by account dropdown
        # data-test-id="account-dropdown"
        # OR check not logged in by login btn
        try:
            # id="cta-wrapper"
            # a data-test-id="Log In-cta-link"
            # cta wrapper could also be shown if logged in
            # so either use exact id
            # or use cta wrapper and check btn says login
            login_btn = driver.find_element('xpath', '//a[@data-test-id="Log In-cta-link"]') #('id', 'cta-wrapper').find_element('tag name', 'a')
            print('login_btn: ' + login_btn.get_attribute('innerHTML'))
            #need_login = True

            try:
                print('Go to Login Page')
                login_btn.click()
            except:
                print('\nFailed to Click Login button. Already Logged In DK\n')
                need_login = False
                #return

        except:
            print('No login btn. Already Logged In DK.')
            need_login = False
            #return

        
        
        # if do not need login
        # check if need recheck location
        if not need_login:
            recheck_location(driver)

        else: # Login

            submit_btn = None
            login_page = False
            while not login_page:
                try:
                    # id login-submit
                    submit_btn = driver.find_element('id', 'login-submit')
                    print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
                    login_page = True
                except:
                    print('Loading Login Page...')
                    time.sleep(1)

            # assuming info already entered
            submit_btn.click()

            # if still loading, not logged in
            logged_in = False
            while not logged_in:
                try:
                    # logged in if betslip
                    driver.find_element('id', 'dom_betslip')
                    logged_in = True
                    print('\nLogin Success\n')
                except:
                    print('Loading Login...')
                    time.sleep(1)
                



    # Do Something
    #time.sleep(1)

    if logged_in:
        print('Logged In, Do We Need to Save Cookies???')
        #reader.save_cookies(driver, website_name, cookies_file, saved_cookies)


    #return driver not needed bc already in parent fcn
    #gets updated



        

def clear_betslip(driver, website_name='betrivers'):
    print('\n===Clear Betslip===\n')
    # Require that betslip is empty
    # So look for betslip html to see if open
    # if open, click clear all

    if website_name == 'betrivers':
        try:
            clear_btn = driver.find_element('class name', 'mod-KambiBC-betslip__clear-btn')
            clear_btn.click()
            print('Cleared Betslip')
        except:
            try:
                remove_pick_btns = driver.find_elements('class name', 'mod-KambiBC-betslip-outcome__close-btn')
                for remove_pick_btn in remove_pick_btns:
                    remove_pick_btn.click()
                    print('Removed Pick')
            except:
                print('Betslip Empty')


def wager_remaining_funds(driver, website_name):
    print('\n===Wager Remaining Funds===\n')

    # enter max amount in field
    funds = reader.read_remaining_funds(driver, website_name)
    wager_field = None
    if website_name == 'betrivers':
        wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
    elif website_name == 'betmgm':
        wager_field = driver.find_element('class name', 'stake-input-value')
    # print('wager_field: ' + wager_field.get_attribute('outerHTML'))
    wager_field.clear()
    time.sleep(0.1)
    wager_field.send_keys(funds)
    time.sleep(0.5)
    print('Wrote In Funds')

    return funds


def close_popups(driver, website_name):
    print('\n===Close Popups===\n')

    if website_name == 'betrivers':

        # usually require main popup
        # but if no main popup after 3 tries asssume already clicked glitch

        popups = main_popup = boost_popup = loc_popup = True
        while popups:
            try:
                # class = close-modal-button-container
                close_popup_btn = driver.find_element('xpath', '//div[@class="close-modal-button"]')
                print('close_popup_btn: ' + close_popup_btn.get_attribute('innerHTML'))
                close_popup_btn.click()
                time.sleep(1)

                print('\nClosed Main Popup\n')
                main_popup = False

            # First time login each day shows profit boost popup instead
            except:
                
                # already clicked other popups so should see main popup by now
                # maybe clicked already before fcn called
                if boost_popup == False and loc_popup== False:
                    print('\nMain Popup Already Closed\n')
                    main_popup = False

                else:
                    print('No Main Popup Yet')


            print('\nCheck If Profit Boost Popup\n')
            # 'data-translate="BTN_CLOSE_TITLE"'
            try:
                close_boost_btn = driver.find_element('xpath', '//a[@data-translate="BTN_CLOSE_TITLE"]')
                close_boost_btn.click()
                print('\nClosed Profit Boost\n')
                boost_popup = False
            except:
                print('No Profit Boost')

                if main_popup == False:
                    boost_popup = False

            print('\nCheck If Location Popup\n')
            try:
                # close location popup
                # 'data-testid="alert"'
                # > tag button or aria-label="Close"
                close_loc_btn = driver.find_element('xpath', '//div[@data-testid="alert"]').find_element('tag name', 'button')
                print('close_loc_btn: ' + close_loc_btn.get_attribute('outerHTML'))
                close_loc_btn.click()
                print('\nClosed Location Popup\n')
                loc_popup = False
            except:
                print('No Location Popup')

                if main_popup == False:
                    loc_popup = False

            # either none or all means exit loop
            if not main_popup and not boost_popup and not loc_popup:
                popups = False

            elif main_popup and boost_popup and loc_popup:
                popups = False

def click_place_btn(place_bet_btn, driver, website_name):

    # needs fcn to account for glitches to ensure clean click
    # may fail with popup glitch 
    # which simply needs to be closed and retried
    try:
        place_bet_btn.click()
        time.sleep(1)
        print('Placed Bet to Find Limit')
        #time.sleep(3) 
    except:
        print('Error: Failed to Click Place Bet Button! Check popup confirm number popup.')

        #if logged_in:
        # check for confirm phone popup
        try:
            confirm_dialog = driver.find_element('tag name', 'ms-modal-dialog')#
            close_dialog_btn = confirm_dialog.find_element('class name', 'ds-button')
            print('close_dialog_btn: ' + close_dialog_btn.get_attribute('innerHTML'))
            close_dialog_btn.click()
            time.sleep(0.5)
            print('Closed Confirm Popup')

            # Now try clicking plce bet again
            try:
                place_bet_btn.click()
                time.sleep(0.5)
            except:
                print('Failed to Click Place Bet After Closed Confirm Popup')

        except:
            print('No Confirm Popup')

            print('Check Location Popup')
            try:
                # tag ms-geo-location-installer
                # class close
                loc_dialog = driver.find_element('tag name', 'ms-geo-location-installer')#
                close_dialog_btn = loc_dialog.find_element('class name', 'close')
                print('close_dialog_btn: ' + close_dialog_btn.get_attribute('innerHTML'))
                close_dialog_btn.click()
                time.sleep(0.5)
                print('Closed Location Popup')
            except:
                print('No Location Popup')



def place_bet(bet_dict, driver, final_outcome, cookies_file, saved_cookies, pick_type='ev', test=True, max_retries=3):
    print('\n===Place Bet===\n')
    #print('Input: bet_dict = ' + str(bet_dict) + '\n')
    
    place_bet = True

    website_name = bet_dict['source']
    print('website_name: ' + website_name)

    url = bet_dict['link']

    init_odds = bet_dict['odds']
    print('init_odds: ' + init_odds)

    # wait to load if not clearing betslip???

    # print('Has Page Shifted Inadvertently Yet??') No

    # click bet btn to add to betslip
    if final_outcome is not None:

        if website_name == 'betmgm':
            #time.sleep(1) # load should be after action not before

            # close survery btn pops up randomly
            # especially after sitting on page for a while
            # class surveyBtn_close

            logged_in = False
            login_result = login_website(website_name, driver, cookies_file, saved_cookies, url)
            if login_result == 'fail':
                close_bet_windows(driver, test=test, bet_dict=bet_dict)
                return

            bet_size = determiner.determine_limit(bet_dict, website_name, pick_type, test)

            wager_field = load_bet_page(driver, website_name, bet_dict, test)
        
            if wager_field is None:
                return

            # if error other than limit
            # then not considered attempted bet
            # so fix error and retry bet to find limit
            attempted_bet = False
            placed_bet = False
            while not attempted_bet and not placed_bet:
                # login takes time so check if odds changed
                try:
                    place_bet_btn = driver.find_element('class name', 'place-button')
                except Exception as e:
                    print('\nERROR: No Bet Button\n')
                    close_bet_windows(driver, test=test, bet_dict=bet_dict)
                    return
                
                # check if enough funds
                place_btn_text = place_bet_btn.find_element('class name', 'ds-btn-text').get_attribute('innerHTML').lower()
                print('place_btn_text: ' + str(place_btn_text))
                # if odds changed, if ev, stop and continue to monitor
                if re.search('accept', place_btn_text):
                    attempted_bet = True
                
                else: # Odds Valid
                
                    #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
                    # placeholder = wager_field.get_attribute('placeholder')
                    # #print('placeholder: ' + placeholder)
                    # # ensure wager field clear
                    # wager_field_val = wager_field.get_attribute('value')
                    # print('wager_field_val: ' + wager_field_val)
                    # error clearing field with placeholder condition after closing popup
                    # so clear every time to avoid error after closing popup
                    #if not placeholder == '' or wager_field_val != '':
                    wager_field.clear()
                    time.sleep(0.5)
                    wager_field.send_keys(bet_size)
                    time.sleep(0.5)
                    #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
                    # except:
                    #     print('Error: No Wager Field. Check Bet Locked???')
                    # test wait
                    #time.sleep(100)

                    # === MONEY ===
                    # Place Bet 1
                    # maybe success
                    # more likely above limit
                    # or rarely not enough funds
                    # place bet at known max limit to find bet limit
                    #try:
                    

                    if re.search('deposit', place_btn_text):
                        # bet all remaining funds
                        wager_remaining_funds(driver, website_name)

                    # ===Click Place Bet Btn BetMGM===
                    click_place_btn(place_bet_btn, driver, website_name)
                    

                    # wait to finish loading
                    # either close receipt btn or alert msg
                    loading = True
                    while loading:

                        # close receipt
                        # tag bs-digital-result-state
                        # tag bs-linear-result-summary
                        # class result-summary__actions
                        # _ngcontent-ng-c980967766
                        # button
                        try:
                            close_receipt_btn = driver.find_element('tag name', 'bs-digital-result-state').find_element('class name', 'result-summary__actions').find_element('tag name', 'button')
                            loading = False
                            print('Done Loading')
                            time.sleep(3)
                            close_receipt_btn.click()
                            time.sleep(1) 
                            print('Closed Receipt')
                            time.sleep(3)

                            # Go to my bets to confirm
                            my_bets_btn = driver.find_element('class name', 'myBetsTab')
                            my_bets_btn.click()
                            print('Clicked My Bets')
                            time.sleep(3) # TEMP wait to manually check bet placed before closing

                            try:
                                open_bets_btn = driver.find_element('class name', 'sliding-menu').find_element('xpath', 'div[2]')
                                open_bets_btn.click()
                                print('Clicked Open Bets')
                                time.sleep(3)
                            except:
                                print('Failed to Click Open Bets')

                            placed_bet = True
                            print('Placed Bet')

                        except:
                            print('No Receipt Yet. Loading placed bet to find limit...')

                            try:
                                #print('\nBet Error\n')
                                #place_bet = False

                                # if test:
                                #     # test wait
                                #     time.sleep(100)

                                # if wager too high, click back
                                # tag name: bs-alert
                                # >class="alert-content__message"
                                # limit
                                alert_msg = driver.find_element('class name', 'alert-content__message').get_attribute('innerHTML').lower() # Wager too high
                                print('alert_msg: ' + alert_msg)

                                loading = False
                                print('Done Loading')

                                if re.search('limit', alert_msg):
                                    attempted_bet = True
                                    print('Attempted Bet')
                                elif re.search('parlay', alert_msg):
                                    print('Failed to Remove Old Pick so Try Again')
                                    remove_old_bets
                                else:
                                    # if not limit problem, then odds changed so close and continue
                                    place_bet = False
                                    # if not limit problem, check if locked or odds changed
                                    # if locked, remove bet from slip and close window
                                    #try:
                                    # class name: place-button-message
                                    try:
                                        btn_msg = driver.find_element('class name', 'place-button-message').get_attribute('innerHTML').lower() # Wager too high
                                        print('\nUNKNOWN ERROR: btn_msg: ' + btn_msg + '\n')
                                    except:
                                        print('No Button Message')

                                        # check for error alert dialog popup
                                        # class geo-comply-error-validation-container
                                        # class ds-button
                                        try:
                                            error_dialog = driver.find_element('class name', 'geo-comply-error-validation-container').get_attribute('innerHTML')
                                            print('error_dialog: ' + error_dialog)
                                            close_dialog_btn = driver.find_element('class name', 'ds-button')
                                            loading = False
                                            print('Done Loading')
                                            close_dialog_btn.click()
                                            time.sleep(1)
                                            print('Closed Error Dialog')
                                            # replace bet to find limit
                                            # loops back around bc attempted bet still false
                                        except:
                                            print('No Error Yet. Loading placed bet to find limit...')
                                
                            except KeyboardInterrupt:
                                loading = False
                            except:
                                print('No Alert Yet. Loading placed bet to find limit...')

                                
                        
            # intended bet size may be below limit
            # so returned placed bet without finding limit
            # bet_limit = find_bet_limit()  
            # if bet_limit is None:
            #     placed_bet = True     

            if not placed_bet:

                # For EV, place at limit
                if not test and place_bet:
                    # Double Check odds before placing final bet
                    new_odds = reader.read_betslip_odds(driver, website_name)
                    # if new odds changed
                    # for ev, close
                    # for arb, check still valid
                    
                    if new_odds != init_odds:
                        print('init_odds: ' + init_odds)
                        print('Odds Changed')
                        close_bet_windows(driver, test=test, bet_dict=bet_dict)
                        return

                    place_bet_btn = driver.find_element('class name', 'place-button')
                    print('place_bet_btn: ' + place_bet_btn.get_attribute('innerHTML'))
                    place_bet_btn.click()
                    time.sleep(3)
                    print('Placed Bet')

                    # NEED to Handle Odds Change on subsequent attempts
                    # loop while odds in range and not yet placed
                    # but for EV if odds change then skip
                    loading = True
                    while loading:
                        # if done loading, will find either receipt or alert
                        try:
                            close_receipt_btn = driver.find_element('tag name', 'bs-digital-result-state').find_element('class name', 'result-summary__actions').find_element('tag name', 'button')
                            loading = False
                            print('Done Loading')
                            close_receipt_btn.click()
                            # DEMO:
                            time.sleep(1)
                            #time.sleep(1) # Wait for bet to fully load and submit before moving on
                            print('Closed Receipt')

                            my_bets_btn = driver.find_element('class name', 'myBetsTab')
                            my_bets_btn.click()
                            print('Clicked My Bets')
                            time.sleep(3) # TEMP wait to manually check bet placed before closing

                            open_bets_btn = driver.find_element('class name', 'sliding-menu').find_element('xpath', 'div[2]')
                            open_bets_btn.click()
                            print('Clicked Open Bets')
                            time.sleep(3)

                        except:
                            print('Loading final placed bet...')
                            # print('\nBet Failed\n')
                            # print('Odds Change or Other Error???')

                            # # handle session timeout
                            # # read bottom msg below button or wager field???
                            # print('\nHandle Session Timeout\n')
                            # time.sleep(100)

                            # if no receipt yet, check if alert msg
                            try:
                                alert_msg = driver.find_element('class name', 'alert-content__message').get_attribute('innerHTML').lower() # Wager too high
                                print('alert_msg: ' + alert_msg)
                                loading = False
                                print('Done Loading')

                                print('\nBet Failed\n')
                                print('Odds Change or Other Error???')

                                # handle session timeout
                                # read bottom msg below button or wager field???
                                print('\nHandle Session Timeout\n')
                                time.sleep(100)
                            except:
                                print('Loading final placed bet...')


                    
                


                

                # if test:
                #     # test wait
                #     time.sleep(100)
                #     # test close
                #     driver.close()

        elif website_name == 'betrivers':
            #clear_betslip(driver)
            
            add_bet_to_betslip(final_outcome, driver, website_name)
            #click_outcome_btn(final_outcome, driver, website_name)
            
            # Need to double check no old bets in slip 
            # bc glitch may hide old betslip until new bet clicked
            # for now simplest way is to keep only last bet in slip bc adds to bottom
            # later parlays will need to keep multiple so cannot assume only 1
            
            # remove old bets here does nothing bc not logged in yet glitch
            #remove_old_bets(driver, website_name)

            #listed_bets = []
            # for listed_bet in listed_bets:
            #     # if not current bet, remove
            #     print('listed_bet: ' + str(listed_bet))

            #     if found_market and determiner.determine_matching_outcome(listed_line, bet_line):
            #         print('Found Bet Listed')
            #     else:
            #         # remove old bet
            #         print('Remove Old Pick from Slip')
            #         remove_btn = listed_bet.find_element('tag name', 'bs-digital-pick-remove-button')
            #         remove_btn.click()
            #         time.sleep(1)

            # print('Has Page Shifted Inadvertently Yet??') No
            # time.sleep(100)

            # Login after adding to betslip bc then keeps in betslip
            # login first detects if already logged in
            #if not test:
            login_result = login_website(website_name, driver, cookies_file, saved_cookies, url)
            if login_result == 'fail':
                close_bet_windows(driver, test=test, bet_dict=bet_dict)
                return
            
            # For Arbs, find limit by placing large bet we know above limit
            # find_bet_limit(website_name, driver)

            # For EVs, place bet at given size, rounded to nearest whole number
            # Then if after place bet, returns msg over limit, place bet at limit

            # === Find Limit === 
            # If EV, start with given wager size
            # If Arb, find limits on both sides
            
            # Determine Pick Type Limit
            bet_size = determiner.determine_limit(bet_dict, website_name, pick_type, test)

            #submit_wager(bet_size, website_name)
            # the field uses a changing id so get container 
            # and then know 1st field is wager field
            #input_container = driver.find_element('class name', 'mod-KambiBC-to-win-input__container')
            #print('input_container: ' + input_container.get_attribute('innerHTML'))
            # loading = True
            # while loading:

            # remove bets before sending keys bc might erase
            remove_old_bets(driver, website_name)
            # need to get wager field after removing bets bc new wager field
            try:   
                wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
                loading = False
            except:
                final_outcome.click()
                time.sleep(1)
                # remove bets before sending keys bc might erase
                remove_old_bets(driver, website_name)

                wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')

            #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
            wager_field.send_keys(bet_size)

            # click Place Bet
            # mod-KambiBC-betslip__place-bet-btn KambiBC-disabled
            place_bet_btn = driver.find_element('class name', 'mod-KambiBC-betslip__place-bet-btn')
            #print('place_bet_btn: ' + place_bet_btn.get_attribute('innerHTML'))
                
            

            # === MONEY ===
            #try:
            #if not test:
            # Need to click twice or just wait longer???
            place_btn_clicked = False
            while not place_btn_clicked:
                # wait until place bet btn loaded becomes clickable
                # it is clicked after receipt or error
                
                # after 3 tries, close and reopen betslip
                # then if fails, close windows and move on
                # click_retries = 0
                # while click_retries < max_retries:
                # place_initial_bet(bet_size, place_bet_btn, driver, website_name)
                # click_place_bet_btn()
                try:
                    place_bet_btn.click()
                    time.sleep(0.5) # need wait for bet to fully load and submit before moving on
                    try:
                        place_bet_btn.click()
                        time.sleep(0.5)
                    except:
                        print('Failed to Click Place Bet second time so check if already placed?')
                    print('Placed Initial Bet: ' + str(bet_size))
                    place_btn_clicked = True
                except:
                    print('Failed to click Place Bet Button. Retry ' + str(click_retries) + '/' + str(max_retries) + '.')
                    time.sleep(1)
                        #click_retries += 1

                    close_popups(driver, website_name)

            # If no receipt
            # Wager too higher, OR
            # Odds Change
            try:
                close_receipt_btn = driver.find_element('class name', 'mod-KambiBC-betslip-receipt__close-button')
                time.sleep(2)
                close_receipt_btn.click()
                time.sleep(1) 
                print('Closed Receipt')

                # Go to my bets to confirm
                #aria-label="Navigate to My Bets"
                my_bets_btn = driver.find_element('xpath', '//button[@aria-label="Navigate to My Bets"]')
                my_bets_btn.click()
                print('Clicked My Bets')
                time.sleep(3) # TEMP wait to manually check bet placed before closing


            except:
                print('Bet Error')
                #place_bet = False

                # if wager too high, click back
                try:
                    error_title = driver.find_element('class name', 'mod-KambiBC-betslip-feedback__title').get_attribute('innerHTML').lower() # Wager too high
                    print('error_title: ' + error_title)

                    #place_bet = True
                    back_btn = driver.find_element('class name', 'mod-KambiBC-betslip-button')
                    print('back_btn: ' + back_btn.get_attribute('innerHTML'))
                    back_btn.click()
                    time.sleep(1)
                    print('Clicked Back Btn')
                    
                    # Still place bet if not allowed above limit?
                    #if error_title == 'wager too high':
                        # click back and then place bet with max amount already in field

                    if error_title == 'not enough money':
                        print('Not enough money')

                        # need to close betslip bc send keys not working
                        final_outcome.click()
                        time.sleep(1)

                        # enter max amount in field
                        # data-target="menu-quick-deposit"
                        funds_element = driver.find_element('xpath', '//div[@data-target="menu-quick-deposit"]')
                        # remove $
                        funds = float(funds_element.find_element('tag name', 'div').find_element('tag name', 'span').get_attribute('innerHTML')[1:])
                        print('funds: ' + str(funds))

                        # reopen
                        final_outcome.click()
                        time.sleep(1)

                        #input_container = driver.find_element('class name', 'mod-KambiBC-to-win-input__container')
                        #print('input_container: ' + input_container.get_attribute('innerHTML'))
                        wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
                        # print('wager_field: ' + wager_field.get_attribute('outerHTML'))
                        # wager_field.clear()
                        # time.sleep(3)
                        # wager_field.clear()
                        # print('Cleared Wager')
                        # wager_field.send_keys(Keys.DELETE)
                        # print('deleted')
                        # time.sleep(1)
                        wager_field.send_keys(funds)
                        # #driver.execute_script("arguments[0].setAttribute('value',arguments[1])",wager_field, funds)
                        # print('wager_field: ' + wager_field.get_attribute('outerHTML'))
                        #WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "mod-KambiBC-stake-input__container"))).send_keys(funds)
                        time.sleep(1)
                        print('Input Funds')
                            
                        # elif error_title == 'odds changed':
                        #     # if arb, check other side to see if still valid
                        #     'mod-KambiBC-betslip-button'

                    elif error_title == 'bet offer suspended':
                        close_bet_windows(driver, side_num=1, test=test, bet_dict=bet_dict)
                        return
                    
                except Exception as e:
                    print('\nUnknown Error while placing bet\n', e)

                    print('Re-Enter Wager in Field')
                    #wager_field.send_keys(bet_size)

                print('Done Loading Initial Bet')

                # if odds change, may still be ok for arb, depending on other side
                # approve odds btn: mod-KambiBC-betslip__place-bet-btn mod-KambiBC-betslip__approve-odds-btn
                # but for ev if odds change need to compare to fair odds before deciding if still proceed
                # For EV, remove pick bc invalidated
                # and do not add to saved list in case becomes valid again
                
                # For EV, place at limit
                if not test and place_bet:
                    # make sure place btn loads
                    # close and continue and if odds changed
                    place_bet_btn = driver.find_element('class name', 'mod-KambiBC-betslip__place-bet-btn')
                    place_bet_btn_text = place_bet_btn.get_attribute('innerHTML').lower()
                    print('place_bet_btn: ' + place_bet_btn_text)
                    
                    if place_bet_btn_text == 'approve odds change':
                        # close window and move on
                        print('Odds Changed')
                        close_bet_windows(driver, test=test, bet_dict=bet_dict)
                        return
                    
                    # wait for place bet btn to enable
                    place_btn_disabled = place_bet_btn.get_attribute('disabled')
                    #print('place_btn_disabled: ' + str(place_btn_disabled))
                    while place_btn_disabled == 'true':
                        try:
                            place_btn_disabled = place_bet_btn.get_attribute('disabled')
                            print('place_btn_disabled: ' + str(place_btn_disabled))
                            
                        except KeyboardInterrupt:
                            place_btn_disabled = 'true'
                            # print('Exit')
                            # exit()

                        except:
                            print('Place Button Enabled')

                        if place_btn_disabled == 'true':
                            bet_limit = ''
                            try:
                                bet_limit = wager_field.get_attribute('value')
                            except:
                                print('Unknown Bet Limit')

                            if bet_limit == '':
                                print('Reached Bet Limit')#: ' + str(bet_limit))
                                close_bet_windows(driver, test=test, bet_dict=bet_dict)#, side_num)
                                return

                    place_bet_btn.click()
                    # time.sleep(1) # need wait
                    # # may need to click twice
                    # try:
                    #     place_bet_btn.click()
                    # except:
                    #     print('No need to click place bet twice. Already placed bet.')
                    # DEMO:
                    time.sleep(1)
                    #time.sleep(1)
                    print('Placed Bet')

                    # NEED to Handle Odds Change on subsequent attempts
                    # loop while odds in range and not yet placed
                    # but for EV if odds change then skip
                    try:
                        close_receipt_btn = driver.find_element('class name', 'mod-KambiBC-betslip-receipt__close-button')
                        time.sleep(2)
                        close_receipt_btn.click()
                        # DEMO:
                        time.sleep(1)
                        #time.sleep(1) # Wait for bet to fully load and submit before moving on
                        print('Closed Receipt')
                    except:
                        print('Bet Failed')
                        print('Odds Change or Other Error???')

                        try:

                            error_title = driver.find_element('class name', 'mod-KambiBC-betslip-feedback__title').get_attribute('innerHTML').lower() # Wager too high
                            print('error_title: ' + error_title)

                            back_btn = driver.find_element('class name', 'mod-KambiBC-betslip-button')
                            print('back_btn: ' + back_btn.get_attribute('innerHTML'))
                            back_btn.click()
                            time.sleep(1)
                            print('Clicked Back Btn')

                            if error_title == 'wager too high':
                                # click back and then place bet with max amount already in field

                                place_bet_btn = driver.find_element('class name', 'mod-KambiBC-betslip__place-bet-btn')
                                place_bet_btn.click()
                                time.sleep(1)
                                print('Placed Bet')

                                close_receipt_btn = driver.find_element('class name', 'mod-KambiBC-betslip-receipt__close-button')
                                close_receipt_btn.click()
                                time.sleep(1)
                                print('Closed Receipt')

                            elif error_title == 'not enough money':
                                print('Not enough money')

                                # close bet to reset
                                final_outcome.click()
                                time.sleep(1)

                                # enter max amount in field
                                # data-target="menu-quick-deposit"
                                funds_element = driver.find_element('xpath', '//div[@data-target="menu-quick-deposit"]')
                                # remove $
                                funds = float(funds_element.find_element('tag name', 'div').find_element('tag name', 'span').get_attribute('innerHTML')[1:])
                                print('funds: ' + str(funds))

                                # reopen
                                final_outcome.click()
                                time.sleep(1)

                                #input_container = driver.find_element('class name', 'mod-KambiBC-to-win-input__container')
                                #print('input_container: ' + input_container.get_attribute('innerHTML'))
                                wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
                                # print('wager_field: ' + wager_field.get_attribute('outerHTML'))
                                # wager_field.clear()
                                # time.sleep(3)
                                # wager_field.clear()
                                # print('Cleared Wager')
                                # time.sleep(1)
                                # wager_field.send_keys(Keys.DELETE)
                                # print('deleted')
                                wager_field.send_keys(funds)
                                # #driver.execute_script("arguments[0].setAttribute('value',arguments[1])",wager_field, funds)
                                # print('wager_field: ' + wager_field.get_attribute('outerHTML'))
                                #WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "mod-KambiBC-stake-input__container"))).send_keys(funds)
                                time.sleep(1)
                                print('Input Funds')

                                place_bet_btn = driver.find_element('class name', 'mod-KambiBC-betslip__place-bet-btn')
                                place_bet_btn.click()
                                time.sleep(1)
                                print('Placed Bet')

                                close_receipt_btn = driver.find_element('class name', 'mod-KambiBC-betslip-receipt__close-button')
                                close_receipt_btn.click()
                                time.sleep(1)
                                print('Closed Receipt')

                        except:

                            print('Error Placing Max Bet')

                    # Navigate to bet page to confirm bet placed
                    #aria-label="Navigate to My Bets"
                    my_bets_btn = driver.find_element('xpath', '//button[@aria-label="Navigate to My Bets"]')
                    my_bets_btn.click()
                    print('Clicked My Bets')
                    time.sleep(3) # TEMP wait to manually check bet placed before closing
            # except:
            #     print('Odds Changed while placing bet')
                #time.sleep(100)
                # if odds changed for better then approve and place
                # else close and go to next pick

        elif website_name == 'draftkings':

            # === Log In ===
            logged_in = False
            login_result = login_website(website_name, driver, cookies_file, saved_cookies, url)
            if login_result == 'fail':
                close_bet_windows(driver, test=test, bet_dict=bet_dict)
                return
            
            while not logged_in:
                try:
                    wager_field = driver.find_element('class name', 'stake-input-value')#.find_element('tag name', 'input')
                    logged_in = True
                except:
                    print('Not Logged In Yet')
                    time.sleep(1)

            remove_old_bets(driver, website_name)

            # WARNING: must be sure of market limit based on tests
            # if unsure then use lowest conservative limit
            # eg big markets like moneyline, especially likely odds
            bet_size = determiner.determine_limit(bet_dict, website_name, pick_type, test)


            place_bet_btn = 'dk-place-bet-button__primary-text'


    
        
        
    # Close Window after placing bet
    # Close Window before going to next pick
    # bc only 1 window at a time
    # if not test:
    #     print('Close Bet Window\n')
    #     driver.close() # comment out to test

    # # always switch bot back to main window so it can click btns  
    # driver.switch_to.window(driver.window_handles[0])

    close_bet_windows(driver, test=test, bet_dict=bet_dict)


def refresh_outcome_button(driver):
    print('\n===Refresh Outcome Button===\n')

    driver.refresh()
    time.sleep(1)
    while True:
        sections = driver.find_elements('class name', 'KambiBC-bet-offer-category')
        print('num sections: ' + str(len(sections)))
        if len(sections) == 0:
            time.sleep(1)
        else:
            break

    

# click outcome btn to add to betslip
def click_outcome_btn(outcome_btn, driver):
    print('\n===Click Outcome Button===\n')

    try:
        outcome_btn.click()
        time.sleep(0.5)
        print('\nClicked Outcome Button\n')
    except Exception as e:
        print('\nERROR: Failed to click outcome button!\n', e)
        try:
            coordinates = outcome_btn.location_once_scrolled_into_view
            print('coordinates: ' + str(coordinates))
            driver.execute_script("window.scrollTo(coordinates['x'], coordinates['y'])")
            #driver.execute_script("arguments[0].scrollIntoView(true);", final_outcome)
        except Exception as e:
            print('\nERROR: Cannot find outcome button!\n', e)

            close_logged_out_popup(driver)
            # try again
            try:
                coordinates = outcome_btn.location_once_scrolled_into_view
                print('coordinates: ' + str(coordinates))
                driver.execute_script("window.scrollTo(coordinates['x'], coordinates['y'])")
            except Exception as e:
                print('\nERROR: Still cannot find outcome button after scroll to coords!\n', e)

                try:
                    # Scroll to top fails opt 1 so try opt 2
                    #driver.execute_script("window.scrollTo(0, 0)")  
                    driver.execute_script("window.scrollBy(0, -document.body.scrollHeight);")
                    
                    driver.execute_script("arguments[0].scrollIntoView(true);", outcome_btn)
                    driver.execute_script("arguments[0].click();", outcome_btn)
                except:
                    print('\nERROR: Still cannot find outcome button after scroll top, scroll into view, execute script click!\n', e)



                # outcome_btn = refresh_outcome_button(driver)

                # try:
                #     outcome_btn.click()
                #     time.sleep(0.5)
                #     print('\nClicked Outcome Button\n')
                # except:
                #     print('\nERROR: Still cannot find outcome button after Refresh!\n', e)

                
        try:
            outcome_btn.click()
            time.sleep(0.5)
            print('\nClicked Outcome Button\n')
        except Exception as e:
            print('\nERROR: Cannot click outcome button!\n', e)
    
    

# COPY TO CLIENT
def add_bet_to_betslip(final_outcome, driver, website_name):
    print('\n===Add Bet to Betslip===\n')

    #clear_betslip(driver)

    try:
        # final_outcome: 
        # <div data-touch-feedback="true" 
        #   class="sc-gEvEer kOrbku"><div data-touch-feedback="true" class="sc-eqUAAy kLwvTb"><div class="sc-fqkvVR cyiQDV">Over</div><div data-touch-feedback="true" class="sc-dcJsrY gCFiej">6.5</div></div><div data-touch-feedback="true" class="sc-iGgWBj kAIwQy"><div class="sc-jXbUNg jRmJQc"></div><div data-touch-feedback="true" class="sc-gsFSXq dqtSKK"><div data-touch-feedback="true" class="sc-kAyceB gLUWXi">-360</div></div></div></div>
        #print('final_outcome before click: ' + final_outcome.get_attribute('outerHTML'))
        # Determine if btn clicked if shown in betslip
        if not re.search('data-pressed=\"null\"', final_outcome.get_attribute('outerHTML')):
            print('Outcome Button Not Yet Clicked')
            click_outcome_btn(final_outcome, driver)
        else:
            print('Outcome Button Already Clicked')
            # problem is if just closed then registers as still clicked
            # so check if betslip open
            # problem is rare event so avoid wasting time
            # checking each time
            # instead wait for error to check and reclick outcome btn
            try:
                driver.find_element('class name', 'mod-KambiBC-stake-input__container')
            except:
                click_outcome_btn(final_outcome, driver)


        # always remove old bets after clicking bet 
        # bc glitch may not show betslip until outcome clicked
        remove_old_bets(driver, website_name)

    except:
        print('Error clicking outcome button! Refresh and Try again. ' + website_name)
        driver.refresh()
        time.sleep(1)

        # refind outcome btn?
        # from read market odds
        # no bc outcome not found for valid reason 
        # due to previous error closed window
        #final_outcome = reader.read_final_outcome(driver, website_name)
        click_outcome_btn(final_outcome, driver)
        #return final_outcome

    #print('final_outcome after click: ' + final_outcome.get_attribute('outerHTML'))      


# draftkings
def recheck_location(driver):#, place_bet_btn):#, website_name):
    print('\n===Recheck Location===\n')

    try:
        place_bet_btn = driver.find_element('class name', 'dk-place-bet-button__primary-text')
        place_bet_btn_text = place_bet_btn.get_attribute('innerHTML').lower()
        print('place_bet_btn_text: ' + place_bet_btn_text)
        if place_bet_btn_text == 'recheck location':
            #recheck_location(driver, place_bet_btn, website_name)
            place_bet_btn.click()

    except:
        print('No Place Bet Btn')
        return    

    loading = True
    while loading:
        try:
            # logged in if betslip
            driver.find_element('id', 'dom_betslip')
            loading = False
            print('\nChecked Location\n')
        except:
            print('Checking Location...')
            time.sleep(1)

# after logging in, wait for fields to load
def load_bet_page(driver, website_name, bet_dict, test, max_retries=3):

    wager_field = None
    load_retries = 0
    refresh_retries = 0
    logged_in = False
    while not logged_in and refresh_retries < max_retries:
        while not logged_in and load_retries < max_retries:
            try:
                # wager field not always there if bet closed during login
                # so look for place bet btn
                #try:
                wager_field = driver.find_element('class name', 'stake-input-value')#.find_element('tag name', 'input')
                logged_in = True
                # except:
                #     print('ERROR: No Wager Field')

                #try:
                driver.find_element('class name', 'place-button')
                logged_in = True
                # except:
                #     print('ERROR: No Place Bet Button')

            except:
                print('Not Logged In Yet')
                time.sleep(1)
                load_retries += 1

        if load_retries == max_retries:
            print('Failed to Load so Refresh and Retry')
            driver.refresh()
            time.sleep(1)
            refresh_retries += 1
            load_retries = 0


    if load_retries == max_retries:
        close_bet_windows(driver, test=test, bet_dict=bet_dict)
        return 

    remove_old_bets(driver, website_name)

    return wager_field

# just like place bet but only up to getting limit
# remove the final place bet click
# starts with window already open from reading actual odds
# side num and num windows tells us which window to go to
# side num refers to side of arb 1 or 2
def find_bet_limit(bet_dict, driver, cookies_file, saved_cookies, pick_type, test, side_num):
    print('\n===Find Bet Limit===\n')
    print('Input: side_num: ' + str(side_num) + '\n')
    #print('Input: bet_dict = {...} = ' + str(bet_dict) + '\n')
    #print('\nOutput: bet_limit = float\n')

    #display_bet_details(bet_dict)

    bet_limit = payout = 0

    # why does num windows return 3 when actuall 4 windows???
    num_windows = len(driver.window_handles)
    #print('num_windows: ' + str(num_windows))


    # if bet dict has bet1/bet2 then we know arb
    # so set single bet vals in dict
    if 'bet1' in bet_dict.keys():
        bet_key = 'bet' + str(side_num)
        source_key = 'source' + str(side_num)
        odds_key = 'odds' + str(side_num)
        actual_odds_key = 'actual odds' + str(side_num)
        link_key = 'link' + str(side_num)
        size_key = 'size' + str(side_num)
        outcome_key = 'outcome' + str(side_num)
        window_key = 'window' + str(side_num)

        bet_dict['bet'] = bet_dict[bet_key]
        bet_dict['source'] = bet_dict[source_key]
        bet_dict['odds'] = bet_dict[odds_key]
        bet_dict['actual odds'] = bet_dict[actual_odds_key]
        bet_dict['link'] = bet_dict[link_key]
        bet_dict['size'] = bet_dict[size_key]
        bet_dict['outcome'] = bet_dict[outcome_key]
        bet_dict['window'] = bet_dict[window_key]

    # switch to bet window returns None if cannot find final outcome
    # so no need to switch twice 
    # if final outcome fails after this then move on to next bet
    print('\nChange Window to Bet: ' + str(side_num) + '\n')
    driver.switch_to.window(bet_dict['window'])
    
    website_name = bet_dict['source']
    print('website_name = ' + website_name)
    url = bet_dict['link']

    market = bet_dict['market']
    odds = bet_dict['actual odds']

    final_outcome = None
    try:
        #print('final_outcome = ' + str(bet_dict['outcome'].get_attribute('outerHTML')))
        final_outcome = bet_dict['outcome']
        print('Final Outcome Up-to-Date')
    except Exception as e:
        print('Error getting final outcome: ', e)
        # we know correct window bc we stored window idx after opening window
        #print('Make Sure Correct Window')
        # attempt to get updated final outcome
        print('Attempt to refind outcome element.')

    # continue if no bet
    # should not reach this point bc actual odds would also be none
    if final_outcome is None:
        print('final_outcome none, Close Bet Windows\n')
        close_bet_windows(driver, side_num, test, bet_dict)
        return bet_limit, payout
    
    # get max number that is less than available funds
    # but always over known limit
    max_bet_size = determiner.determine_source_limit(website_name, market, odds) #determine_limit(bet_dict, website_name, pick_type, test)

    # if max bet 0 then limit NA so see if we know other side limit
    # OR use conservative limit

    if website_name == 'betmgm':

        
        login_result = login_website(website_name, driver, cookies_file, saved_cookies, url)
        if login_result == 'fail':
            close_bet_windows(driver, side_num, test, bet_dict)
            return

        wager_field = load_bet_page(driver, website_name, bet_dict, test)
        
        if wager_field is None:
            return

        attempted_bet = False
        while not attempted_bet:

            # login takes time so check if odds changed
            place_bet_btn = driver.find_element('class name', 'place-button')
            # check if enough funds
            place_btn_text = place_bet_btn.find_element('class name', 'ds-btn-text').get_attribute('innerHTML').lower()
            print('place_btn_text: ' + str(place_btn_text))
            # if odds changed, if arb, check new odds
            if re.search('accept', place_btn_text):
                # accept odds for now until we check other side of arb
                place_bet_btn.click()
                time.sleep(0.5)

                new_odds = '' # driver.find_element()
            
            #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
            placeholder = wager_field.get_attribute('placeholder')
            #print('placeholder: ' + placeholder)
            if not placeholder == '':
                wager_field.clear()
                time.sleep(0.5)
            wager_field.send_keys(max_bet_size)
            time.sleep(0.5)

            if re.search('deposit', place_btn_text):
                print('Not Enough Money')
                # do NOT bet all remaining funds
                # instead, check if remaining funds > source max bet size
                # we know funds < max bet size 
                # bc we entered max bet size into wager field, which alerts deposit
                # so we cannot risk entering remaining funds
                # until we know limit on other side
                # so use remaining funds as limit on this side
                remaining_funds = reader.read_remaining_funds(driver, website_name)
                # enter remaining funds into wager field to get payout
                wager_field.clear()
                time.sleep(0.5)
                wager_field.send_keys(remaining_funds)
                time.sleep(0.5)

                # remove , needed here bc returns here
                payout = re.sub(',','',driver.find_element('class name', 'betslip-summary-row--winnings').find_element('class name', 'betslip-summary-value').get_attribute('innerHTML').split('$')[1])
                payout = float(payout)
                print('payout: ' + str(payout))
                
                return remaining_funds, payout, wager_field, place_bet_btn


            # place_bet_btn.click()
            # time.sleep(1)
            # print('Placed Bet to Find Limit')
            # time.sleep(3) 
            # ===Click Place Bet Btn BetMGM===
            # needs fcn to account for glitches to ensure clean click
            # may fail with popup glitch 
            # which simply needs to be closed and retries
            click_place_btn(place_bet_btn, driver, website_name)
            # place_bet_btn.click()
            # time.sleep(1)
            # print('Placed Bet to Find Limit')
            # time.sleep(1) 

            # wait to finish loading
            loading = True
            while loading:
                try:
                    alert_msg = driver.find_element('class name', 'alert-content__message').get_attribute('innerHTML').lower() # Wager too high
                    print('alert_msg: ' + alert_msg)
                    loading = False
                    print('Done Loading placed bet to find limit')

                    if re.search('limit', alert_msg):
                        attempted_bet = True
                        print('Attempted Bet')

                    elif re.search('parlay', alert_msg):
                        print('Failed to Remove Old Pick so Try Again')
                        remove_old_bets

                    else:
                        # if not limit problem, then odds changed so close and continue
                        # if not limit problem, check if locked or odds changed
                        # if locked, remove bet from slip and close window
                        try:
                            btn_msg = driver.find_element('class name', 'place-button-message').get_attribute('innerHTML').lower() # Wager too high
                            print('\nUNKNOWN ERROR: btn_msg: ' + btn_msg)
                        except:
                            print('No Button Message')

                            # check for error alert dialog popup
                            # class geo-comply-error-validation-container
                            # class ds-button
                            try:
                                error_dialog = driver.find_element('class name', 'geo-comply-error-validation-container').get_attribute('innerHTML')
                                print('error_dialog: ' + error_dialog)
                                close_dialog_btn = driver.find_element('class name', 'ds-button')
                                loading = False
                                print('Done Loading')
                                close_dialog_btn.click()
                                time.sleep(1)
                                print('Closed Error Dialog')
                                # replace bet to find limit
                                # loops back around bc attempted bet still false
                            except:
                                print('No Error Yet. Loading placed bet to find limit...')
                    
                except KeyboardInterrupt:
                    loading = False
                except:
                    print('Loading placed bet to find limit...')
                    time.sleep(1)

        try:
            bet_limit = wager_field.get_attribute('value').split('$')[1] # or getText()
            print('bet_limit: ' + bet_limit)
        except Exception as e:
            print('\nERROR: Failed to get bet limit bc failed to remove old picks?\n')

        # $100.00 -> 100.00
        # class betslip-summary-row--winnings
        payout = driver.find_element('class name', 'betslip-summary-row--winnings').find_element('class name', 'betslip-summary-value').get_attribute('innerHTML').split('$')[1]
        # remove , done at end for all sources
        # payout = re.sub(',','',payout)
        # payout = float(payout)
        print('payout: ' + payout)

    elif website_name == 'betrivers':
        
        # source glitchy so sometimes betslip not shown
        # even tho bet selected
        # so already need to remove old picks after clicking current pick
        # so no need to clear in beginning, to save time
        #clear_betslip(driver)

        # click outcome btn to add to betslip
        add_bet_to_betslip(final_outcome, driver, website_name)
        #click_outcome_btn(final_outcome, driver, website_name)

        # Check if odds changed after clicking outcome btn
        # problem is glitch changes back and forth
        # so take only first change
        betslip_odds = reader.read_betslip_odds(driver, website_name)
        # if betslip odds None, error reading odds
        # if betslip odds '', bet closed
        # TEST
        betslip_odds = bet_dict['actual odds'] # TEST until can read betslip odds to compare
        if betslip_odds != '':
            # update odds on side of arb
            bet_dict[actual_odds_key] = betslip_odds
            # compare init actual odds
            actual_odds = bet_dict['actual odds']
            if int(betslip_odds) < int(actual_odds):
                # check if still valid
                if not determiner.determine_valid_arb_odds(bet_dict):
                    close_bet_windows(driver, side_num, test, bet_dict)
                    return

        login_result = login_website(website_name, driver, cookies_file, saved_cookies, url)
        if login_result == 'fail':
            close_bet_windows(driver, side_num, test, bet_dict)
            return
        
        # remove bets before sending keys bc might erase
        #remove_old_bets(driver, website_name)

        # add max bet size to wager field
        try:   
            wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
        except:
            try:
                final_outcome.click()
                print('Clicked Final Outcome')
                time.sleep(1)
                # remove bets before sending keys bc might erase
                remove_old_bets(driver, website_name)

                wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
                print('Found Wager Field')
            except Exception as e:
                print('Failed to Click Final Outcome: ', e)
                close_bet_windows(driver, side_num, test, bet_dict)
                return bet_limit, payout

        

        #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
        wager_field.send_keys(max_bet_size)

        # click Place Bet to find limit
        place_bet_btn = driver.find_element('class name', 'mod-KambiBC-betslip__place-bet-btn')
        #print('place_bet_btn: ' + place_bet_btn.get_attribute('innerHTML'))
            
        # wait to finish loading
        # the only way to confirm button pressed is by output
        # so need to include btn press in load loop
        # in case btn press fails
        loading = True
        load_retries = 0
        max_retries = 3
        while loading and load_retries < max_retries:

            try:
                # Need to click twice for this website
                place_bet_btn.click()
                time.sleep(0.5) # need wait for bet to fully load and submit before moving on
                try:
                    place_bet_btn.click()
                    time.sleep(0.5)
                except:
                    print('Failed to Click Place Bet second time so check if already placed?')
                
                print('Placed Bet to find limit')
                #break
                #placed_bet = True
            except KeyboardInterrupt:
                print('Exit')
                exit()
            except:
                print('Failed to click Place Bet Button. Retry.')
                load_retries += 1
                time.sleep(1)
                place_bet_btn_text = driver.find_element('class name', 'mod-KambiBC-betslip__place-bet-btn').get_attribute('innerHTML').lower()
                print('place_bet_btn_text: ' + place_bet_btn_text)
                if place_bet_btn_text == 'approve odds change':
                    # close windows and move on
                    print('Odds Changed, so skip')
                    close_bet_windows(driver, side_num, test, bet_dict)
                    return bet_limit, payout, wager_field, place_bet_btn
                else:
                    # if failed to click bc not add to betslip
                    # so add to betslip
                    add_bet_to_betslip(final_outcome, driver, website_name)
                    #click_outcome_btn(final_outcome, driver, website_name)

            try:
                error_title = driver.find_element('class name', 'mod-KambiBC-betslip-feedback__title').get_attribute('innerHTML').lower() # Wager too high
                print('error_title: ' + error_title)

                loading = False
                print('Done Loading placed bet to find limit')

                if error_title == 'not enough money':
                    print('Not enough money')
                    remaining_funds = reader.read_remaining_funds(driver, website_name)
                    return remaining_funds, payout, wager_field, place_bet_btn
                elif error_title == 'bet offer suspended':
                    # close window and move on
                    close_bet_windows(driver, side_num, test, bet_dict)
                    return bet_limit, payout, wager_field, place_bet_btn
                elif error_title == 'odds changed':
                    # ideally check other side to see if odds still in range
                    # OR
                    # close window and move on
                    close_bet_windows(driver, side_num, test, bet_dict)
                    return bet_limit, payout, wager_field, place_bet_btn

                # Sorry, the maximum allowed wager is $4.01.
                # sorry, the maximum allowed wager is <span data-prop="0"><span class="mod-kambibc-betslip-feedback__currency">$25.87</span></span>.
                error_element = driver.find_element('class name', 'mod-KambiBC-betslip-feedback__paragraph')
                error_msg = error_element.get_attribute('innerHTML').lower() 
                print('error_msg: ' + error_msg)

                # $100.00 -> 100.00
                # mod-kambibc-betslip-feedback__currency
                # error finding element so reinspect or just split from error msg
                #feedback_currency = driver.find_element('class name', 'mod-kambibc-betslip-feedback__currency').get_attribute('innerHTML')
                #feedback_currency = error_msg.split('</span></span>')[0]
                #print('feedback_currency: ' + feedback_currency)
                #[:-1] # remove final period not needed bc span has only money
                if re.search('\$', error_msg):
                    bet_limit = error_msg.split('$')[1].split('<')[0]
                    print('bet_limit: ' + bet_limit)
                    
                    # click back btn to see payout
                    back_btn = driver.find_element('class name', 'mod-KambiBC-betslip-button')
                    print('back_btn: ' + back_btn.get_attribute('innerHTML'))
                    back_btn.click()
                    time.sleep(1)
                    print('Clicked Back Btn to see payout')

                    payout = driver.find_element('class name', 'mod-KambiBC-js-betslip-summary__potential-payout-value').get_attribute('innerHTML').split('$')[1]
                    # remove , done at end for all sources
                    # payout = re.sub(',','',payout)
                    # payout = float(payout)
                    print('payout: ' + str(payout))

            except:
                print('Loading placed bet to find limit...')
                time.sleep(1)

        # # $100.00 -> 100.00
        # # mod-kambibc-betslip-feedback__currency
        # # error finding element so reinspect or just split from error msg
        # #feedback_currency = driver.find_element('class name', 'mod-kambibc-betslip-feedback__currency').get_attribute('innerHTML')
        # #feedback_currency = error_msg.split('</span></span>')[0]
        # #print('feedback_currency: ' + feedback_currency)
        # #[:-1] # remove final period not needed bc span has only money
        # if re.search('\$', error_msg):
        #     bet_limit = error_msg.split('$')[1].split('<')[0]
        #     print('bet_limit: ' + bet_limit)
            
        #     # click back btn to see payout
        #     back_btn = driver.find_element('class name', 'mod-KambiBC-betslip-button')
        #     print('back_btn: ' + back_btn.get_attribute('innerHTML'))
        #     back_btn.click()
        #     time.sleep(1)
        #     print('Clicked Back Btn to see payout')

        #     payout = driver.find_element('class name', 'mod-KambiBC-js-betslip-summary__potential-payout-value').get_attribute('innerHTML').split('$')[1]
        #     # remove , done at end for all sources
        #     # payout = re.sub(',','',payout)
        #     # payout = float(payout)
        #     print('payout: ' + str(payout))

        
    elif website_name == 'draftkings':

        # === Log In ===
        logged_in = False
        login_result = login_website(website_name, driver, cookies_file, saved_cookies, url)
        if login_result == 'fail':
            close_bet_windows(driver, side_num, test, bet_dict)
            return
        
        # WARNING: must be sure of market limit based on tests
        # if unsure then use lowest conservative limit
        # eg big markets like moneyline, especially likely odds

        try:

            place_bet_btn = driver.find_element('class name', 'dk-place-bet-button__primary-text')

            attempted_bet = False
            while not attempted_bet:
                place_bet_btn_text = place_bet_btn.get_attribute('innerHTML').lower()
                print('place_bet_btn_text: ' + place_bet_btn_text)

                if re.search('accept', place_bet_btn_text):
                    # accept odds for now until we check other side of arb
                    place_bet_btn.click()
                elif re.search('remove', place_bet_btn_text):
                    print('\nWarning: Bet Closed\n')
                    close_bet_windows(driver, side_num, test, bet_dict)

                
                wager_field = driver.find_element('class name', 'betslip-wager-box__input')
                #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
                placeholder = wager_field.get_attribute('placeholder')
                #print('placeholder: ' + placeholder)
                if not placeholder == '0.00':
                    wager_field.clear()
                    time.sleep(0.5)
                wager_field.send_keys(max_bet_size)
                time.sleep(0.5)

                place_bet_btn.click()
                time.sleep(1)
                print('Placed Bet to Find Limit')

                # wait to finish loading
                loading = True
                while loading:
                    try:
                        alert_msg = driver.find_element('class name', 'dk-action-required__title').get_attribute('innerHTML').lower() # Wager too high
                        print('alert_msg: ' + alert_msg)
                        loading = False
                        print('Done Loading placed bet to find limit')

                        if re.search('too high', alert_msg):
                            attempted_bet = True
                            print('Attempted Bet')
                    except KeyboardInterrupt:
                        loading = False
                    except:
                        print('Loading placed bet to find limit...')
                        time.sleep(1)

            # after attempted bet to find limit
            wager_field = driver.find_element('class name', 'betslip-wager-box__input')
            bet_limit = wager_field.get_attribute('value')#.split('$')[1] # or getText()
            print('bet_limit: ' + bet_limit)

            # $100.00 -> 100.00
            payout = driver.find_element('class name', 'betslip-regular-payout__label-value').get_attribute('innerHTML').split('$')[1]
            print('payout: ' + payout)

            # do we need to click leave in betslip
            # to see odds changes? is it glitchy? YES
            # also important so place bet can click btn
            # and we can diff bt odds change vs wager change
            # class dk-betslip-tertiary-button__wrapper
            betslip_btn = driver.find_element('class name', 'dk-betslip-tertiary-button__wrapper')
            betslip_btn.click()
            print('Clicked Leave in Betslip')


        except Exception as e:
            print('\nUnknown Errror While Finding Bet Limit!\n', e)


    # Do not close window after finding limit
    
    bet_limit = float(bet_limit)
    payout = re.sub(',', '', payout)
    payout = float(payout)
    print('bet_limit: ' + str(bet_limit))
    print('payout: ' + str(payout))

    # if bet limit 0, close and move on bc no use
    if bet_limit == 0:
        print('\nWarning: Bet Limit 0\n')
        close_bet_windows(driver, side_num, test, bet_dict)

    return bet_limit, payout, wager_field, place_bet_btn


# given other side assumed odds
# unless this side odds change, 
# we must assume last reading other side is accurate
# in arb['actual odds<other side num>']
def place_arb_bet(driver, arb, side_num, test):

    print('\n===Place Arb Bet: ' + str(side_num) + '===\n')

    # change to bet side window
    window_key = 'window' + str(side_num)
    print('window_key: ' + window_key)
    window_handle = arb[window_key]
    print('window_handle: ' + window_handle)
    driver.switch_to.window(window_handle)
    print('Changed to Bet ' + str(side_num))# + ': Window ' + str(window_idx))
    
    # enter bet 1
    wager_field_key = 'wager field' + str(side_num)
    source_key = 'source' + str(side_num)
    outcome_key = 'outcome' + str(side_num)
    print('wager_field_key: ' + wager_field_key)
    print('source_key: ' + source_key)
    print('outcome_key: ' + outcome_key)
    wager_field = arb[wager_field_key]
    # problem sending keys in betrivers after leaving window
    source = arb[source_key]
    outcome = arb[outcome_key]
    print('source: ' + source)
    if source == 'betrivers':
        outcome.click() # close betslip
        time.sleep(0.5)
        outcome.click() # reopen betslip
        wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
    
    # bet_size1 = arb['size1']
    # if re.search('\$', str(bet_size1)):
    size_key = 'size' + str(side_num)
    print('size_key: ' + size_key)
    bet_size = arb[size_key].split('$')[1]
    print('bet_size: ' + bet_size)
    if test:
        bet_size = '1'

    try:
    
        # rewrite in bet size
        wager_field.clear()
        wager_field.send_keys(bet_size)
        print('Entered Bet ' + str(side_num) + ': ' + bet_size)
        time.sleep(0.1)
    except Exception as e:
        print('\nERROR: Failed to rewrite in bet size!\n', e)
        #close_bet_windows(driver, side_num, test, arb)
        return

    # click bet side
    placed_bet = False
    bet_placed_key = 'placed' + str(side_num)
    arb[bet_placed_key] = placed_bet
    valid_odds = True
    bet_open = True
    if not test:
        # MAYBE New place bet btn at this point
        # bc found limit
        # so now need to accept and place
        # but some interface may have some btn
        # so try same and if fails get new
        place_btn_key = 'place btn' + str(side_num)
        print('place_btn_key: ' + place_btn_key)
        place_btn = arb[place_btn_key]

        other_side_bet_placed = False
        other_side_num = 2
        if side_num == 2:
            other_side_num = 1
        other_side_bet_placed_key = 'placed' + str(other_side_num)
        if other_side_bet_placed_key not in arb.keys():
            arb[other_side_bet_placed_key] = other_side_bet_placed
        other_side_bet_placed = arb[other_side_bet_placed_key]

        # check if odds changed
        # if side 1 odds changed, need to check side 2 before placing
        # if side 2 odd changed, side 1 already placed, so place anyway
        while not placed_bet and bet_open:# and valid_odds:
            # case 1, odds same, bet accepted
            # case 2, side 1 odds changed, check side 2
            # case 2a betrivers: how to tell if glitch odds changed?
            # - compare to init odds
            # case 3, side 2 odds changed, approve and place
            try:
                place_btn_text = place_btn.get_attribute('innerHTML').lower()
            except Exception as e:
                print('Failed to Click Place Bet Button! ', e)
                # place_bet_btn = driver.find_element('class name', 'mod-KambiBC-betslip__place-bet-btn')
                place_btn = reader.find_place_bet_button(driver, source)
                place_btn_text = place_btn.get_attribute('innerHTML').lower()
            print('place_btn_text: ' + place_btn_text)
            
            # new_odds = determiner.determine_odds_changed(driver, source)
            # if new_odds is not None:
            #     actual_odds_key = 'actual odds' + str(side_num)
            #     arb[actual_odds_key] = new_odds
            #     if source == 'betrivers' and new_odds == init_odds:
            #         print('Approve Odds')
            #     if side_num == 1:
            #         return arb

            if re.search('approve|accept', place_btn_text):
                try:
                    print('Approve Odds')
                    place_btn.click()
                    print('Clicked Approve Odds')

                    # if source == betrivers,
                    # determine if odds changed glitch 
                    # or actually need to check other side

                    new_odds = reader.read_betslip_odds(driver, source)
                    # actual_odds_key = 'actual odds' + str(side_num)
                    # arb[actual_odds_key] = new_odds

                    # If other side not yet placed:
                    # check if odds changed other side
                    if not other_side_bet_placed:
                        print('Other Side Bet Not Yet Placed')
                        # if other side not yet placed, check other side
                        #return arb
                    
                    # If other side already placed:
                    # determine if need to change bet size
                    else:
                        print('Other Side Bet Already Placed')
                        # if odds still in arb range, get new bet size
                        # to match payout other side
                        # if other side already placed, keep same bet size
                        
                        
                        # if not determiner.determine_valid_arb_odds(arb):
                        #     bet_size = ''


                except Exception as e:
                    print('Failed to Click Approve Odds')


            try:
                print('Place Bet')
                place_btn.click()
                # betrivers glitch needs 2 clicks
                if source == 'betrivers':
                    try:
                        place_btn.click()
                        print('Clicked Place Bet Twice')
                    except:
                        print('Failed to Click Place Bet 2nd Time')

                print('Clicked Place Bet')
                #time.sleep(3)
                # confirm placed bet 1
                
                start_time = datetime.today()
                receipt_btn = None
                loading = True
                while loading:
                    try:
                        # look for loading bar or spinner
                        # or close receipt btn
                        if source == 'betmgm':
                            driver.find_element('tag name', 'bs-digital-result-state').find_element('class name', 'result-summary__actions').find_element('tag name', 'button')
                        elif source == 'betrivers':
                            receipt_btn = driver.find_element('class name', 'mod-KambiBC-betslip-receipt__close-button')
                        elif source == 'draftkings':
                            driver.find_element('class name', 'receipt')
                        
                        loading = False
                        print('Done Loading')
                    except:
                        print('Loading bet receipt...')
                        # check if bet placed
                        if source == 'betrivers':
                            try:
                                place_btn.click()
                                print('Clicked Place Bet Again')
                            except:
                                print('Failed to Click Place Again')
                                # if arb bet 1, close and move on
                                # if arb bet 2, arb 1 already placed so keep open until becomes available again
                                return 
                            
                        time.sleep(0.5)

                end_time = datetime.today()
                duration = (end_time - start_time).seconds
                start_time = str(start_time.hour) + ':' + str(start_time.minute) + ':' + str(start_time.second)
                end_time = str(end_time.hour) + ':' + str(end_time.minute) + ':' + str(end_time.second)
                print('start_time: ' + str(start_time))
                print('end_time: ' + str(end_time))
                print('duration: ' + str(duration) + ' seconds')

                placed_bet = True
                arb[bet_placed_key] = placed_bet

                # only betrivers close receipt bc keep window open
                # do all other windows auto close receipt when window closes
                # or does receipt appear still when new window opens in same source???
                # keep receipt open for side 1 until side 2 placed, to compare
                # and if side 2, closing receipt is not needed bc window closed
                # if receipt_btn is not None:
                #     print('Close Receipt')
                #     receipt_btn.click()

            except Exception as e:
                print('Failed to Click Place Bet Btn: ', e)

                # check odds changed

                # check odds went up so new limit
                # bet at limit

                # check bet closed
                bet_open = False

                # if only suspended, 
                # then keep window open until becomes available again
                # so need to keep control on suspended window
                # for 1 minute??? and then check back every minute???

        
    print('\nPlaced Arb Bet: ' + str(side_num) + '\n')
    return arb


def place_bets_simultaneously(driver, arb, test):
    print('\n===Place Bets Simultaneously===\n')
    #print('Input: arb = {...} = ' + str(arb) + '\n')

    # display updated details since before finding limits
    # like bet size
    # and actual odds
    display_bet_details(arb)

    bet1_placed = bet2_placed = False
    while not bet1_placed or not bet2_placed:
        if not bet1_placed:
            side_num = 1
            arb = place_arb_bet(driver, arb, side_num, test)
            if arb is None:
                return
            bet1_placed = arb['placed1']

        # if side 1 odds changed while placing bet
        # need to check side 2 before placing side 1
        # and since then moved to side 2, also placed side 2
        # before it has a chance to change as well

        if not bet2_placed:
            side_num = 2
            arb = place_arb_bet(driver, arb, side_num, test)
            if arb is None:
                return
            bet2_placed = arb['placed2']

    print('\nPlaced Bets Simultaneously\n')

    # pause for video
    # to confirm bets placed
    time.sleep(3)


# input adjustable arb deepcopy of init arb
# so it can be updated without affecting init log
def place_arb_bets(arb, driver, cookies_file, saved_cookies, pick_type, test):
    print('\n===Place Arb Bets===\n')
    #print('Input: arb = {...} = ' + str(arb) + '\n')

    num_windows = len(driver.window_handles)
    #print('num_windows: ' + str(num_windows))

    

    # bet1
    # bet_dict = {'market':arb['market'], 
	# 			'bet':'Josh Kelly', 
	# 			'odds':'+105', 
	# 			'game':'Josh Kelly vs Liam Smith',
	# 			'source':'betmgm',
	# 			'sport':'boxing',
	# 			'league':'international boxing',
	# 			'value':'5.0',
	# 			'size':'$3.00',
	# 			'game date':'Sat Sep 21 2024',
	# 			'link':'https://sports.ny.betmgm.com/en/sports/events/16058791?options=16058791-1139065602--1022063921'}
	
    # does dict need deepcopy? Yes
    # update new arb with new data 
    # but keep init arb raw to compare to new arbs
    # to make sure no duplicates
    # already saved in monitor after read actual odds
    # bc added actual odds
    #arb_bets = copy.deepcopy(arb)

    # go up to finding limit
    # and then go to other side to get limit
    # we need to get wager field and place btn to find limit
    # so save them here and pass them to place bet fcn
    # so we do not need to get them twice
    # BUT does driver.find_element actually take more time than retrieving from memory? probably
   
    side_num = 1

    # dk not yet enabled
    if arb['source1'] == 'draftkings' or arb['source2'] == 'draftkings':
        print('\nDK not yet enabled for auto arb. NEED to enable.')
        close_bet_windows(driver, side_num=2, test=test, bet_dict=arb)
        return
    
    bet_limit_data = find_bet_limit(arb, driver, cookies_file, saved_cookies, pick_type, test, side_num)
    if bet_limit_data is None:
        return
    
    bet_limit1 = bet_limit_data[0]
    arb['limit1'] = bet_limit1
    arb['payout1'] = bet_limit_data[1]
    arb['wager field1'] = bet_limit_data[2]
    arb['place btn1'] = bet_limit_data[3]

    # at this point we checked actual odds 
    # but now that we logged in and found limit, odds may have changed
    # so do we want to immediately close or leave open in case it changes back???
    
    # if bet still available, but odds changed
    # need to compare with other side recently read odds
    # before determining if we want to find bet 2 limit
    #updated_odds1, arb['actual odds2']
    #arb['updated odds1'] = bet_limit_data[4]
    # determine_valid_arb_odds(arb)


    # if bet suspended, will return 0
    # for now just close and move on
    # window already closed in find bet limit fcn
    if bet_limit1 == 0:
        return 
    
    side_num = 2
    bet_limit_data = find_bet_limit(arb, driver, cookies_file, saved_cookies, pick_type, test, side_num)
    if bet_limit_data is None:
        return
    
    bet_limit2 = bet_limit_data[0]
    arb['limit2'] = bet_limit2
    arb['payout2'] = bet_limit_data[1]
    arb['wager field2'] = bet_limit_data[2]
    arb['place btn2'] = bet_limit_data[3]

    bet1_size, bet2_size = determiner.determine_arb_bet_sizes(arb)
    
    arb['size1'] = '$' + str(bet1_size)
    arb['size2'] = '$' + str(bet2_size)

    if bet_limit2 == 0:
        return 

    # write in and place bets
    place_bets_simultaneously(driver, arb, test)




    print('Done Placing Both Bets Auto Arb, so close windows')
    close_bet_windows(driver, side_num, test, arb)

    #print('arb: ' + str(arb))
    

# write 1 arb in post
# no need to send mobile
def write_arb_to_post(arb, client):#, post=False):
    print('\n===Write Arb to Post===\n')
    #print('arb = {val:x, ...} = ' + str(arb)) 

    props_str = ''
    
    # Need diff string for each channel:
    # 1. all
    # 2. home runs
    # 3. new user
		
    # for test_pick in test_picks:
    # 	print('\n' + str(test_pick))

    # all props str
    all_props_str = '' # advanced when limited need to find more exploits
    new_user_props_str = '' # changes constantly as user needs to blend in as normal
    #for arb_idx in range(len(arbs)):
    #for arb_idx, arb in arbs.items():
    #arb = arbs[arb_idx]

    value = arb['value']
    #value_str = 'Value:\t' + value + '%'
    game = arb['game']
    #game_str = 'Game:\t' + game
    market = arb['market']
    #market_str = 'Market:\t' + market

    bet1 = arb['bet1']
    # bet1_str = 'Bet 1:\t' + bet1
    bet2 = arb['bet2']
    # bet2_str = 'Bet 2:\t' + bet2
    odds1 = arb['odds1']
    # odds1_str = 'Odds 1:\t' + odds1
    odds2 = arb['odds2']
    # bet2_str = 'Bet 2:\t' + bet2
    link1 = arb['link1']
    link2 = arb['link2']
    source1 = arb['source1'].title()
    source2 = arb['source2'].title()

    size1 = arb['size1']
    size2 = arb['size2']

    game_date = arb['game date']
    game_time = arb['game time']

    
    # Make list of sizes depending on limit, from 1000 to 100, every 100
    # size1_options = []
    # size2_options = []
    max_limit = 1000
    # Better to make hedge bet rounder number bc seems more normal/rec
    # size1 = converter.convert_odds_to_bet_size(odds1, odds2, max_limit)
    # size1_str = '$' + str(size1)
    # size2_str = '$' + str(max_limit)
    size1_float = float(size1.split('$')[1])

    # compute payout, given odds and bet size
    # For positive American odds, divide the betting odds by 100 and multiply the result by the amount of your wager (Profit = odds/100 x wager). 
    # With negative odds, you divide 100 by the betting odds, then multiply that number by the wager amount (Profit = 100/odds x wager).
    # take positive side bc = both sides
    profit = str(converter.round_half_up(int(odds2) / 100 * max_limit) - size1_float)
    #print('profit: ' + profit)


    # Format Message
    # Top part 4 lines of msg shows in notification preview 
    # so show useful info to decide if need to see more
    # 1. which books to avoid limits
    # 2. market/prop to go to
    # 3. odds to double check
    # 4. value to see how important/valuable
    # props_str += bet1 + ', ' + bet2 + '\t\t\t\t'
    # props_str += game + '\t'
    # props_str += market + '\t|\t'
    # props_str += odds1 + ', ' + odds2 + '\t|\t'
    # props_str += value + '%' + '\t|\t'

    # props_str += '\n' + bet1 + ', ' + bet2 + '\t\n'
    # props_str += odds1 + ', ' + odds2 + ' - \n' # + '\t'#|\t'

    #arb_num = str(arb_idx + 1)
    props_str = '\n===Arb===\n'
    props_str += '\n' + source1 + ' ' + odds1 + ', ' + source2 + ' ' + odds2 +'. \n\n'
    props_str += game + ' - \n\n'
    props_str += market + ' - \n\n\n'

    props_str += source1 + ', ' + source2 +'. \n\n'
    props_str += bet1 + ', ' + bet2 + ' - \n\n'
    props_str += odds1 + ', ' + odds2 + ' - \n\n'
    props_str += size1 + ', ' + size2 + ' - \n\n'
    #props_str += value + '%' + ' - \n\n'

    props_str += game_date + ', ' + game_time + ' - \n\n\n'

    props_str += 'LINK 1:\n' + link1 + ' \n\n'
    props_str += 'LINK 2:\n' + link2 + ' \n\n\n'
    

    # split player and market in given market field
    # so we can see market at the top and decide if we can take the bet or if limited or suspicious
    # player = ''
    # if re.search('-', market):
    #     market_data = market.split(' - ')
    #     player = market_data[0].strip()
    #     market = market_data[1].strip()
    # #props_str += '\nBETS: ' + bet1 + ' ' + odds1 + ', ' + bet2 + ' ' + odds2 +'. \n\n'
    # props_str += '\nSOURCE 1: ' + source1 + ', ' + odds1 + ', ' + bet1 + ' \n'
    # props_str += 'SOURCE 2: ' + source2 + ', ' + odds2 + ', ' + bet2 + ' \n\n'
    # if player != '':
    #     props_str += 'PLAYER: ' + player + ' \n\n'
    # props_str += 'MARKET: ' + market + ' \n\n'
    # #props_str += 'BETS: ' + bet1 + ', ' + bet2 + ' \n\n'
    # props_str += 'GAME: ' + game + ' \n\n'
    #props_str += 'TIME: ' + game_time + ' \n\n'

    props_str += 'VALUE: ' + value + '% \n\n'
    props_str += 'PROFIT: $' + profit + ' \n\n'

    
    

    # if Betrivers show range bc inaccurate reading
    # props_str += '\n' + value + '%\n'

    # props_str += '\n' + game + '\n'

    # props_str += '\n' + market + '\n'

    # Betrivers		Fanatics
    # -110			+110
    # $1200			$1000
    # -105			+110
    # $1250			$1000
    # props_str += '\n' + bet1 + '\t' + bet2

    # props_str += '\n' + odds1 + '\t' + odds2

    # props_str += '\n' + size1_str + '\t' + size2_str

    arb_table = [[source1, '', source2], [odds1, '', odds2], [size1, '', size2]]

    props_str += '\n' + tabulate(arb_table)

    props_str += '\n==================\n==================\n\n'

    # always add to all props str
    all_props_str += props_str
    # but selectively add to select channels
    if not re.search('Home Run', market):
        # add to new user str bc they avoid home runs
        new_user_props_str += props_str

    cur_time = datetime.today().time()
    timestamp = str(cur_time.hour) + ':' + str(cur_time.minute)
    print('\nTimestamp: ' + timestamp + '\n')
    print(all_props_str)
    #print(tabulate(arb_table))
    # print('New User Arbs')
    # print(new_user_props_str)

    # separate props into diff channels for specific types of users
    # 1 channel for all possible
    # 1 channel for new user avoiding home runs
    # 1 channel for limited users who can take home runs on specific apps
    # Do not post home runs to general channel bc only use on limited apps
    # post_arbs = []
    # for pick in new_picks:
    #     arb_market = pick[market_idx]
    #     if not re.search('Home Run', arb_market):
    #         post_arbs.append(pick)


    #send msg on slack app
    post = True # send to log so we can see if arb still available later
    print('Post: ' + str(post) + '\n\n')
    if post:
        # to avoid double msg, 
        # only apply 1 channel per user
        # OR do not repeat arbs
        # BUT all will repeat all which are separated into channels
        post_all = True # for testing all arbs before finalizing all category channels
        if all_props_str != '' and post_all:
            client.chat_postMessage(
                channel='all-arbs',
                text=props_str,
                username='Ball'
            )

        elif new_user_props_str != '':
            client.chat_postMessage(
                channel='ball', # arbitrary name given to first channel
                text=props_str,
                username='Ball'
            )

# def write_arb_to_post(arb, client, post=False):
#     # print('\n===Write Arb to Post===\n')
#     # print('arb: ' + str(arb))

#     props_str = ''

#     val_idx = 0
#     game_idx = 1
#     market_idx = 2
#     bet_idx = 3
#     source1_idx = 4
#     source2_idx = 5
#     odds1_idx = 6
#     odds2_idx = 7
#     link1_idx = 8
#     link2_idx = 9

    
# 	# Need diff string for each channel:
#     # 1. all
#     # 2. home runs
#     # 3. new user
		
#     # for test_pick in test_picks:
#     # 	print('\n' + str(test_pick))

#     # all props str
#     new_user_props_str = '' # changes constantly as user needs to blend in as normal


#     value = arb[val_idx]
#     #value_str = 'Value:\t' + value + '%'
#     game = arb[game_idx]
#     #game_str = 'Game:\t' + game
#     market = arb[market_idx]
#     #market_str = 'Market:\t' + market
#     bet = arb[bet_idx]

#     source1 = arb[source1_idx]
#     # bet1_str = 'Bet 1:\t' + bet1
#     source2 = arb[source2_idx]
#     # bet2_str = 'Bet 2:\t' + bet2
#     odds1 = arb[odds1_idx]
#     # odds1_str = 'Odds 1:\t' + odds1
#     odds2 = arb[odds2_idx]
#     # bet2_str = 'Bet 2:\t' + bet2
#     link1 = arb[link1_idx]
#     link2 = arb[link2_idx]

    
#     # Make list of sizes depending on limit, from 1000 to 100, every 100
#     size1_options = []
#     size2_options = []
#     max_limit = 1000
#     # Better to make hedge bet rounder number bc seems more normal/rec
#     size1 = converter.convert_odds_to_bet_size(odds1, odds2, max_limit)
#     size1_str = '$' + str(size1)
#     size2_str = '$' + str(max_limit)

#     # compute payout, given odds and bet size
#     # For positive American odds, divide the betting odds by 100 and multiply the result by the amount of your wager (Profit = odds/100 x wager). 
#     # With negative odds, you divide 100 by the betting odds, then multiply that number by the wager amount (Profit = 100/odds x wager).
#     # take positive side bc = both sides
#     profit = str(converter.round_half_up(int(odds2) / 100 * max_limit) - size1)
#     #print('profit: ' + profit)


#     # Format Message
#     # Top part 4 lines of msg shows in notification preview 
#     # so show useful info to decide if need to see more
#     # 1. which books to avoid limits
#     # 2. market/prop to go to
#     # 3. odds to double check
#     # 4. value to see how important/valuable
#     # props_str += bet1 + ', ' + bet2 + '\t\t\t\t'
#     # props_str += game + '\t'
#     # props_str += market + '\t|\t'
#     # props_str += odds1 + ', ' + odds2 + '\t|\t'
#     # props_str += value + '%' + '\t|\t'

#     # props_str += '\n' + bet1 + ', ' + bet2 + '\t\n'
#     # props_str += odds1 + ', ' + odds2 + ' - \n' # + '\t'#|\t'

#     props_str = '\n===Arb===\n'
#     props_str += '\n' + source1 + ' ' + odds1 + ', ' + source2 + ' ' + odds2 +'. \n\n'
#     props_str += game + ' - \n\n'
#     props_str += market + ' - \n\n'
#     props_str += bet + ' - \n\n'
#     props_str += value + '%' + ' - \n\n'
    

#     # split player and market in given market field
#     # so we can see market at the top and decide if we can take the bet or if limited or suspicious
#     player = ''
#     if re.search('-', market):
#         market_data = market.split('-')
#         player = market_data[0].strip()
#         market = market_data[1].strip()
#     #props_str += '\nBETS: ' + bet1 + ' ' + odds1 + ', ' + bet2 + ' ' + odds2 +'. \n\n'
#     props_str += '\nSOURCE 1: ' + source1 + ', ' + odds1 + ' \n'
#     props_str += 'SOURCE 2: ' + source2 + ', ' + odds2 + ' \n\n'
#     props_str += 'MARKET: ' + market + ', ' + bet + ' \n\n'
#     props_str += 'GAME: ' + game + ' \n\n'
#     if player != '':
#         props_str += 'PLAYER: ' + player + ' \n\n'
#     props_str += 'VALUE: ' + value + '% \n\n'
#     props_str += 'PROFIT: $' + profit + ' \n\n'
#     props_str += 'LINK 1: ' + link1 + ' \n'
#     props_str += 'LINK 2: ' + link2 + ' \n\n'
    

#     # if Betrivers show range bc inaccurate reading
#     # props_str += '\n' + value + '%\n'

#     # props_str += '\n' + game + '\n'

#     # props_str += '\n' + market + '\n'

#     # Betrivers		Fanatics
#     # -110			+110
#     # $1200			$1000
#     # -105			+110
#     # $1250			$1000
#     # props_str += '\n' + bet1 + '\t' + bet2

#     # props_str += '\n' + odds1 + '\t' + odds2

#     # props_str += '\n' + size1_str + '\t' + size2_str

#     arb_table = [[source1, '', source2], [odds1, '', odds2], [size1_str, '', size2_str]]

#     props_str += '\n' + tabulate(arb_table)

#     props_str += '\n==================\n==================\n\n'


#     # but selectively add to select channels
#     # if not re.search('Home Run', market):
#     #     # add to new user str bc they avoid home runs
#     #     new_user_channel = True


#     #print(tabulate(arb_table))
#     # print('New User Arbs')
#     # print(new_user_props_str)

#     # separate props into diff channels for specific types of users
#     # 1 channel for all possible
#     # 1 channel for new user avoiding home runs
#     # 1 channel for limited users who can take home runs on specific apps
#     # Do not post home runs to general channel bc only use on limited apps
#     # post_arbs = []
#     # for pick in new_picks:
#     #     arb_market = pick[market_idx]
#     #     if not re.search('Home Run', arb_market):
#     #         post_arbs.append(pick)


#     #send msg on slack app
#     print('Post: ' + str(post) + '\n\n')
#     if post:
#         # to avoid double msg, 
#         # only apply 1 channel per user
#         # OR do not repeat arbs
#         # BUT all will repeat all which are separated into channels
#         post_all = True # for testing all arbs before finalizing all category channels
#         if props_str != '' and post_all:
#             client.chat_postMessage(
#                 channel='all-arbs',
#                 text=props_str,
#                 username='Ball'
#             )

#         elif new_user_props_str != '':
#             client.chat_postMessage(
#                 channel='ball', # arbitrary name given to first channel
#                 text=props_str,
#                 username='Ball'
#             )


def write_ev_to_post(ev, client, send_mobile):
    print('\n===Write EV to Post===\n')
    #print('ev: ' + str(ev))

    props_str = ''

    
	# Need diff string for each channel:
    # 1. all
    # 2. home runs
    # 3. new user
		
    # for test_pick in test_picks:
    # 	print('\n' + str(test_pick))

    # all props str
    all_props_str = '' # advanced when limited need to find more exploits
    new_user_props_str = '' # changes constantly as user needs to blend in as normal
    #for ev_idx in range(len(evs)):
    #for ev_idx, ev in evs.items():
    #ev = evs[ev_idx]

    value = ev['value']
    #value_str = 'Value:\t' + value + '%'
    game = ev['game']
    #game_str = 'Game:\t' + game
    market = ev['market']
    #market_str = 'Market:\t' + market
    bet = ev['bet']

    source = ev['source'].title()
    # bet1_str = 'Bet 1:\t' + bet1
    odds = ev['odds']
    # odds1_str = 'Odds 1:\t' + odds1
    link = ev['link']

    # $x -> x
    # size_num = re.sub('\$','',ev['size'])
    # print('size_num', size_num)
    #size = '$' + str(converter.round_half_up(float(re.sub('\$','',ev['size']))))
    size = converter.round_ev_bet_size(ev)

    game_date = ev['game date']
    game_time = ev['game time']

    sport = ev['sport'].title()
    league = ev['league'].title()

    # Format Message
    # Top part 4 lines of msg shows in notification preview 
    # so show useful info to decide if need to see more
    # 1. which books to avoid limits
    # 2. market/prop to go to
    # 3. odds to double check
    # 4. value to see how important/valuable
    # props_str += bet1 + ', ' + bet2 + '\t\t\t\t'
    # props_str += game + '\t'
    # props_str += market + '\t|\t'
    # props_str += odds1 + ', ' + odds2 + '\t|\t'
    # props_str += value + '%' + '\t|\t'

    # props_str += '\n' + bet1 + ', ' + bet2 + '\t\n'
    # props_str += odds1 + ', ' + odds2 + ' - \n' # + '\t'#|\t'

    #ev_num = str(ev_idx + 1)
    props_str = '\n===EV===\n'
    props_str += '\n' + source + ' ' + odds + ' - \n\n'
    props_str += game + ' - \n\n'
    props_str += market + ', ' + bet + ' - \n\n'
    #props_str += bet + ' - \n\n'
    props_str += size + ' - \n\n'
    props_str += value + '%' + ' - \n\n'
    props_str += sport + ', ' + league + ' - \n\n'
    props_str += game_date + ', ' + game_time + ' - \n\n'
    props_str += link + '\n\n'

    #props_str += 'LINK:\n' + link + ' \n\n'
    

    # split player and market in given market field
    # so we can see market at the top and decide if we can take the bet or if limited or suspicious
    # player = ''
    # # need space bt dash so not compound name
    # if re.search(' - ', market):
    #     market_data = market.split(' - ')
    #     player = market_data[0].strip()
    #     market = market_data[1].strip()
    # #props_str += '\nBETS: ' + bet1 + ' ' + odds1 + ', ' + bet2 + ' ' + odds2 +'. \n\n'
    # props_str += '\nSOURCE: ' + source + ', ' + odds + ' \n\n'
    # if player != '':
    #     props_str += 'PLAYER: ' + player + ' \n\n'
    # props_str += 'MARKET: ' + market + ', ' + bet + ' \n\n'
    # props_str += 'GAME: ' + game + ' \n\n'
    # props_str += 'SIZE: ' + size + ' \n\n'

    #props_str += 'VALUE: ' + value + '% \n\n'
    #props_str += 'PROFIT: $' + profit + ' \n\n'

    


    props_str += '\n==================\n==================\n\n'

    # always add to all props str
    all_props_str += props_str
    # but selectively add to select channels
    if not re.search('Home Run', market):
        # add to new user str bc they avoid home runs
        new_user_props_str += props_str

    cur_time = datetime.today()
    timestamp = str(cur_time.hour) + ':' + str(cur_time.minute)
    print('\nTimestamp: ' + timestamp + '\n')
    print(all_props_str)
    #print(tabulate(arb_table))
    # print('New User Arbs')
    # print(new_user_props_str)

    # separate props into diff channels for specific types of users
    # 1 channel for all possible
    # 1 channel for new user avoiding home runs
    # 1 channel for limited users who can take home runs on specific apps
    # Do not post home runs to general channel bc only use on limited apps
    # post_arbs = []
    # for pick in new_picks:
    #     arb_market = pick[market_idx]
    #     if not re.search('Home Run', arb_market):
    #         post_arbs.append(pick)


    #send msg on slack app
    print('send_mobile: ' + str(send_mobile) + '\n\n')
    if send_mobile:
        # to avoid double msg, 
        # only apply 1 channel per user
        # OR do not repeat arbs
        # BUT all will repeat all which are separated into channels
        post_all = True # for testing all arbs before finalizing all category channels
        send_retries = 0
        max_retries = 3
        # while send_retries < max_retries:
        try:
            if all_props_str != '' and post_all:
                client.chat_postMessage(
                    channel='all-evs',
                    text=all_props_str,
                    username='Ball'
                )

            elif new_user_props_str != '':
                client.chat_postMessage(
                    channel='ball', # arbitrary name given to first channel
                    text=all_props_str,
                    username='Ball'
                )
        except Exception as e:
            print('\nERROR: Failed to Post Message to Slack!\n', e)
            # send_retries += 1
            # time.sleep(1)

def write_evs_to_post(evs, client, post=False):
    print('\n===Write EVs to Post===\n')
    print('evs: ' + str(evs))

    props_str = ''

    val_idx = 0
    game_idx = 1
    # skip game date idx
    market_idx = 3
    bet_idx = 4
    odds_idx = 5
    size_idx = 6
    link_idx = 7
    source_idx = 8

    
	# Need diff string for each channel:
    # 1. all
    # 2. home runs
    # 3. new user
		
    # for test_pick in test_picks:
    # 	print('\n' + str(test_pick))

    # all props str
    all_props_str = '' # advanced when limited need to find more exploits
    new_user_props_str = '' # changes constantly as user needs to blend in as normal
    #for ev_idx in range(len(evs)):
    for ev_idx, ev in evs.items():
        #ev = evs[ev_idx]

        value = ev['value']
        #value_str = 'Value:\t' + value + '%'
        game = ev['game']
        #game_str = 'Game:\t' + game
        market = ev['market']
        #market_str = 'Market:\t' + market
        bet = ev['bet']

        source = ev['source']
        # bet1_str = 'Bet 1:\t' + bet1
        odds = ev['odds']
        # odds1_str = 'Odds 1:\t' + odds1
        link = ev['link']

        size = ev['size']



        # Format Message
        # Top part 4 lines of msg shows in notification preview 
        # so show useful info to decide if need to see more
        # 1. which books to avoid limits
        # 2. market/prop to go to
        # 3. odds to double check
        # 4. value to see how important/valuable
        # props_str += bet1 + ', ' + bet2 + '\t\t\t\t'
        # props_str += game + '\t'
        # props_str += market + '\t|\t'
        # props_str += odds1 + ', ' + odds2 + '\t|\t'
        # props_str += value + '%' + '\t|\t'

        # props_str += '\n' + bet1 + ', ' + bet2 + '\t\n'
        # props_str += odds1 + ', ' + odds2 + ' - \n' # + '\t'#|\t'

        ev_num = str(ev_idx + 1)
        props_str = '\n===EV ' + ev_num + '===\n'
        props_str += '\n' + source + ' ' + odds + '. \n\n'
        props_str += game + ' - \n\n'
        props_str += market + ' - \n\n'
        props_str += bet + ' - \n\n'
        props_str += size + ' - \n\n'
        props_str += value + '%' + ' - \n\n'
        

        # split player and market in given market field
        # so we can see market at the top and decide if we can take the bet or if limited or suspicious
        player = ''
        # need space bt dash so not compound name
        if re.search(' - ', market):
            market_data = market.split(' - ')
            player = market_data[0].strip()
            market = market_data[1].strip()
        #props_str += '\nBETS: ' + bet1 + ' ' + odds1 + ', ' + bet2 + ' ' + odds2 +'. \n\n'
        props_str += '\nSOURCE: ' + source + ', ' + odds + ' \n\n'
        props_str += 'MARKET: ' + market + ', ' + bet + ' \n\n'
        props_str += 'GAME: ' + game + ' \n\n'
        if player != '':
            props_str += 'PLAYER: ' + player + ' \n\n'
        props_str += 'SIZE: ' + size + ' \n\n'
        props_str += 'VALUE: ' + value + '% \n\n'
        #props_str += 'PROFIT: $' + profit + ' \n\n'
        props_str += 'LINK:\n' + link + ' \n'


        props_str += '\n==================\n==================\n\n'

        # always add to all props str
        all_props_str += props_str
        # but selectively add to select channels
        if not re.search('Home Run', market):
            # add to new user str bc they avoid home runs
            new_user_props_str += props_str

    print('\n===All EVs===\n')
    print(all_props_str)
    #print(tabulate(arb_table))
    # print('New User Arbs')
    # print(new_user_props_str)

    # separate props into diff channels for specific types of users
    # 1 channel for all possible
    # 1 channel for new user avoiding home runs
    # 1 channel for limited users who can take home runs on specific apps
    # Do not post home runs to general channel bc only use on limited apps
    # post_arbs = []
    # for pick in new_picks:
    #     arb_market = pick[market_idx]
    #     if not re.search('Home Run', arb_market):
    #         post_arbs.append(pick)


    #send msg on slack app
    print('Post: ' + str(post) + '\n\n')
    if post:
        # to avoid double msg, 
        # only apply 1 channel per user
        # OR do not repeat arbs
        # BUT all will repeat all which are separated into channels
        post_all = True # for testing all arbs before finalizing all category channels
        if all_props_str != '' and post_all:
            client.chat_postMessage(
                channel='all-evs',
                text=all_props_str,
                username='Ball'
            )

        elif new_user_props_str != '':
            client.chat_postMessage(
                channel='ball', # arbitrary name given to first channel
                text=all_props_str,
                username='Ball'
            )


# write all arbs in 1 post
def write_arbs_to_post(arbs, client, post=False):
    print('\n===Write Arbs to Post===\n')
    print('arbs = {val:x, ...} = ' + str(arbs)) 

    props_str = ''

    val_idx = 0
    game_idx = 1
    market_idx = 2
    bet1_idx = 3
    bet2_idx = 4
    odds1_idx = 5
    odds2_idx = 6
    link1_idx = 7
    link2_idx = 8

    
	# Need diff string for each channel:
    # 1. all
    # 2. home runs
    # 3. new user
		
    # for test_pick in test_picks:
    # 	print('\n' + str(test_pick))

    # all props str
    all_props_str = '' # advanced when limited need to find more exploits
    new_user_props_str = '' # changes constantly as user needs to blend in as normal
    #for arb_idx in range(len(arbs)):
    for arb_idx, arb in arbs.items():
       #arb = arbs[arb_idx]

        value = arb['value']
        #value_str = 'Value:\t' + value + '%'
        game = arb['game']
        #game_str = 'Game:\t' + game
        market = arb['market']
        #market_str = 'Market:\t' + market

        bet1 = arb['bet1']
        # bet1_str = 'Bet 1:\t' + bet1
        bet2 = arb['bet2']
        # bet2_str = 'Bet 2:\t' + bet2
        odds1 = arb['odds1']
        # odds1_str = 'Odds 1:\t' + odds1
        odds2 = arb['odds2']
        # bet2_str = 'Bet 2:\t' + bet2
        link1 = arb['link1']
        link2 = arb['link2']
        source1 = arb['source1'].title()
        source2 = arb['source2'].title()

        
        # Make list of sizes depending on limit, from 1000 to 100, every 100
        size1_options = []
        size2_options = []
        max_limit = 1000
        # Better to make hedge bet rounder number bc seems more normal/rec
        size1 = converter.convert_odds_to_bet_size(odds1, odds2, max_limit)
        size1_str = '$' + str(size1)
        size2_str = '$' + str(max_limit)

        # compute payout, given odds and bet size
        # For positive American odds, divide the betting odds by 100 and multiply the result by the amount of your wager (Profit = odds/100 x wager). 
        # With negative odds, you divide 100 by the betting odds, then multiply that number by the wager amount (Profit = 100/odds x wager).
        # take positive side bc = both sides
        profit = str(converter.round_half_up(int(odds2) / 100 * max_limit) - size1)
        #print('profit: ' + profit)


        # Format Message
        # Top part 4 lines of msg shows in notification preview 
        # so show useful info to decide if need to see more
        # 1. which books to avoid limits
        # 2. market/prop to go to
        # 3. odds to double check
        # 4. value to see how important/valuable
        # props_str += bet1 + ', ' + bet2 + '\t\t\t\t'
        # props_str += game + '\t'
        # props_str += market + '\t|\t'
        # props_str += odds1 + ', ' + odds2 + '\t|\t'
        # props_str += value + '%' + '\t|\t'

        # props_str += '\n' + bet1 + ', ' + bet2 + '\t\n'
        # props_str += odds1 + ', ' + odds2 + ' - \n' # + '\t'#|\t'

        arb_num = str(arb_idx + 1)
        props_str = '\n===Arb ' + arb_num + '===\n'
        props_str += '\n' + source1 + ' ' + odds1 + ', ' + source2 + ' ' + odds2 +'. \n\n'
        props_str += game + ' - \n\n'
        props_str += market + ' - \n\n'
        props_str += bet1 + ', ' + bet2 + ' - \n\n'
        props_str += value + '%' + ' - \n\n'
        

        # split player and market in given market field
        # so we can see market at the top and decide if we can take the bet or if limited or suspicious
        player = ''
        if re.search('-', market):
            market_data = market.split(' - ')
            player = market_data[0].strip()
            market = market_data[1].strip()
        #props_str += '\nBETS: ' + bet1 + ' ' + odds1 + ', ' + bet2 + ' ' + odds2 +'. \n\n'
        props_str += '\nSOURCE 1: ' + source1 + ', ' + odds1 + ' \n'
        props_str += 'SOURCE 2: ' + source2 + ', ' + odds2 + ' \n\n'
        props_str += 'MARKET: ' + market + ' \n\n'
        props_str += 'BETS: ' + bet1 + ', ' + bet2 + ' \n\n'
        props_str += 'GAME: ' + game + ' \n\n'
        if player != '':
            props_str += 'PLAYER: ' + player + ' \n\n'
        props_str += 'VALUE: ' + value + '% \n\n'
        props_str += 'PROFIT: $' + profit + ' \n\n'
        props_str += 'LINK 1:\n' + link1 + ' \n'
        props_str += 'LINK 2:\n' + link2 + ' \n\n'
        

        # if Betrivers show range bc inaccurate reading
        # props_str += '\n' + value + '%\n'

        # props_str += '\n' + game + '\n'

        # props_str += '\n' + market + '\n'

        # Betrivers		Fanatics
        # -110			+110
        # $1200			$1000
        # -105			+110
        # $1250			$1000
        # props_str += '\n' + bet1 + '\t' + bet2

        # props_str += '\n' + odds1 + '\t' + odds2

        # props_str += '\n' + size1_str + '\t' + size2_str

        arb_table = [[source1, '', source2], [odds1, '', odds2], [size1_str, '', size2_str]]

        props_str += '\n' + tabulate(arb_table)

        props_str += '\n==================\n==================\n\n'

        # always add to all props str
        all_props_str += props_str
        # but selectively add to select channels
        if not re.search('Home Run', market):
            # add to new user str bc they avoid home runs
            new_user_props_str += props_str

    print('\n===All Arbs===\n')
    print(all_props_str)
    #print(tabulate(arb_table))
    # print('New User Arbs')
    # print(new_user_props_str)

    # separate props into diff channels for specific types of users
    # 1 channel for all possible
    # 1 channel for new user avoiding home runs
    # 1 channel for limited users who can take home runs on specific apps
    # Do not post home runs to general channel bc only use on limited apps
    # post_arbs = []
    # for pick in new_picks:
    #     arb_market = pick[market_idx]
    #     if not re.search('Home Run', arb_market):
    #         post_arbs.append(pick)


    #send msg on slack app
    print('Post: ' + str(post) + '\n\n')
    if post:
        # to avoid double msg, 
        # only apply 1 channel per user
        # OR do not repeat arbs
        # BUT all will repeat all which are separated into channels
        post_all = True # for testing all arbs before finalizing all category channels
        if all_props_str != '' and post_all:
            client.chat_postMessage(
                channel='all-arbs',
                text=props_str,
                username='Ball'
            )

        elif new_user_props_str != '':
            client.chat_postMessage(
                channel='ball', # arbitrary name given to first channel
                text=props_str,
                username='Ball'
            )
        
        
# write each arb in separate post
def write_all_arbs_to_post(arbs):

    for arb_idx in range(len(arbs)):
        arb = arbs[arb_idx]
        arb['id'] = arb_idx

        write_arb_to_post(arb)




def display_game_data(all_valid_streaks_list):
    #print("\n===Game Data===\n")
    # all_player_pre_dicts = [{'prediction':val,'overall record':[],..},{},..]
    # get headers
    # header_row = ['Prediction']
    # for pre_dict in all_player_pre_dicts.values():
    #     for key in pre_dict:
    #         header_row.append(key.title())
    #     break
    # game_data = [header_row]

    # print("all_player_pre_dicts: " + str(all_player_pre_dicts))
    # for prediction, pre_dict in all_player_pre_dicts.items():
    #     prediction_row = [prediction]
    #     for val in pre_dict.values():
    #         prediction_row.append(val)
    #     game_data.append(prediction_row)



    # get headers
    header_row = []
    header_string = '' # separate by semicolons and delimit in spreadsheet
    if len(all_valid_streaks_list) > 0:
        streak1 = all_valid_streaks_list[0]
        for key in streak1.keys():
            header_row.append(key.title())
            header_string += key.title() + ";"

        game_data = [header_row]
        game_data_strings = []
        for streak in all_valid_streaks_list:
            streak_row = []
            streak_string = ''
            for val in streak.values():
                streak_row.append(val)
                streak_string += str(val) + ";"
            game_data.append(streak_row)
            game_data_strings.append(streak_string)
    else:
        print('Warning: no valid streaks!')


    #print(tabulate(game_data))

    #print("Export")
    print(header_string)
    for game_data in game_data_strings:
        print(game_data)



def display_stat_plot(all_valid_streaks_list, all_players_stats_dicts, stat_of_interest, player_of_interest, season_year=2024):
    #print('\n===Plot Stats===\n')
    #Three lines to make our compiler able to draw:
    import matplotlib.pyplot as plt

    #display player stat values so we can see plot
    #columns: game num, stat val, over average record
    #print('all_players_stats_dicts: ' + str(all_players_stats_dicts))
    for valid_streak in all_valid_streaks_list:

        
        
        if re.search(stat_of_interest, valid_streak['prediction'].lower()) and re.search(player_of_interest, valid_streak['prediction'].lower()):

            #print('valid_streak: ' + str(valid_streak))
            player_name = ' '.join(valid_streak['prediction'].split()[:-2]).lower() # anthony davis 12+ pts
            #print("player_name from prediction: " + player_name)

            stat_name = valid_streak['prediction'].split()[-1].lower()
            condition = 'all'
            #season_year = 2023
            stat_vals_dict = all_players_stats_dicts[player_name][season_year][stat_name][condition]
            #print('stat_vals_dict: ' + str(stat_vals_dict))

            game_nums = list(stat_vals_dict.keys())
            #print('game_nums: ' + str(game_nums))
            stat_vals = list(stat_vals_dict.values())
            stat_vals.reverse()
            #print('stat_vals: ' + str(stat_vals))

            stat_line = int(valid_streak['prediction'].split()[-2][:-1])
            #print('stat_line: ' + str(stat_line))

            plot_stat_line = [stat_line] * len(game_nums)
            #print('plot_stat_line: ' + str(plot_stat_line))

            # x = np.array(game_nums)
            # y = np.array(stat_vals)

            plt.plot(game_nums, stat_vals, label = "Stat Vals") # reverse bc input from recent to distant but we plot left to right
            plt.plot(game_nums, plot_stat_line,  label = "Stat Line")

            # also plot avg over time to compare trend of avg
            # bc just seeing season avg is barely useful almost useless unless we see either avg in last few games (and multiple subset) or we can simply see if avg is increasing or decreasing
            # the avg for the first game must be based on previous seasons
            # but for now arbitrary number
            #init_mean_stat_val
            prev_stat_vals = []
            mean_stat_vals = [] # how mean changes over time
            past_ten_stat_vals = []
            past_ten_mean_stat_vals = [] # mean over last 10 games to get more recent relevant picture
            past_three_stat_vals = []
            past_three_mean_stat_vals = []
            for stat_val_idx in range(len(stat_vals)):
                stat_val = stat_vals[stat_val_idx]
                #print('prev_stat_vals: ' + str(prev_stat_vals))
                #print('past_ten_stat_vals: ' + str(past_ten_stat_vals))
                # compute avg of this and previous vals
                if stat_val_idx == 0:
                    mean_stat_val = stat_val
                    past_ten_mean_stat_val = stat_val
                    past_three_mean_stat_val = stat_val

                else:
                    mean_stat_val = converter.round_half_up(np.mean(np.array(prev_stat_vals)), 1)
                    #print('mean_stat_val: ' + str(mean_stat_val))
                    past_ten_mean_stat_val = converter.round_half_up(np.mean(np.array(past_ten_stat_vals)), 1)
                    #print('past_ten_mean_stat_val: ' + str(past_ten_mean_stat_val))
                    past_three_mean_stat_val = converter.round_half_up(np.mean(np.array(past_three_stat_vals)), 1)
                    #print('past_three_mean_stat_val: ' + str(past_three_mean_stat_val))

                mean_stat_vals.append(mean_stat_val)
                past_ten_mean_stat_vals.append(past_ten_mean_stat_val)
                past_three_mean_stat_vals.append(past_three_mean_stat_val)

                prev_stat_vals.append(stat_val)

                if stat_val_idx < 10: # add vals to list until we reach 10 bc we only want past 10 games
                    past_ten_stat_vals.append(stat_val)
                else: # replace in list instead of adding
                    past_ten_stat_vals.pop(0)
                    past_ten_stat_vals.append(stat_val)
                if stat_val_idx < 3: # add vals to list until we reach 10 bc we only want past 10 games
                    past_three_stat_vals.append(stat_val)
                else: # replace in list instead of adding
                    past_three_stat_vals.pop(0)
                    past_three_stat_vals.append(stat_val)
                

            #print('mean_stat_vals: ' + str(mean_stat_vals))
            #print('past_ten_mean_stat_vals: ' + str(past_ten_mean_stat_vals))
            #print('past_three_mean_stat_vals: ' + str(past_three_mean_stat_vals))

            plt.plot(game_nums, mean_stat_vals,  label = "Overall Mean")
            plt.plot(game_nums, past_ten_mean_stat_vals,  label = "Past 10 Mean")
            plt.plot(game_nums, past_three_mean_stat_vals,  label = "Past 3 Mean")


            plt.title(player_name.title() + " " + stat_name.upper() + " over Time")
            plt.xlabel("Game Num")
            plt.ylabel(stat_name.upper())

            plt.legend()
            plt.show()

            # display table so we can export to files and view graphs in spreadsheet

            #Two  lines to make our compiler able to draw:
            # plt.savefig(sys.stdout.buffer)
            # sys.stdout.flush()


def display_all_players_records_dicts(all_players_records_dicts, all_players_season_logs):
    #print('\n===Display All Players Records Dicts===\n')

    # player_stat_dict = { year: .. }
    for player_name, player_stat_dict in all_players_stats_dicts.items():
    #for player_idx in range(len(all_player_game_logs)):

        #print('\n===' + player_name.title() + '===\n')

        #season_year = 2023

        # player_season_stat_dict = { stat name: .. }
        for season_year, player_season_stat_dict in player_stat_dict.items():

            #print("\n===Year " + str(season_year) + "===\n")
            #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
            #player_name = player_names[player_idx] # player names must be aligned with player game logs

            # all_pts_dicts = {'all':{idx:val,..},..}
            all_pts_dicts = player_season_stat_dict['pts']
            all_rebs_dicts = player_season_stat_dict['reb']
            all_asts_dicts = player_season_stat_dict['ast']
            all_threes_made_dicts = player_season_stat_dict['3pm']
            all_bs_dicts = player_season_stat_dict['blk']
            all_ss_dicts = player_season_stat_dict['stl']
            all_tos_dicts = player_season_stat_dict['to']
            if len(all_pts_dicts['all'].keys()) > 0:
                # no matter how we get data, 
                # next we compute relevant results

                # first for all then for subsets like home/away
                # all_pts_dict = { 'all':[] }
                # all_pts_means_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_medians_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_modes_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_min_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_max_dict = { 'all':0, 'home':0, 'away':0 }

                all_stats_counts_dict = { 'all': [], 'home': [], 'away': [] }

                # at this point we have added all keys to dict eg all_pts_dict = {'1of2':[],'2of2':[]}
                #print("all_pts_dict: " + str(all_pts_dict))
                #print("all_pts_dicts: " + str(all_pts_dicts))
                # all_pts_dicts = {'all':{1:20}}
                # key=condition, val={idx:stat}

                
                #compute stats from data
                # key represents set of conditions of interest eg home/away
                for conditions in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

                    # reset for each set of conditions

                    # for same set of conditions, count streaks for stats
                    min_line_hits = 7
                    game_sample = 10
                    current_line_hits = 10 # player reached 0+ stats in all 10/10 games. current hits is for current level of points line

                    pts_count = 0
                    r_count = 0
                    a_count = 0

                    threes_count = 0
                    b_count = 0
                    s_count = 0
                    to_count = 0

                    all_pts_counts = []
                    all_rebs_counts = []
                    all_asts_counts = []

                    all_threes_counts = []
                    all_blks_counts = []
                    all_stls_counts = []
                    all_tos_counts = []

                    # prob = 1.0
                    # while(prob > 0.7):
                    #if set_sample_size = True: # if we set a sample size only consider those settings. else take all games
                    #while(current_line_hits > min_line_hits) # min line hits is considered good odds. increase current line hits count out of 10
                        # if count after 10 games is greater than min line hits then check next level up
                    for game_idx in range(len(all_pts_dicts[conditions].values())):
                        pts = list(all_pts_dicts[conditions].values())[game_idx]
                        rebs = list(all_rebs_dicts[conditions].values())[game_idx]
                        asts = list(all_asts_dicts[conditions].values())[game_idx]

                        threes = list(all_threes_made_dicts[conditions].values())[game_idx]
                        blks = list(all_bs_dicts[conditions].values())[game_idx]
                        stls = list(all_ss_dicts[conditions].values())[game_idx]
                        tos = list(all_tos_dicts[conditions].values())[game_idx]

                        player_projected_lines = projected_lines_dict[player_name]
                        if pts >= int(player_projected_lines['PTS']):
                            pts_count += 1
                        if rebs >= int(player_projected_lines['REB']):
                            r_count += 1
                        if asts >= int(player_projected_lines['AST']):
                            a_count += 1

                        if threes >= int(player_projected_lines['3PT']):
                            threes_count += 1
                        if blks >= int(player_projected_lines['BLK']):
                            b_count += 1
                        if stls >= int(player_projected_lines['STL']):
                            s_count += 1
                        if tos >= int(player_projected_lines['TO']):
                            to_count += 1

                        all_pts_counts.append(pts_count)
                        all_rebs_counts.append(r_count)
                        all_asts_counts.append(a_count)

                        all_threes_counts.append(threes_count)
                        all_blks_counts.append(b_count)
                        all_stls_counts.append(s_count)
                        all_tos_counts.append(to_count)

                    # make stats counts to find consistent streaks
                    all_stats_counts_dict[conditions] = [ all_pts_counts, all_rebs_counts, all_asts_counts, all_threes_counts, all_blks_counts, all_stls_counts, all_tos_counts ]

                    stats_counts = [ all_pts_counts, all_rebs_counts, all_asts_counts, all_threes_counts, all_blks_counts, all_stls_counts, all_tos_counts ]

                    header_row = ['Games']
                    over_pts_line = 'PTS ' + str(player_projected_lines['PTS']) + "+"
                    over_rebs_line = 'REB ' + str(player_projected_lines['REB']) + "+"
                    over_asts_line = 'AST ' + str(player_projected_lines['AST']) + "+"
                    
                    over_threes_line = '3PM ' + str(player_projected_lines['3PT']) + "+"
                    over_blks_line = 'BLK ' + str(player_projected_lines['BLK']) + "+"
                    over_stls_line = 'STL ' + str(player_projected_lines['STL']) + "+"
                    over_tos_line = 'TO ' + str(player_projected_lines['TO']) + "+"
                    
                    prob_pts_row = [over_pts_line]
                    prob_rebs_row = [over_rebs_line]
                    prob_asts_row = [over_asts_line]

                    prob_threes_row = [over_threes_line]
                    prob_blks_row = [over_blks_line]
                    prob_stls_row = [over_stls_line]
                    prob_tos_row = [over_tos_line]

                    

                    for game_idx in range(len(all_pts_dicts[conditions].values())):
                        p_count = all_pts_counts[game_idx]
                        r_count = all_rebs_counts[game_idx]
                        a_count = all_asts_counts[game_idx]

                        threes_count = all_threes_counts[game_idx]
                        b_count = all_blks_counts[game_idx]
                        s_count = all_stls_counts[game_idx]
                        to_count = all_tos_counts[game_idx]

                        current_total = str(game_idx + 1)
                        current_total_games = current_total# + ' Games'
                        header_row.append(current_total_games)

                        prob_over_pts_line = str(p_count) + "/" + current_total
                        prob_pts_row.append(prob_over_pts_line)
                        
                        prob_over_rebs_line = str(r_count) + "/" + current_total
                        prob_rebs_row.append(prob_over_rebs_line)
                        prob_over_asts_line = str(a_count) + "/" + current_total
                        prob_asts_row.append(prob_over_asts_line)

                        prob_over_threes_line = str(threes_count) + "/" + current_total
                        prob_threes_row.append(prob_over_threes_line)
                        prob_over_blks_line = str(b_count) + "/" + current_total
                        prob_blks_row.append(prob_over_blks_line)
                        prob_over_stls_line = str(s_count) + "/" + current_total
                        prob_stls_row.append(prob_over_stls_line)
                        prob_over_tos_line = str(to_count) + "/" + current_total
                        prob_tos_row.append(prob_over_tos_line)

                    # display game info for reference based on game idx
                    game_num_header = 'Games Ago'
                    game_num_row = [game_num_header]
                    game_day_header = 'DoW'
                    game_day_row = [game_day_header]
                    game_date_header = 'Date'
                    game_date_row = [game_date_header]

                    for game_num in all_pts_dicts[conditions].keys():
                        #game_num = all_pts_dicts[key]
                        game_num_row.append(game_num)
                        game_day_date = player_game_log.loc[game_num,'Date']
                        game_day = game_day_date.split()[0]
                        game_day_row.append(game_day)
                        game_date = game_day_date.split()[1]
                        game_date_row.append(game_date)
                    

                    #total = str(len(all_pts))
                    #probability_over_line = str(count) + "/" + total
                    #total_games = total + " Games"
                    #header_row = ['Points', total_games]
                    #print(probability_over_line)

                    #prob_row = [over_line, probability_over_line]

                    #print("\n===" + player_name.title() + " Probabilities===\n")

                    game_num_table = [game_num_row, game_day_row, game_date_row]
                    print(tabulate(game_num_table))

                    prob_pts_table = [prob_pts_row]
                    print(tabulate(prob_pts_table))

                    prob_rebs_table = [prob_rebs_row]
                    print(tabulate(prob_rebs_table))

                    prob_asts_table = [prob_asts_row]
                    print(tabulate(prob_asts_table))

                    prob_threes_table = [prob_threes_row]
                    print(tabulate(prob_threes_table))

                    prob_blks_table = [prob_blks_row]
                    print(tabulate(prob_blks_table))

                    prob_stls_table = [prob_stls_row]
                    print(tabulate(prob_stls_table))

                    prob_tos_table = [prob_tos_row]
                    print(tabulate(prob_tos_table))

            season_year -= 1

# players_outcomes = {player: stat name: outcome dict}
def display_players_outcomes(players_outcomes):
    #print("\n===Player Outcomes===\n")
    #print('players_outcomes: ' + str(players_outcomes))

    # sort so we see all instances of teammates out grouped together instead of game order bc we are interested to see by type of condition not by game at this point
    # we do want to see ordered by games as well so we have game idx and need way to switch bt views
    
    #todo: sorted_players_outcomes = sorter.sort_players_outcomes(players_outcomes) 


    # convert player outcomes dict into list
    player_outcomes_list = []
    # stat_outcome_dict = stat:outcome_dict
    for stat_outcome_dict in players_outcomes.values():

        for season_part_outcome_dict in stat_outcome_dict.values():

            for outcome_dict in season_part_outcome_dict.values():

                player_outcomes_list.append(outcome_dict) # outcome_dict = prediction:stats

    # get headers
    header_row = []
    header_string = '' # separate by semicolons and delimit in spreadsheet
    if len(player_outcomes_list) > 0:
        # print header row
        outcome1 = player_outcomes_list[0]
        for key in outcome1.keys():
            header_row.append(key.title())
            header_string += key.title() + ";"

        # print data rows
        game_data = [header_row]
        game_data_strings = []
        for outcome in player_outcomes_list:
            outcome_row = []
            outcome_string = ''
            for val in outcome.values():
                outcome_row.append(val)
                outcome_string += str(val) + ";"
            game_data.append(outcome_row)
            game_data_strings.append(outcome_string)
    else:
        print('Warning: no valid streaks!')


    #print(tabulate(game_data))

    #print("Export")
    print(header_string)
    for game_data in game_data_strings:
        print(game_data)

    #print("\n===End Player Outcomes===\n")


# we have saved lessons from experience and logic that must be accounted for when deciding so display prominently and constantly reference
# lessons = [outcome, lesson]
def display_lessons(lessons):
    #print("\n===Display Lessons===\n")

    header_string = 'Outcome;Lesson'

    lesson_strings = []
    for lesson in lessons:
        lesson_string = lesson[0] + ';' + lesson[1]
        lesson_strings.append(lesson_string)

    #print("Export")
    print(header_string)
    for lesson in lesson_strings:
        print(lesson)

    #print("\n===End Lessons===\n")


# data = [[name,id],..]
# for espn id we only want to append new ids bc they do not change
# write_param = create (error if exists), overwrite, or append
def write_data_to_file(data, filepath, write_param='w', extension=''):
    #print('\n===Write Data to File: ' + filepath + '===\n')

    if extension == '':
        extension = filepath.split('.')[1]

    if extension == 'csv':

        with open(filepath, write_param) as csvfile:

            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(data)

    elif extension == 'json':
        with open(filepath, write_param) as outfile:
            json.dump(dict, outfile)

    elif extension == 'txt':
        f = open(filepath, write_param)
        f.write(data)
        f.close()

    else:
        print('Warning: Unknown file extension! ')
    
def write_json_to_file(dict, filepath, write_param='w+'):
    #print('\n===Write JSON to File: ' + filepath + '===\n')
    # filepath = data/game logs/cur/...

    # see if dir exists and make new if not
    # path_data = filepath.split('/')[:-1]
    # folder_path = ''
    # for folder in path_data:
    #     folder_path += folder
    #     if not os.path.exists(folder_path):
    #         os.mkdir(folder_path)


    try:

    #filepath = re.sub('\s+','-',filepath) # is this needed or are spaces ok?
        with open(filepath, write_param) as outfile:
            json.dump(dict, outfile)

    except Exception as e:
        print('e: ' + str(e))
        if str(e) == 'FileNotFoundError':
            #if not os.path.isfile(filepath):
            gpath = 'content/gdrive/My Drive/' + filepath
            open(gpath, 'x')

            with open(gpath, write_param) as outfile:
                json.dump(dict, outfile)

# data = [[name,id],..]
# for espn id we only want to append new ids bc they do not change
# def append_data_to_file(data, filepath):

#     print('\n===Write Data to File===\n')


# init record condition_record format ['1/1',..]
# desired format 1/1,..
# remove brackets and quotes
def convert_list_to_string(init_list):
    #print('init_list: ' + str(init_list))

    final_string = re.sub('[\\[\\]\']','',str(init_list))

    #print('final_string: ' + final_string)
    return final_string


# moved to generator
# all_player_consistent_stats = {} same format as stat records, 


#desired_order=list  headers
def list_dicts(dicts, desired_order=[], separator=',', output=''):
    #print('\n===List Dicts===\n')

    # desired_order = ['player name','stat name','ok val','ok pp','ok p']
    dict_list = converter.convert_dicts_to_lists(dicts, desired_order)

    # we cannot see clearly in tabulate format for big data
    #print('dict_list')
    #print(tabulate(dict_list))

    headers = []#[list(dicts[0].keys())]
    for key in desired_order:
        headers.append(key)
    if len(dicts) > 0:
        for key in dicts[0].keys():
            if key not in desired_order:
                headers.append(key)


    dict_list = [headers] + dict_list

    # export
    # to semicolon separated value
    # or csv bc semicolon only needed if comma used in cell
    for row in dict_list:
        export_row = ''
        for cell in row:
            # stop Sheets autoformatting 3pm as 3:00 PM
            # by adding apostrophe to the front
            #print('cell: ' + str(cell))
            if str(cell) == '3pm':
                cell = '\'3pm'
            export_row += str(cell) + separator

        print(export_row)

    if output == 'excel':
        data_key = 'stat probs' # folder and data type
        book_name = 'data/' + data_key + '/' + 'all ' + data_key + '.xlsx'
        print('book_name: ' + str(book_name))
        writer = pd.ExcelWriter(book_name)

        stat_probs_df = pd.DataFrame(dict_list)
        #print('stat_probs_df: ' + str(stat_probs_df))
        stat_probs_df.to_excel(writer)
        writer.close()

# one page for each stat showing all conditions
# all_player_stat_probs = {condition:year:part:stat:val} = {'all': {2023: {'regular': {'pts': {'0': { 'prob over': po, 'prob under': pu },...
# stat_probs_by_stat = {stat:val:condition:year:part} = {'pts':{'0':{'all':{2023:{'regular':{po,pu}}
def write_all_stat_probs_by_stat(all_player_stat_probs):
    #print('\n===Write All Player Stat Probs by Stat===\n')

    for player, player_stat_probs in all_player_stat_probs.items():
        stat_probs_by_stat = {} # this must be in player loop or it will show max val for all players when we only need max for current players here bc separate sheets. this would be outside loop for all players when we want all players in same sheet
        #print('player: ' + str(player))
        if len(player_stat_probs.keys()) > 0:
            data_key = 'stat probs' # folder and data type
            organized_by = 'stat' # input key desired by user
            book_name = 'data/' + data_key + '/' + player + ' ' + data_key + ' - ' + organized_by + '.xlsx'
            #print('book_name: ' + str(book_name))
            writer = pd.ExcelWriter(book_name)

            headers = ['val']
            all_conditions = []
            for condition, condition_stat_probs in player_stat_probs.items():
                #print('condition: ' + str(condition))
                for year, year_stat_probs in condition_stat_probs.items():
                    #print('year: ' + str(year))
                    for part, part_stat_probs in year_stat_probs.items():
                        #print('part: ' + str(part))
                        conditions = condition + ' ' + str(year) + ' ' + part + ' prob'
                        all_conditions.append(conditions)
                        headers.extend([conditions + ' over', conditions + ' under'])
                        for stat, stat_probs in part_stat_probs.items():
                            
                            for val, probs_dict in stat_probs.items():
                                
                                if stat not in stat_probs_by_stat.keys():
                                    stat_probs_by_stat[stat] = {}
                                    stat_probs_by_stat[stat][val] = {}
                                elif val not in stat_probs_by_stat[stat].keys():
                                    stat_probs_by_stat[stat][val] = {}

                                stat_probs_by_stat[stat][val][conditions] = probs_dict


            # player_stat_probs_dict: {0: {'pts': {'prob over': 1.0, 'prob under': 0.0}, 'reb': {
            # stat_probs_by_stat = {stat:val:conditions} = {'pts':{'0'{'all':{2023:{'regular':{po,pu}}
            #print('stat_probs_by_stat: ' + str(stat_probs_by_stat))
            #print('headers: ' + str(headers))
            for stat, stat_prob_dict in stat_probs_by_stat.items():
                stat_probs_table = []
                sheet_name = stat
                #print('\nsheet_name: ' + str(sheet_name))
                #print('stat_prob_dict: ' + str(stat_prob_dict))
                for val, val_probs_dict in stat_prob_dict.items():
                    #print('val: ' + str(val))
                    #print('val_probs_dict: ' + str(val_probs_dict)) # conditions: {po:po, pu:pu}
                    stat_probs_row = [val]

                    #for conditions, conditions_probs_dict in val_probs_dict.items():  

                    for conditions in all_conditions:
                        #print('conditions: ' + str(conditions))
                        p_o = 0
                        p_u = 100
                        if conditions in val_probs_dict.keys():
                            stat_prob = val_probs_dict[conditions]
                            p_o = converter.round_half_up(stat_prob*100)
                            p_u = 100 - p_o #converter.round_half_up(stat_probs_dict['prob under']*100)
                        stat_probs_row.extend([p_o, p_u])

                    #print('stat_probs_row: ' + str(stat_probs_row))
                    stat_probs_table.append(stat_probs_row)

                #print('stat_probs_table: ' + str(stat_probs_table))
                stat_probs_df = pd.DataFrame(stat_probs_table, columns=headers)
                #print('stat_probs_df: ' + str(stat_probs_df))
                stat_probs_df.to_excel(writer,sheet_name)

            writer.close()

# each player gets a table separate sheet 
# showing over and under probs for each stat val
# val, prob over, prob under
# 0, P_o0, P_u0
# all_player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': { 'prob over': po, 'prob under': pu },...
# switch stat,val to val,stat to get
# player_stat_probs_dict: {0: {'pts': {'prob over': 1.0, 'prob under': 0.0}, 'reb': {
def write_all_player_stat_probs(all_player_stat_probs):
    #print('\n===Write All Player Stat Probs===\n')

    headers = ['val', 'pts prob over', 'pts prob under', 'reb prob over', 'reb prob under', 'ast prob over', 'ast prob under', '3pm prob over', '3pm prob under']

    # first arrange with all different stats in same sheet for each set of conditions
    # then arrange with same stat under all different conditions for each stat
    # this is a common method of rearranging dictionary levels for the purposes of
    # displaying in different forms and perspectives
    # see also generate_all_consistent_stat_dicts()
    # so make a fcn called rearrange dict, which takes desired output levels
    # and rearranges available keys in that order
    # so here it would be param=desired output order=[condition,year,part,val,stat]
    # where we only swap val and stat bc 1 val per row used as index which has multiple different stats in the same row
    # but those headers arent actually in the dict so we need to know the level nums of the init dict, 
    # and also input the desired output indexes
    # until we make that fcn for now we will make a temp dict with altered levels
    # and loop thru that to create rows after populating
    # so first loop makes temp dict rearranged in desired order
    # and second loop displays rows in desired order and format (however temp dict is arranged)
    # this is like creating a vector by aligning data points/features
    # each player gets its own book
    
    for player, player_stat_probs in all_player_stat_probs.items():
        #print('player: ' + str(player))
        #print('player_stat_probs: ' + str(player_stat_probs))
        if len(player_stat_probs.keys()) > 0:
            data_key = 'stat probs' # folder and data type

            organized_by = 'condition' # input key desired by user
            book_name = 'data/' + data_key + '/' + player + ' ' + data_key + ' - ' + organized_by + '.xlsx'
            #print('book_name: ' + str(book_name))
            writer = pd.ExcelWriter(book_name)
            #stat_probs_table = []
            for condition, condition_stat_probs in player_stat_probs.items():
                #print('condition: ' + str(condition))
                for year, year_stat_probs in condition_stat_probs.items():
                    #print('year: ' + str(year))
                    for part, part_stat_probs in year_stat_probs.items():
                        #print('part: ' + str(part))
                        sheet_name = condition + ' ' + str(year) + ' ' + part
                        #print('sheet_name: ' + str(sheet_name))

                        # rearrange all_player_stat_probs in desired order of columns (x,y)
                        # here we have x,y=stat,val
                        # output in player_stat_probs_dict
                        
                        player_stat_probs_dict = {}
                        for stat, stat_probs in part_stat_probs.items():
                            for val, probs_dict in stat_probs.items():
                                # only put val for first stat pts bc all stats share a row
                                # if stat == 'pts':
                                #     stat_probs_row = [val]
                                # p_o = probs_dict['prob over']
                                # p_u = probs_dict['prob under']
                                # stat_probs_row.extend([p_o, p_u])

                                if val not in player_stat_probs_dict.keys():
                                    player_stat_probs_dict[val] = {}
                                player_stat_probs_dict[val][stat] = probs_dict
                        # player_stat_probs_dict: {0: {'pts': {'prob over': 1.0, 'prob under': 0.0}, 'reb': {
                        #print('player_stat_probs_dict: ' + str(player_stat_probs_dict))
                        # need to fill blank cells with 0s or 100s to keep order alignment
                        # max_val = list(player_stat_probs_dict.keys())[-1] # last key is always max bc placed in order
                        # max_val = 0
                        # for val, val_probs_dict in player_stat_probs_dict.items():
                        #     max_stat_val = list(player_stat_probs_dict.keys())[-1] # last key is always max bc placed in order
                        #     print('max_stat_val: ' + str(max_stat_val))
                        #     if max_stat_val > max_val:
                        #         max_val = max_stat_val
                        # print('max_val: ' + str(max_val))

                        # stat probs by condition bc each condition gets a page showing all stats for that condition
                        stat_probs_table = []
                        #all_stat_keys = []
                        if 0 in player_stat_probs_dict.keys():
                            all_stat_keys = list(player_stat_probs_dict[0].keys()) # we need to get all stat keys from first dict so we know if player missed val for that stat
                        
                            for val, val_probs_dict in player_stat_probs_dict.items():
                                #val_idx = 0
                                stat_probs_row = [val]
                                for stat in all_stat_keys:
                                    p_o = 0
                                    p_u = 100
                                    if stat in val_probs_dict.keys():
                                        stat_prob = val_probs_dict[stat]
                                #for stat, stat_probs_dict in val_probs_dict.items():
                                        p_o = converter.round_half_up(stat_prob*100)
                                        p_u = 100 - p_o #converter.round_half_up(stat_probs_dict['prob under']*100)
                                    stat_probs_row.extend([p_o, p_u])

                                stat_probs_table.append(stat_probs_row)

                                #val_idx += 1

                            stat_probs_df = pd.DataFrame(stat_probs_table, columns=headers)
                            stat_probs_df.to_excel(writer,sheet_name)

                        
            writer.close()

    #write_all_stat_probs_by_condition(all_player_stat_probs)
    write_all_stat_probs_by_stat(all_player_stat_probs)


# write 1 sheet for all +ev props, sorted by true prob
# AND write 1 sheet for all 0 ev props, sorted by true prob
# AND write 1 sheet for all -ev props, sorted by true prob
# AND write 1 sheet for each strategy
def write_prop_tables(prop_dicts, sheet_names, desired_order, joint_sheet_name='Joints', rare_sheet_name='Rare', todays_date=datetime.today().strftime('%m-%d-%y')):
    print('\n===Write Prop Tables===\n')
    #print('prop_dicts: ' + str(prop_dicts))
    # print('sheet_names: ' + str(sheet_names))
    # print('desired_order: ' + str(desired_order))

    

    # book name = prop tables
    book_name = 'data/prop tables - ' + todays_date + '.xlsx'
    print('book_name: ' + str(book_name))
    writer = pd.ExcelWriter(book_name)#, font_size=20)

    # Set the wrap text format for all cells in the workbook.
    #writer.book.formats[0].set_text_wrap(True)
    workbook = writer.book
    wrap_format = workbook.add_format({'text_wrap': True, 'font_size':14})
    ratio_format = workbook.add_format({"num_format": "0.##", 'text_wrap': True, 'font_size':14})
    #font_format = workbook.add_format({'font_name': 'Arial', 'font_size': 14})
    #dictionary for map position of selected columns to excel headers
    #d = dict(zip(range(26), list(string.ascii_uppercase)))
    #print('d: ' + str(d))

    init_desired_order = desired_order
    for table_idx in range(len(prop_dicts)):
        table_dicts = prop_dicts[table_idx]

        sheet_name = sheet_names[table_idx]

        if sheet_name == joint_sheet_name:
            desired_order = ['joint', 'min risk', 'max picks top ev', 'max picks top prob']
        elif sheet_name == rare_sheet_name:
            desired_order = ['Game', 'Name', 'Stat', 'Norm', 'Prev', 'Cnt', 'Prob', 'Total']
        else:
            desired_order = init_desired_order

        #desired_order = [x.title() for x in desired_order]
        table_df = pd.DataFrame(table_dicts, columns=desired_order)
        #print('table_dicts: ' + str(table_dicts))
        #print('table_df: ' + str(table_df))
        table_df.columns = [x.title() for x in table_df.columns]
        table_df = table_df.applymap(lambda x: str(x).title())
        # title player names
        # if len(table_dicts) > 0 and 'player' in table_dicts[0].keys():
        #     #player_str = str(table_df['Player'])
        #     #print('table_df[Player]: ' + str(table_df['Player']))
        #     player_val = table_df.player
        #     if isinstance(player_val, str):
        #         table_df[0] = player_val.str.title() 
            # else:
            #     print('Warning: player val not string! ' + str(player_val))

        
        table_df.to_excel(writer,sheet_name, index=False)#, format=font_format)#, font={'name': 'Arial', 'size': 12})

        worksheet = writer.sheets[sheet_name]

        # wrap_format = worksheet.add_format({'text_wrap': True, 'font_size':14})
        # ratio_format = worksheet.add_format({"num_format": "0.##", 'text_wrap': True, 'font_size':14})

        #worksheet.set_column('A:AZ', None, wrap_format)


        # for column in table_df.columns.get_indexer(desired_order):
        #     print('column: ' + str(column))
        #     excel_header = d[column] + ':' + d[column]
        #     print('excel_header: ' + str(excel_header))
        #     worksheet.set_column(excel_header, None, wrap_format) #, cell_format=writer.book.add_format({'text_wrap': True})) #wrap_text=True)

        #worksheet.set_font(14)

        # set odds ratio column J format number 2 decimal places

        
        # set column width
        # some columns are small so fit to data
        # large columns get max width!
        # worksheet = writer.sheets[sheet_name]
        for idx, col in enumerate(table_df):
            series = table_df[col]
            # default font is 11 but ideal font is 14 so adjust
            max_len = max((series.astype(str).map(len).max() + 5, # len of largest item
                           len(str(series.name)) # len of column name/header
                           )) + 1 # adding a little extra space
            # limit width for readability
            # cannot see former team col full screen at 50
            max_len = min(max_len, 45)
            
            # if odds ratio col, set number format
            cell_format = wrap_format
            if idx == 9:
                cell_format = ratio_format
                max_len = len(str(series.name)) + 1 # header longer than number
                
            #worksheet.set_column(idx, idx, max_len)
            worksheet.set_column(idx, idx, max_len, cell_format)

        # needs another library
        # table_df = table_df.style.set_properties(**{
        #     'font-size': '20pt',
        # })

        worksheet.freeze_panes(1, 5)
        # set zoom does not work in google sheets
        #worksheet.set_zoom(115)


    writer.close()

    # delete prev game prop table bc already backed up
    remover.delete_file('prop tables', todays_date)
    

# divide logs/data (eg player game logs) into cur yr and prev yrs
# init and final dicts combine cur and prev yrs
# so here we separate to write cur and prev separately
# bc prev stays same while cur changes each new game
# need cur_yr bc only cur yr changes
# data_type is folder to find preexisting file to delete
def write_cur_and_prev(init_dict, final_dict, cur_file, prev_file, cur_yr, subject_name='', todays_date='', data_type=''):
    # print('\n===Write Cur and Prev===\n')
    # print('cur_yr: ' + str(cur_yr))
    # cur file = player_cur_season_log_filename = 'data/game logs/' + player_name + ' ' + current_year_str + ' game log ' + todays_date + '.json'

    # print('init_dict: ' + str(init_dict))
    # print('final_dict: ' + str(final_dict))
    # print('cur_file: ' + str(cur_file))
    # print('prev_file: ' + str(prev_file) + '\n')
    
    # take first year as cur yr
    init_cur_dict = {} #list(init_dict.values)[0]
    init_prev_dict = {}
    final_cur_dict = {} #list(final_dict.values)[0]
    final_prev_dict = {}
    
    # if init dict does not have cur yr then init cur dict = {}
    # if cur_yr in init_dict.keys():
    #     init_cur_dict = init_dict[cur_yr]
    # if cur_yr in final_dict.keys():
    #     final_cur_dict = final_dict[cur_yr]

    #year_idx = 0
    for year, year_dict in init_dict.items():
        
        if year == cur_yr:
            init_cur_dict = year_dict

        else:
            init_prev_dict[year] = year_dict

        #year_idx += 1

    #year_idx = 0
    for year, year_dict in final_dict.items():
        
        if year == cur_yr:
            final_cur_dict = year_dict

        else:
            final_prev_dict[year] = year_dict

        #year_idx += 1

    #print('init_cur_dict: ' + str(init_cur_dict))
    #print('final_cur_dict: ' + str(final_cur_dict))
    #print('init_prev_dict: ' + str(init_prev_dict))
    #print('final_prev_dict: ' + str(final_prev_dict))
    if not init_cur_dict == final_cur_dict:
        #print(subject_name + ' CURRENT year data changed so write to file')
        write_json_to_file(final_cur_dict, cur_file)

        # delete prev day cur file bc replaced by cur day
        #yesterday = 
        #yesterday_file = prev_day_cur_file = 'data/game logs/' + player_name + ' ' + current_year_str + ' game log ' + todays_date + '.json'
        #pathlib.Path(path).is_file():
        # determine if existing file in folder has player name
        if data_type != '':
            # add cur bc we only need to delete cur files which get changed each game
            # separate folder bc we ignore it when backing up files
            data_type += '/cur' # game logs/cur
            remover.delete_file(subject_name, todays_date, data_type)
            

        

    if not init_prev_dict == final_prev_dict:
        #print(subject_name + ' PREVIOUS year data changed so write to file')
        write_json_to_file(final_prev_dict, prev_file)


	# now that we have new cur game log, we can delete the old one
	# by using same name structure with different date
	# if file does not exist, do nothing
	# always good reason to have stat dict (or game log) saved is if we want to see how probs changed over time after each game
	# BUT stat dict also shows that for each condition so that actually applies to stat dict even better than game log
	# player_old_cur_season_log_key = player_name + ' ' + current_year_str + ' game log '
	# not_string = todays_date
	# writer.delete_file(player_old_cur_season_log_key, not_string) # delete file in folder with name containing key string but not other string
        



def display_game_info(after_injury_players, rare_prev_val_players):
    print('\n===Display Game Info===\n')


    title = 'after injury players'
    print('\n===' + title.title() + '===\n')

    after_injury_players_table = []
    for player in after_injury_players:
        after_injury_players_table.append([player])

    print(tabulate(after_injury_players_table, headers=['Player'])) # game, days after, injury type, restricted playtime

    for rare_cat, rare_cat_players in rare_prev_val_players.items():
        title = rare_cat
        print('\n===' + title.title() + '===\n')
        #header_row = ['Player', 'Stat', 'Norm', 'Prev']
        #rare_cat_players = header_row + rare_cat_players
        # remove last idx from all lists
        final_rare_cat_players = []
        for rare_player_data in rare_cat_players:
            final_rare_cat_players.append(rare_player_data[:-1])

        print(tabulate(final_rare_cat_players, headers=['G', 'Name', 'S', 'N', 'Pre', 'Ct', 'P', 'Tot']))


def display_list(list, title):
    print('\n===' + title.title() + '===\n')

    for item in list:
        print(item)

    print('\n==============================\n')