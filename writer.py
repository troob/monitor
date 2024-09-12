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




# if ev, just close 1 window
# if arb side 1, just close 1 window
# if arb side 2, close both windows
# then relinquish control back to main monitor window
def close_bet_windows(driver, side_num):
    print('\n===Close Bet Windows===\n')
    print('side_num: ' + str(side_num) + '\n')

    # close window 1 or 2
    driver.close()

    # if side 2, both windows open
    # so also close side 1 window
    if side_num == 2:
        driver.switch_to.window(driver.window_handles[2])
        driver.close()
    
    # send back to main window
    driver.switch_to.window(driver.window_handles[0])



# Assume already on webpage
def login_website(website_name, driver, cookies_file, saved_cookies, url):
    print('\n===Login Website===\n')
    print('Input: web name: ' + website_name)
    #print('\nOutput: Logged In\n')

    email = os.environ['EMAIL']
    token = os.environ[website_name.upper()]

    
    logged_in = False

    if website_name == 'betrivers':
        # look for my account menu btn
        # betrivers always requires login new window so may not need this for betrivers
        # unless leave open window for certain predefined time period
        # such as 5 min bc if haven't seen prop in 5min then probably not for a while???
        # not necessarily so maybe dont keep open at all unless already have more props in queue
        try:
            driver.find_element('xpath', '//div[@data-target="menu-user-account"]')
            print('Already Logged In Betrivers')
        except:
            print('Login Betrivers')
            # login_betrivers()

        # keep looking for login page
        # OR just click login btn once???
        # problem is if not loaded yet then will move on before login
        login_page = False
        while not login_page:
            # class = sc-gHLcSH cnmSeS
            # id=rsi-top-navigation
            # div
            # second div
            # button
            login_btn = driver.find_element('id', 'rsi-top-navigation').find_element('tag name', 'div').find_element('xpath', 'div[2]').find_element('tag name', 'button')   # .find_element('class name', 'sc-gHLcSH')
            print('login_btn: ' + login_btn.get_attribute('innerHTML'))
            login_btn.click()
            time.sleep(1)

            try:
                usr_field_input = driver.find_element('id', 'login-form-modal-email')
                usr_field_html = usr_field_input.get_attribute('outerHTML')
                print('usr_field_html: ' + usr_field_html)

                login_page = True
            except:
                print('Not Login Page')

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
        time.sleep(3)

        popup = True
        while popup:
            try:
                # class = close-modal-button-container
                close_popup_btn = driver.find_element('xpath', '//div[@class="close-modal-button"]')
                print('close_popup_btn: ' + close_popup_btn.get_attribute('innerHTML'))
                close_popup_btn.click()
                time.sleep(1)

            # First time login each day shows profit boost popup instead
            except:
                print('Close Profit Boost Popup')
                popup = False

                # 'data-translate="BTN_CLOSE_TITLE"'
                try:
                    close_boost_btn = driver.find_element('xpath', '//a[@data-translate="BTN_CLOSE_TITLE"]')
                    close_boost_btn.click()
                    print('Closed Profit Boost')
                except:
                    print('No Profit Boost')

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
            print('Go to Login Page')
            # OPTION 1
            # driver.get(login_url) 
             
            # OPTION 2
            login_btn = driver.find_element('xpath', '//vn-menu-item-text-content[@data-testid="signin"]')
            print('login_btn: ' + login_btn.get_attribute('innerHTML'))
            login_btn.click()

            time.sleep(3)  
        else:
            print('\nAlready Logged In\n')
            return
        
        # try to simply login with dialog
        # even tho expected error
        # sometimes works
        login_page = False
        while not login_page:
            try:
                submit_btn = driver.find_element('class name', 'login')#find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
                print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
                login_page = True
            except:
                print('Loading Login Page...')
                time.sleep(1)
        
        submit_btn.click()
        time.sleep(3) 

        # if error, try backup login method
        pwd_msg = ''
        try:
            pwd_msg = driver.find_element('class name', 'm2-validation-message').get_attribute('innerHTML').lower()
            print('pwd_msg: ' + pwd_msg)
        except:
            print('Loading...')

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
                
            reg_link.click()
            time.sleep(3)

            login_link = driver.find_element('class name', 'conversation-textalign').find_element('tag name', 'a')
            login_link.click()
            time.sleep(3) 

            usr_field_html = driver.find_element('id', 'username').get_attribute('innerHTML')
            if re.search('ng-untouched', usr_field_html):
                print('Enter Username')
                usr_field = driver.find_element('id', 'userId')
                usr_field.send_keys(email)
                time.sleep(1)

            pwd_field = driver.find_element('id', 'password')
            pwd_field_html = pwd_field.get_attribute('innerHTML')
            if re.search('ng-untouched', pwd_field_html):
                print('Enter Password')
                #pwd_field = driver.find_element('name', 'password')
                pwd_field.clear()
                time.sleep(1)
                pwd_field.send_keys(token)
                time.sleep(3)

            submit_btn = driver.find_element('class name', 'login')#find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
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




         # if still loading, not logged in
        while not logged_in:
            try:
                pwd_field = driver.find_element('name', 'password')
            except:
                logged_in = True
                print('\nLogin Success\n')


        # login_page = False
        # usr_field_html = pwd_field_html = ''
        # while not login_page:
            
        #     try:
        #         usr_field_html = driver.find_element('id', 'username').get_attribute('innerHTML')
        #         #usr_field_html = usr_field_div.get_attribute('innerHTML')
        #         #print('usr_field_html: ' + usr_field_html)

        #         pwd_field = driver.find_element('id', 'password')
        #         pwd_field_html = pwd_field.get_attribute('innerHTML')
        #         print('pwd_field_html: ' + pwd_field_html)

        #         login_page = True
        #         print('Login Page')
        #     except:
        #         print('Not Login Page')

                
            # try:
            #     # if login page open btn available
            #     # OR login submit btn available
            #     # got to login url

            #     # check for btn to open login dialog bc that means not logged in
            #     try:
            #         login_btn = driver.find_element('xpath', '//vn-menu-item-text-content[@data-testid="signin"]')
            #         #print('login_btn: ' + login_btn.get_attribute('innerHTML'))
            #         driver.get(login_url)
            #     except:
            #         print('No button to open login dialog, so check if session expired so already on login page.')
                
                    
            #         # check already sent to login page
            #         try:
            #             pwd_field = driver.find_element('id', 'password')
            #         except:
            #             print('Not on login page, so go to login page.')
            #             driver.get(login_url)
                        
            #         # check session expired by login duration Nan
            #         try:
            #             login_duration = driver.find_element('class name', 'login-duration-time').get_attribute('innerHTML')
            #             print('login_duration: ' + login_duration)
            #             if login_duration == 'NaN:NaN:NaN':
            #                 # go to login page
            #                 driver.get(login_url)
            #         except:
            #             print('No login duration, so check if sent to login page.')

            #     if need_login:
            #         driver.get(login_url)    
            #     else:
            #         print('\nAlready Logged In\n')

            #     # problem with login dialog
            #     # so instead of clicking login button to get dialog
            #     # go direct to login url page
            #     #login_btn.click()
            #     #driver.get(login_url)
            #     time.sleep(5)
            # except:
                
            #     # tag vn-login-duration
            #     # class login-duration-time
            #     # NaN:NaN:NaN
            #     login_duration = driver.find_element('class name', 'login-duration-time').get_attribute('innerHTML')
            #     print('login_duration: ' + login_duration)
            #     if login_duration == 'NaN:NaN:NaN':
            #         driver.get(login_url)
            #         time.sleep(5)
            #     else:
            #         print('\nAlready Logged In\n')
            #         return




                # print('\nCheck if Session Timed Out to Login Page or Glitch Home Page\n')
                # # login button???
                # time.sleep(1)

                # # tag vn-login-duration
                # # class login-duration-time
                # # NaN:NaN:NaN
                # login_duration = driver.find_element('class name', 'login-duration-time').get_attribute('innerHTML')
                # print('login_duration: ' + login_duration)
                # if login_duration == 'NaN:NaN:NaN':
                #     # close window and reopen
                #     print('Login Error: Close and Reopen')
                #     driver.close()
                #     driver.get(url)
                #     # init with old cookies and then save new cookies after loading
                #     saved_cookies = reader.add_cookies(driver, website_name, cookies_file)
                #     time.sleep(2) # wait to load. sometimes fails at 1 sec
                #     reader.save_cookies(driver, website_name, cookies_file, saved_cookies)




                # # if funds say zero not enough to tell if timed out bc may actually be 0 funds
                # # so what is identifier of timeout???
                # else:
                #     print('\nAlready Logged In\n')
                #     return

            
        # Login Page
        # if username already entered previously and saved
        # then go to next field
        # if untouched empty field, then input email
        # if starts off blank, then save cookies bc we know not saved yet
        
        # if re.search('ng-untouched', usr_field_html):
        #     print('Enter Username')
        #     usr_field = driver.find_element('id', 'userId')
        #     usr_field.send_keys(email)
        #     time.sleep(1)

        # # for some reason not recognizing password already there
        # # clear not working
        # # pwd field has class ng untouched even tho pwd already there
        # # print('pwd_field_html: ' + pwd_field.get_attribute('outerHTML'))
        # # if re.search('ng-untouched', pwd_field_html):
        # print('Enter Password')
        # pwd_field = driver.find_element('name', 'password')
        # pwd_field.clear()
        # #time.sleep(3)
        # # # #print('Cleared Twice') # does not work
        # # # print('Cleared 1') # works but still error after clicking submit
        # # # time.sleep(3)

        # pwd_field.send_keys(token)
        # #time.sleep(3)
        # # # print('Entered 1')
        # # # time.sleep(3)
        
        # pwd_field.clear()
        # #time.sleep(3)
        # # # print('Cleared 2')
        # # # time.sleep(3)

        # # pwd_field.send_keys(token)
        # # time.sleep(3)
        # pwd_field.send_keys(token)
        # #time.sleep(3)
        # # print('Entered 2')
        # # time.sleep(3)

        # #driver.switch_to.active_element
        # # pwd_field = driver.find_element('name', 'password')
        # # pwd_field.send_keys('')

        # try:
        #     submit_btn = driver.find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
        #     print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
        #     submit_btn.click()
        #     time.sleep(3)
        # except:
        #     print('Cannot Click Submit Button')
        #time.sleep(21) # 21 seconds enough time to inspect element for test




       

        # if not logged_in:
        #     print('Not Logged In Yet, Try Again')
        #     # OPTION 1 fails
        #     # go to other login link fails too
        #     driver.get(login_url2) 
        #     time.sleep(3) 

        #     print('Enter Password')
        #     pwd_field = driver.find_element('name', 'password')
        #     pwd_field.clear()
        #     pwd_field.send_keys(token)
        #     pwd_field.clear()
        #     pwd_field.send_keys(token)
        #     submit_btn = driver.find_element('class name', 'login')#find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
        #     print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
        #     submit_btn.click()
        #     time.sleep(3) 

        #     # OPTION 2
        #     # OR try clicking thru registration page bc seems to work
        #     reg_link = driver.find_element('class name', 'registration-link')
        #     reg_link.click()
        #     time.sleep(3)

        #     login_link = driver.find_element('class name', 'conversation-textalign').find_element('tag name', 'a')
        #     login_link.click()
        #     time.sleep(3) 

        #     # may not need to renter pwd bc login already clickable
        #     # print('Enter Password')
        #     # pwd_field = driver.find_element('name', 'password')
        #     # pwd_field.clear()
        #     # pwd_field.send_keys(token)
        #     # pwd_field.clear()
        #     # pwd_field.send_keys(token)
        #     submit_btn = driver.find_element('class name', 'login')#find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
        #     print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
        #     submit_btn.click()
        #     time.sleep(3) 



        # Close Survey Popup
        # data-aut="button-close"
        # class surveyBtn_close




        # wait for verification manually first time
        # https://www.ny.betmgm.com/en/mobileportal/twofa
        # verified = False
        # while not verified:
        #     try:
        #         # if still login dialog, loading, not verified
        #         login_dialog = driver.find_element('tag name', 'lh-login')
        #         print('Still Logging In...')

        #         try:
        #             # check error
        #             # class, m2-validation-message, Please enter your password.
        #             pwd_msg = driver.find_element('class name', 'm2-validation-message').get_attribute('innerHTML').lower()
        #             print('pwd_msg: ' + pwd_msg)

        #             # try refreshing page
        #             driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'r')
        #             time.sleep(3)

        #             # usr_field = driver.find_element('id', 'userId')
        #             # usr_field.clear()
        #             # usr_field.send_keys(email)
        #             # time.sleep(1)

        #             # # if pwd msg, reenter pwd
        #             # pwd_field = driver.find_element('name', 'password')
        #             # pwd_field.clear()
        #             # pwd_field.send_keys(token)
        #             # time.sleep(1)

        #             # submit_btn = login_dialog.find_element('class name', 'login')
        #             # print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
        #             # submit_btn.click()

        #             # time.sleep(3)
        #         except:
        #             print('No pwd msg')

        #     except:
        #         print('No Login Dialog')
        #         # if no login dialog after pressing submit
        #         # then verified
        #         verified = True
        #         print('Verified')

        #     time.sleep(1)

            
        #     # if still submit btn then check if login error
        #     # try:
        #     #     submit_btn = driver.find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
        #     #     print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
            
        #     #     try:
        #     #         # tag vn-message-panel, scope="login"
        #     #         # class message-panel
        #     #         # class theme-error-i
        #     #         # class cms-container
        #     #         #  We've encountered a problem. Please try again
        #     #         error_msg = driver.find_element('class name', 'cms-container').get_attribute('innerHTML').lower()
        #     #         print('error_msg: ' + error_msg)
                    
        #     #     except:
        #     #         print('Loading...')

        #     #     time.sleep(1)
        #     # except:
        #     #     verified = True
        #     #     print('Verified')
        #     #     time.sleep(1)

        #     # url = driver.current_url
        #     # #print('current url: ' + url)
        #     # if not url == 'https://www.ny.betmgm.com/en/mobileportal/twofa':
        #     #     verified = True
        #     #     print('Verified')
        #     #     time.sleep(1)

        



    # Do Something
    time.sleep(1)

    if logged_in:
        print('Logged In, Do We Need to Save Cookies???')
        #reader.save_cookies(driver, website_name, cookies_file, saved_cookies)


    #return driver not needed bc already in parent fcn
    #gets updated

def clear_betslip(driver):
    # Require that betslip is empty
    # So look for betslip html to see if open
    # if open, click clear all
    try:
        clear_btn = driver.find_element('class name', 'mod-KambiBC-betslip__clear-btn')
        clear_btn.click()
        print('Cleared Betslip')
    except:
        try:
            remove_pick_btn = driver.find_element('class name', 'mod-KambiBC-betslip-outcome__close-btn')
            remove_pick_btn.click()
            print('Removed Pick')
        except:
            print('Betslip Empty')

def wager_remaining_funds(driver):
    print('\n===Wager Remaining Funds===\n')

    # enter max amount in field
    funds_element = driver.find_element('class name', 'user-balance')
    # remove $
    funds = float(funds_element.get_attribute('innerHTML')[1:])
    print('funds: ' + str(funds))

    wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
    # print('wager_field: ' + wager_field.get_attribute('outerHTML'))
    wager_field.clear()
    wager_field.send_keys(funds)
    time.sleep(1)
    print('Input Funds')


def place_bet(bet_dict, driver, final_outcome, cookies_file, saved_cookies, pick_type='ev', test=True):
    print('\n===Place Bet===\n')
    print('Input: bet_dict = ' + str(bet_dict))
    
    place_bet = True

    website_name = bet_dict['source']
    print('website_name = ' + website_name)

    url = bet_dict['link']

    # wait to load if not clearing betslip???

    # print('Has Page Shifted Inadvertently Yet??') No

    # click bet btn to add to betslip
    if final_outcome is not None:

        if website_name == 'betmgm':
            #time.sleep(1) # load should be after action not before

            logged_in = False
            login_website(website_name, driver, cookies_file, saved_cookies, url)

            bet_size = determiner.determine_limit(bet_dict, website_name, pick_type, test)

            while not logged_in:
                try:
                    wager_field = driver.find_element('class name', 'stake-input-value')#.find_element('tag name', 'input')
                    logged_in = True
                except:
                    print('Not Logged In Yet')
                    time.sleep(1)

            # login takes time so check if odds changed
            place_bet_btn = driver.find_element('class name', 'place-button')
            # check if enough funds
            place_btn_text = place_bet_btn.find_element('class name', 'ds-btn-text').get_attribute('innerHTML').lower()
            print('place_btn_text: ' + str(place_btn_text))
            # if odds changed, if ev, stop and continue to monitor
            if not re.search('accept', place_btn_text):
            
                #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
                placeholder = wager_field.get_attribute('placeholder')
                #print('placeholder: ' + placeholder)
                if not placeholder == '':
                    wager_field.clear()
                    time.sleep(1)
                wager_field.send_keys(bet_size)
                time.sleep(1)
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
                    wager_remaining_funds(driver)
                place_bet_btn.click()
                time.sleep(1)
                print('Placed Bet to Find Limit')
                time.sleep(3) 
                # except:
                #     print('Error: No Place Bet Button!')

                # wait to finish loading
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

                        # test wait
                        #time.sleep(100)

                        

                        # Go to my bets to confirm
                        my_bets_btn = driver.find_element('class name', 'myBetsTab')
                        my_bets_btn.click()
                        print('Clicked My Bets')
                        time.sleep(3) # TEMP wait to manually check bet placed before closing

                        open_bets_btn = driver.find_element('class name', 'sliding-menu').find_element('xpath', 'div[2]')
                        open_bets_btn.click()
                        print('Clicked Open Bets')
                        time.sleep(3)

                    except:
                        print('\nBet Error\n')
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

                        if not re.search('limit', alert_msg):
                            # if not limit problem, then odds changed so close and continue
                            place_bet = False
                            # if not limit problem, check if locked or odds changed
                            # if locked, remove bet from slip and close window
                            #try:
                            # class name: place-button-message
                            btn_msg = driver.find_element('class name', 'place-button-message').get_attribute('innerHTML').lower() # Wager too high
                            print('btn_msg: ' + btn_msg)

                    # except:
                    #     print('Unknown Error while placing bet')


                        # For EV, place at limit
                        if not test and place_bet:
                            place_bet_btn = driver.find_element('class name', 'place-button')
                            print('place_bet_btn: ' + place_bet_btn.get_attribute('innerHTML'))
                            place_bet_btn.click()
                            time.sleep(3)
                            print('Placed Bet')

                            # NEED to Handle Odds Change on subsequent attempts
                            # loop while odds in range and not yet placed
                            # but for EV if odds change then skip
                            try:
                                close_receipt_btn = driver.find_element('tag name', 'bs-digital-result-state').find_element('class name', 'result-summary__actions').find_element('tag name', 'button')
                                print('Done Loading')
                                close_receipt_btn.click()
                                # DEMO:
                                time.sleep(1)
                                #time.sleep(1) # Wait for bet to fully load and submit before moving on
                                print('Closed Receipt')
                            except:
                                print('\nBet Failed\n')
                                print('Odds Change or Other Error???')

                                # handle session timeout
                                # read bottom msg below button or wager field???
                                print('\nHandle Session Timeout\n')
                                time.sleep(100)


                            my_bets_btn = driver.find_element('class name', 'myBetsTab')
                            my_bets_btn.click()
                            print('Clicked My Bets')
                            time.sleep(3) # TEMP wait to manually check bet placed before closing

                            open_bets_btn = driver.find_element('class name', 'sliding-menu').find_element('xpath', 'div[2]')
                            open_bets_btn.click()
                            print('Clicked Open Bets')
                            time.sleep(3)

                            # break loading loop even if bet failed
                            loading = False
                            print('Done Loading')


                

                # if test:
                #     # test wait
                #     time.sleep(100)
                #     # test close
                #     driver.close()

        elif website_name == 'betrivers':
            #time.sleep(1) # load

        
            clear_betslip(driver)
            

            # print('Has Page Shifted Inadvertently Yet??') No
            # time.sleep(100)

            # if not already clicked
            # data-pressed=\"null\"

            # final_outcome: 
            # <button type="button" 
            #   class="sc-aXZVg dYaJxz sc-dAlyuH buSnVV KambiBC-betty-outcome" 
            #   data-touch-feedback="true">
            #   <div data-touch-feedback="true" 
            #       class="sc-gEvEer kOrbku">
            #       <div data-touch-feedback="true" 
            #           class="sc-eqUAAy kLwvTb">
            #           <div class="sc-fqkvVR cyiQDV">Over</div>
            #           <div data-touch-feedback="true" 
            #               class="sc-dcJsrY gCFiej">6.5
            #           </div>
        #           </div>
        #           <div data-touch-feedback="true" 
        #               class="sc-iGgWBj kAIwQy">
        #               <div class="sc-jXbUNg jRmJQc"></div>
        #               <div data-touch-feedback="true" 
        #                   class="sc-gsFSXq dqtSKK">
        #                   <div data-touch-feedback="true" 
        #                       class="sc-kAyceB gIMtGL">-360
        #                   </div>
    #                   </div>
    #               </div>
    #           </div>
            # </button>


            # final_outcome: 
            # <div data-touch-feedback="true" 
            #   class="sc-gEvEer kOrbku"><div data-touch-feedback="true" class="sc-eqUAAy kLwvTb"><div class="sc-fqkvVR cyiQDV">Over</div><div data-touch-feedback="true" class="sc-dcJsrY gCFiej">6.5</div></div><div data-touch-feedback="true" class="sc-iGgWBj kAIwQy"><div class="sc-jXbUNg jRmJQc"></div><div data-touch-feedback="true" class="sc-gsFSXq dqtSKK"><div data-touch-feedback="true" class="sc-kAyceB gLUWXi">-360</div></div></div></div>
            #print('final_outcome before click: ' + final_outcome.get_attribute('outerHTML'))
            if not re.search('data-pressed=\"null\"', final_outcome.get_attribute('outerHTML')):
                # 
                # #driver.execute_script('window.scrollTo(0, 0);')
                # 
                try:
                    final_outcome.click()
                except:
                    coordinates = final_outcome.location_once_scrolled_into_view
                    print('coordinates: ' + str(coordinates))
                    driver.execute_script("window.scrollTo(coordinates['x'], coordinates['y'])")
                    #driver.execute_script("arguments[0].scrollIntoView(true);", final_outcome)
                    final_outcome.click()
                
                time.sleep(1)

            #print('final_outcome after click: ' + final_outcome.get_attribute('outerHTML'))      

            # Need to double check no old bets in slip 
            # bc glitch may hide old betslip until new bet clicked
            # for now simplest way is to keep only last bet in slip bc adds to bottom
            # later parlays will need to keep multiple so cannot assume only 1
            remove_bet_btns = driver.find_elements('class name', 'mod-KambiBC-betslip-outcome__close-btn')
            if len(remove_bet_btns) > 1:
                # remove old bets
                print('Remove Old Bets')
                for btn in remove_bet_btns[:-2]:
                    btn.click()
                    time.sleep(1)
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
            if not test:
                login_website(website_name, driver, cookies_file, saved_cookies, url)

            # For Arbs, find limit by placing large bet we know above limit
            # find_bet_limit(website_name, driver)

            # For EVs, place bet at given size, rounded to nearest whole number
            # Then if after place bet, returns msg over limit, place bet at limit

            # === Find Limit === 
            # If EV, start with given wager size
            # If Arb, find limits on both sides
            bet_size = 0
            if not test and pick_type == 'ev':
                bet_size = converter.round_half_up(float(re.sub('\$','',bet_dict['size'])))
            else: # if test or arb
                # enter bet size into wager field
                # Test find limit with bet size guaranteed above limit
                # depends on source and market
                # for betrivers, $300 is max 
                # so if less than 300 available then need to set limits diff by market
                max_bet = 0
                if website_name == 'betrivers':
                    max_bet = 400

                bet_size = max_bet #bet_dict['size']

            #submit_wager(bet_size, website_name)
            # the field uses a changing id so get container 
            # and then know 1st field is wager field
            #input_container = driver.find_element('class name', 'mod-KambiBC-to-win-input__container')
            #print('input_container: ' + input_container.get_attribute('innerHTML'))
            try:   
                wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
            except:
                final_outcome.click()
                time.sleep(1)
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
            place_bet_btn.click()
            time.sleep(1) # need wait for bet to fully load and submit before moving on
            place_bet_btn.click()
            time.sleep(1)
            print('Clicked bet twice')
            print('Placed Bet')
            time.sleep(1) 

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
                except:
                    print('Unknown Error while placing bet')

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
                    print('place_bet_btn: ' + place_bet_btn.get_attribute('innerHTML'))
                    # wait for place bet btn to enable
                    place_btn_disabled = place_bet_btn.get_attribute('disabled')
                    while place_btn_disabled == 'true':
                        try:
                            place_btn_disabled = place_bet_btn.get_attribute('disabled')
                            print('place_btn_disabled: ' + place_btn_disabled)
                        except:
                            print('Place Button Enabled')
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

                            if error_title == 'not enough money':
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
    
        # Navigate to bet page to confirm bet placed
        
    # Close Window after placing bet
    # Close Window before going to next pick
    # bc only 1 window at a time
    if not test:
        print('Close Bet Window\n')
        driver.close() # comment out to test

    # always switch bot back to main window so it can click btns  
    driver.switch_to.window(driver.window_handles[0])

# just like place bet but only up to getting limit
# remove the final place bet click
# starts with window already open from reading actual odds
def find_bet_limit(bet_dict, driver, final_outcome, cookies_file, saved_cookies, pick_type, test, side_num):
    print('\n===Find Bet Limit===\n')
    print('Input: bet_dict = {...} = ' + str(bet_dict))
    print('Input: final_outcome = ' + str(final_outcome))
    print('\nOutput: bet_limit = float\n')

    bet_limit = 0

    # if bet dict has bet1/bet2 then we know arb
    # so set single bet vals in dict
    if 'bet1' in bet_dict.keys():
        bet_key = 'bet' + str(side_num)
        source_key = 'source' + str(side_num)
        odds_key = 'odds' + str(side_num)
        link_key = 'link' + str(side_num)
        size_key = 'size' + str(side_num)

        bet_dict['bet'] = bet_dict[bet_key]
        bet_dict['source'] = bet_dict[source_key]
        bet_dict['odds'] = bet_dict[odds_key]
        bet_dict['link'] = bet_dict[link_key]
        bet_dict['size'] = bet_dict[size_key]

    website_name = bet_dict['source']
    print('website_name = ' + website_name)
    url = bet_dict['link']

    # continue if no bet
    # should not reach this point bc actual odds would also be none
    if final_outcome is None:
        print('final_outcome none, Close Bet Window\n')
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return bet_limit
    
    # get max number that is less than available funds
    # but always over known limit
    max_bet_size = determiner.determine_source_limit(website_name) #determine_limit(bet_dict, website_name, pick_type, test)

    if website_name == 'betmgm':

        logged_in = False
        login_website(website_name, driver, cookies_file, saved_cookies, url)

        while not logged_in:
            try:
                wager_field = driver.find_element('class name', 'stake-input-value')#.find_element('tag name', 'input')
                logged_in = True
            except:
                print('Not Logged In Yet')
                time.sleep(1)

        # login takes time so check if odds changed
        place_bet_btn = driver.find_element('class name', 'place-button')
        # check if enough funds
        place_btn_text = place_bet_btn.find_element('class name', 'ds-btn-text').get_attribute('innerHTML').lower()
        print('place_btn_text: ' + str(place_btn_text))
        # if odds changed, if ev, stop and continue to monitor
        if re.search('accept', place_btn_text):
            # accept odds for now until we check other side of arb
            place_bet_btn.click()
            time.sleep(1)

            new_odds = '' # driver.find_element()
        
        #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
        placeholder = wager_field.get_attribute('placeholder')
        #print('placeholder: ' + placeholder)
        if not placeholder == '':
            wager_field.clear()
            time.sleep(1)
        wager_field.send_keys(max_bet_size)
        time.sleep(1)

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
            return remaining_funds


        place_bet_btn.click()
        time.sleep(1)
        print('Placed Bet to Find Limit')
        time.sleep(3) 

        # wait to finish loading
        loading = True
        while loading:
            try:
                alert_msg = driver.find_element('class name', 'alert-content__message').get_attribute('innerHTML').lower() # Wager too high
                print('alert_msg: ' + alert_msg)
                loading = False
                print('Done Loading placed bet to find limit')

                if not re.search('limit', alert_msg):
                    # if not limit problem, then odds changed so close and continue
                    # if not limit problem, check if locked or odds changed
                    # if locked, remove bet from slip and close window
                    btn_msg = driver.find_element('class name', 'place-button-message').get_attribute('innerHTML').lower() # Wager too high
                    print('btn_msg: ' + btn_msg)
            except:
                print('Loading placed bet to find limit...')
                time.sleep(1)

        bet_limit = wager_field.get_attribute('value') # or getText()

    elif website_name == 'betrivers':
        
        clear_betslip(driver)

        # click outcome btn to add to betslip
        if not re.search('data-pressed=\"null\"', final_outcome.get_attribute('outerHTML')):
            try:
                final_outcome.click()
            except:
                coordinates = final_outcome.location_once_scrolled_into_view
                print('coordinates: ' + str(coordinates))
                driver.execute_script("window.scrollTo(coordinates['x'], coordinates['y'])")
                #driver.execute_script("arguments[0].scrollIntoView(true);", final_outcome)
                final_outcome.click()
            
            time.sleep(1)

        # remove old bets from slip
        remove_bet_btns = driver.find_elements('class name', 'mod-KambiBC-betslip-outcome__close-btn')
        if len(remove_bet_btns) > 1:
            # remove old bets
            print('Remove Old Bets')
            for btn in remove_bet_btns[:-2]:
                btn.click()
                time.sleep(1)

        login_website(website_name, driver, cookies_file, saved_cookies, url)

        # add max bet size to wager field
        try:   
            wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')
        except:
            final_outcome.click()
            time.sleep(1)
            wager_field = driver.find_element('class name', 'mod-KambiBC-stake-input__container').find_element('tag name', 'input')

        #print('wager_field: ' + wager_field.get_attribute('outerHTML'))
        wager_field.send_keys(max_bet_size)

        # click Place Bet to find limit
        place_bet_btn = driver.find_element('class name', 'mod-KambiBC-betslip__place-bet-btn')
        #print('place_bet_btn: ' + place_bet_btn.get_attribute('innerHTML'))
            
        # Need to click twice for this website
        place_bet_btn.click()
        time.sleep(1) # need wait for bet to fully load and submit before moving on
        place_bet_btn.click()
        time.sleep(1)
        print('Clicked bet twice')
        print('Placed Bet')
        time.sleep(1) 

        # wait to finish loading
        loading = True
        while loading:
            try:
                error_title = driver.find_element('class name', 'mod-KambiBC-betslip-feedback__title').get_attribute('innerHTML').lower() # Wager too high
                print('error_title: ' + error_title)

                loading = False
                print('Done Loading placed bet to find limit')

                if error_title == 'not enough money':
                    print('Not enough money')
                    remaining_funds = reader.read_remaining_funds(driver, website_name)
                    return remaining_funds

                # Sorry, the maximum allowed wager is $4.01.
                error_msg = driver.find_element('class name', 'mod-KambiBC-betslip-feedback__paragraph').get_attribute('innerHTML').lower() 
                print('error_msg: ' + error_msg)

            except:
                print('Loading placed bet to find limit...')
                time.sleep(1)

        bet_limit = error_msg.split('$')[1][:-2]


        
    # Do not close window after finding limit
    
    bet_limit = float(bet_limit)
    print('bet_limit: ' + str(bet_limit))
    return bet_limit


def place_bets_simultaneously(driver, bet1_size, bet2_size, wager_field1, wager_field2, place_btn1, place_btn2):
    print('\n===Place Bets Simultaneously===\n')

def place_arb_bets(arb, driver, final_outcomes, cookies_file, saved_cookies, pick_type, test):
    print('\n===Place Arb Bets===\n')
    print('Input: arb = {...} = ' + str(arb))
    print('Input: final_outcomes = ' + str(final_outcomes))

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
	
    # go up to finding limit
    # and then go to other side to get limit
    # we need to get wager field and place btn to find limit
    # so save them here and pass them to place bet fcn
    # so we do not need to get them twice
    # BUT does driver.find_element actually take more time than retrieving from memory? probably
    # bet_limit_data = find_bet_limit(arb, driver, final_outcomes[0], cookies_file, saved_cookies, pick_type, test, side_num=1)
    # arb['limit1'] = bet_limit_data[0]
    # arb['payout1'] = bet_limit_data[1]
    # arb['wager field1'] = bet_limit_data[2]
    # arb['place btn1'] = bet_limit_data[3]

    # # at this point we checked actual odds 
    # # but now that we logged in and found limit, odds may have changed

    # bet_limit_data = find_bet_limit(arb, driver, final_outcomes[1], cookies_file, saved_cookies, pick_type, test, side_num=2)
    # arb['limit2'] = bet_limit_data[0]
    # arb['payout2'] = bet_limit_data[1]
    # arb['wager field2'] = bet_limit_data[2]
    # arb['place btn2'] = bet_limit_data[3]

    # bet1_size, bet2_size = determiner.determine_arb_bet_sizes(arb)
    
    # arb['size1'] = bet1_size
    # arb['size2'] = bet2_size

    # # write in and place bets
    # place_bets_simultaneously(driver, arb)



    print('Done Placing Both Bets Auto Arb, so close windows')
    close_bet_windows(driver, side_num=2)
    

# write 1 arb in post
def write_arb_to_post(arb, client, post=False):
    print('\n===Write Arb to Post===\n')
    print('arb = {val:x, ...} = ' + str(arb)) 

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

    
    # Make list of sizes depending on limit, from 1000 to 100, every 100
    # size1_options = []
    # size2_options = []
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

    #arb_num = str(arb_idx + 1)
    props_str = '\n===Arb===\n'
    props_str += '\n' + source1 + ' ' + odds1 + ', ' + source2 + ' ' + odds2 +'. \n\n'
    props_str += game + ' - \n\n'
    props_str += market + ' - \n\n'
    props_str += bet1 + ', ' + bet2 + ' - \n\n'
    props_str += value + '%' + ' - \n\n'
    

    # split player and market in given market field
    # so we can see market at the top and decide if we can take the bet or if limited or suspicious
    player = ''
    if re.search('-', market):
        market_data = market.split('-')
        player = market_data[0].strip()
        market = market_data[1].strip()
    #props_str += '\nBETS: ' + bet1 + ' ' + odds1 + ', ' + bet2 + ' ' + odds2 +'. \n\n'
    props_str += '\nSOURCE 1: ' + source1 + ', ' + odds1 + ', ' + bet1 + ' \n'
    props_str += 'SOURCE 2: ' + source2 + ', ' + odds2 + ', ' + bet2 + ' \n\n'
    if player != '':
        props_str += 'PLAYER: ' + player + ' \n\n'
    props_str += 'MARKET: ' + market + ' \n\n'
    #props_str += 'BETS: ' + bet1 + ', ' + bet2 + ' \n\n'
    props_str += 'GAME: ' + game + ' \n\n'
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

    print('\n===New Arb===\n')
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


def write_ev_to_post(ev, client, post=False):
    print('\n===Write EV to Post===\n')
    print('ev: ' + str(ev))

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
    size = '$' + str(converter.round_half_up(float(re.sub('\$','',ev['size']))))



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
        market_data = market.split('-')
        player = market_data[0].strip()
        market = market_data[1].strip()
    #props_str += '\nBETS: ' + bet1 + ' ' + odds1 + ', ' + bet2 + ' ' + odds2 +'. \n\n'
    props_str += '\nSOURCE: ' + source + ', ' + odds + ' \n\n'
    if player != '':
        props_str += 'PLAYER: ' + player + ' \n\n'
    props_str += 'MARKET: ' + market + ', ' + bet + ' \n\n'
    props_str += 'GAME: ' + game + ' \n\n'
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

    print('\n===EV===\n')
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
            market_data = market.split('-')
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
            market_data = market.split('-')
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