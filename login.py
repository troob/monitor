# Login to websites
# some websites have saved autofill in cache
# others need programmatic entry

import reader, writer
import os, time, re#, joblib


def test_login_website(website_name):#, website_names, url=''):
    print('\n===Test Login Website===\n')
    print('Input: web name: ' + website_name)

    # website_name = 'betmgm'
    # url = 'https://sports.ny.betmgm.com/en/sports/baseball-23/betting/usa-9/mlb-75'

    # website_name = 'betrivers'
    # url = 'https://ny.betrivers.com/?page=sportsbook&feed=featured#home'

    #if url == '':
    website_urls = {'betmgm':'https://sports.ny.betmgm.com/en/sports/baseball-23/betting/usa-9/mlb-75',
                    'betrivers':'https://ny.betrivers.com/?page=sportsbook&feed=featured#home',
                    'fanduel':'https://sportsbook.fanduel.com/'}
    url = website_urls[website_name]

    # first_window = False
    # if website_name == website_names[0]:
    #     first_window = True
    #     print('First Window')

    # open website
    driver = reader.open_react_website(url)


    return driver

def login_website(website_name, url=''):
    print('\n===Login Website===\n')
    print('Input: web name: ' + website_name)

    # website_name = 'betmgm'
    # url = 'https://sports.ny.betmgm.com/en/sports/baseball-23/betting/usa-9/mlb-75'

    # website_name = 'betrivers'
    # url = 'https://ny.betrivers.com/?page=sportsbook&feed=featured#home'

    if url == '':
        website_urls = {'betmgm':'https://sports.ny.betmgm.com/en/sports/baseball-23/betting/usa-9/mlb-75',
                        'betrivers':'https://ny.betrivers.com/?page=sportsbook&feed=featured#home',
                        'fanduel':'https://sportsbook.fanduel.com/'}
        url = website_urls[website_name]

    email = os.environ['EMAIL']
    token = os.environ[website_name.upper()]

    # open website
    driver = reader.open_react_website(url)

    # Get all available cookies
    # as soon as page opened
    # cookies = driver.get_cookies()
    # print('Cookies Before Login')
    # #print(cookies)
    # for cookie_idx in range(len(cookies)):
    #     cookie = cookies[cookie_idx]
    #     print('Cookie ' + str(cookie_idx) + ': ' + str(cookie))

    #time.sleep(30)

    cookies_file = 'data/cookies.json'
    saved_cookies = reader.read_json(cookies_file)
    website_cookies = []
    # save cookies if no cookies saved for this website yet???
    # No actually NEED to save cookies every session
    # Simplest to save every time new window opened
    #save_cookies = True
    if website_name in saved_cookies.keys(): 
        #save_cookies = False

        website_cookies = saved_cookies[website_name]
        #print('website_cookies: ' + str(website_cookies))
        for cookie in website_cookies:
            # Adds the cookie into current browser context
            driver.add_cookie(cookie)

    
    logged_in = False

    if website_name == 'betmgm':
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

        # Empty
        # <input type="text" 
        #   name="username" 
        #   id="userId" 
        #   autocomplete="username" 
        #   formcontrolname="username" 
        #   vntrackingevent="Event.Functionality.Login" 
        #   class="form-control form-control-i-l form-group-i-l form-control-f-w 
        #       ng-dirty 
        #       ng-invalid 
        #       ng-untouched">

        # Incomplete
        # <input type="text" 
        #   name="username" 
        #   id="userId" 
        #   autocomplete="username" 
        #   formcontrolname="username" 
        #   vntrackingevent="Event.Functionality.Login" 
        #   class="form-control form-control-i-l form-group-i-l form-control-f-w 
        #       ng-dirty 
        #       ng-invalid 
        #       ng-not-empty 
        #       ng-touched">

        # Complete
        # <input type="text" 
        #   name="username" 
        #   id="userId" 
        #   autocomplete="username" 
        #   formcontrolname="username" 
        #   vntrackingevent="Event.Functionality.Login" 
        #   class="form-control form-control-i-l form-group-i-l 
        #       ng-not-empty 
        #       form-control-f-w 
        #       ng-pristine 
        #       ng-valid 
        #       ng-touched">

        # Check if already logged in
        # Check if need to login

        login_page = False
        while not login_page:
            login_btn = driver.find_element('xpath', '//vn-menu-item-text-content[@data-testid="signin"]')
            print('login_btn: ' + login_btn.get_attribute('innerHTML'))
            login_btn.click()
            time.sleep(1)

            try:
                usr_field_div = driver.find_element('id', 'username')
                usr_field_html = usr_field_div.get_attribute('innerHTML')
                print('usr_field_div: ' + usr_field_html)

                login_page = True
            except:
                print('Not Login Page')

        # if username already entered previously and saved
        # then go to next field
        # if untouched empty field, then input email
        # if starts off blank, then save cookies bc we know not saved yet
        
        if re.search('ng-untouched', usr_field_html):
            usr_field = driver.find_element('id', 'userId')
            usr_field.send_keys(email)


        pwd_field = driver.find_element('name', 'password')
        pwd_field.send_keys(token)

        submit_btn = driver.find_element('xpath', '//button[@class="login w-100 btn btn-primary"]')
        print('submit_btn: ' + submit_btn.get_attribute('innerHTML'))
        submit_btn.click()
        time.sleep(3)


        # wait for verification manually first time
        # https://www.ny.betmgm.com/en/mobileportal/twofa
        verified = False
        while not verified:
            url = driver.current_url
            #print('current url: ' + url)
            if not url == 'https://www.ny.betmgm.com/en/mobileportal/twofa':
                verified = True
                print('Verified')
                time.sleep(1)

        logged_in = True



    # if save_cookies:
    #     # Get all available cookies
    #     # after logging in
    #     # time it after clicking login button
    #     cookies = driver.get_cookies()
    #     # print('Cookies After Login')
    #     # #print(cookies)
    #     # for cookie_idx in range(len(cookies)):
    #     #     cookie = cookies[cookie_idx]
    #     #     print('Cookie ' + str(cookie_idx) + ': ' + str(cookie))

    #     #all_cookies = saved_cookies
    #     saved_cookies[website_name] = cookies
    #     writer.write_json_to_file(saved_cookies, cookies_file)


    # Do Something
    time.sleep(1)

    if logged_in:

        # always save cookies before closing window 
        # to ensure most recent before next time opening
        # Get all available cookies
        # after logging in
        # time it after clicking login button
        cookies = driver.get_cookies()
        # print('Cookies After Login')
        # #print(cookies)
        # for cookie_idx in range(len(cookies)):
        #     cookie = cookies[cookie_idx]
        #     print('Cookie ' + str(cookie_idx) + ': ' + str(cookie))

        #all_cookies = saved_cookies
        saved_cookies[website_name] = cookies
        writer.write_json_to_file(saved_cookies, cookies_file)

    driver.close()


    return driver


website_name = 'betrivers'
driver = login_website(website_name)


# ensure actual odds match oddsview displayed odds
# open game page
# url = 'https://ny.betrivers.com/?page=sportsbook&feed=featured#home'
# # https://ny.betrivers.com/?page=sportsbook#event/1020374430
# driver = reader.open_react_website(url)
# # before getting odds, need to login? 
# # No, bc if not logged in and odds wrong then no need to login
# # so if format changes after login, 
# # need to make if statements for both formats
# if determine_logged_in(website_name)
# actual_odds = read_actual_odds()



# set window size so we can shift new windows right so all are visible
# size = driver.get_window_size()
# # print('size: ' + str(size))
# # pos = driver.get_window_position()
# # print('pos: ' + str(pos))

# # driver.set_window_size(1212, 1144)
# # driver.set_window_position(0, 0)

# website_name = 'betrivers'
# url = 'https://ny.betrivers.com/?page=sportsbook&feed=featured#home'
# #login_website(website_name, url)
# # script_str = "window.open('');" #" + url + "')" #, type:'window');" #, 'secondtab');"
# # driver.execute_script(script_str)

# driver.switch_to.new_window(type_hint='window')
# window2_x = size['width'] + 1
# driver.set_window_position(window2_x, 0)
# driver.get(url)

# time.sleep(5)

# driver.switch_to.window(driver.window_handles[0])

#time.sleep(100)

# cookies = driver.get_cookies()
# print('cookies:\n' + str(cookies))
# driver.close()


# website_names = ('betmgm', 'betrivers')
# # 3 jobs bc 3 windows: 1 for monitor and 2 for bets
# both_side_bets = joblib.Parallel(n_jobs=3)(joblib.delayed(test_login_website)(website_name, website_names) for website_name in website_names)