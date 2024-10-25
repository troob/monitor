# read odds for all different websites

import reader, writer, converter
import time, re



# diff markets have diff formats
# moneyline has only 1 div but others have 2
def read_outcome_label(outcome, market):
    print('\n===Read Outcome Label===\n')
    print('Input: outcome: ' + outcome.get_attribute('innerHTML'))
    print('Input: market = ' + market)

    outcome_sub_element_1 = outcome.find_element('tag name', 'div')
    parts = outcome_sub_element_1.find_elements('tag name', 'div')
    print('Parts 1:')
    for part in parts:
        print('part: ' + part.get_attribute('innerHTML'))
    
    # Need to tell if grayed out NA by class or lack of odds???
    # outcome_sub_element_2 = outcome_sub_element_1.find_element('tag name', 'div')
    # parts2 = outcome_sub_element_2.find_elements('tag name', 'div')
    # print('Parts 2:')
    # for part in parts:
    #     print('part: ' + part.get_attribute('innerHTML'))

    
    outcome_label = ''
    # Moneyline
    if market == 'moneyline':
        outcome_label = parts[1].get_attribute('innerHTML').lower()

    else:# market == 'run line':
        # Run Line / Spread
        # label = div 1 + div 2
        part1 = parts[1].get_attribute('innerHTML').lower()
        print('\npart1: ' + part1)
        part2 = parts[2].get_attribute('innerHTML') # symbols/numbers dont lower
        print('part2: ' + part2)
        outcome_label = part1 + ' ' + part2

    # elif market == 'total':
    #     # label = div 1 + div 2
    #     part1 = parts[1].get_attribute('innerHTML').lower()
    #     print('\npart1: ' + part1)
    #     part2 = parts[2].get_attribute('innerHTML') # symbols/numbers dont lower
    #     print('part2: ' + part2)
    #     outcome_label = part1 + ' ' + part2


    #elif market == 'hits':

        
    print('\noutcome_label: ' + outcome_label)

    outcome_odds = parts[-1].get_attribute('innerHTML')
    print('outcome_odds: ' + outcome_odds)

    return outcome_label, outcome_odds

def read_market_odds(market, market_element, bet_dict):
    print('\n===Read Market Odds===\n')
    print('Input: market = ' + market)
    print('Input: bet_dict = ' + str(bet_dict))

    market_odds = ''

    bet_outcome = bet_dict['bet'].lower()
    print('bet_outcome: ' + bet_outcome)

    
    # === Player Props === 
    # separate outcomes if player prop
    # Check for specific player
    # ryne nelson - pitcher strikeouts
    # player_names = market.split(' - ')[0].split()
    # first_name = player_names[0]
    # last_name = player_names[1]
    # player_title = last_name + ', ' + first_name
    # print('player_title: ' + player_title)

    # outcomes = []
    # # cannot simply take all outcomes in market
    # # need all children to separate players by header
    # # get 2 columns 'KambiBC-outcomes-list__column'
    # market_columns = market_element.find_elements('class name', 'KambiBC-outcomes-list__column')
    # over_column = market_columns[0]
    # under_column = market_columns[1]
    # market_children = over_column.find_elements('xpath', './/*')
    # for child in market_children:
    #     print('\nMarket_child: ' + child.get_attribute('innerHTML'))

        # if header, use as key
        # if button, use as outcome

        # start at player name
        # stop at header or end

        
    

    # when it is grayed out NA disabled there is no odds section
    outcomes = market_element.find_elements('class name', 'KambiBC-betty-outcome')
    # see if given bet matches any of the outcomes
    
    for outcome in outcomes:

        outcome_label, outcome_odds = read_outcome_label(outcome, market)

        if outcome_label == bet_outcome:
            print('Found Outcome')
            outcome_disabled = outcome.get_attribute('disabled')
            print('outcome_disabled: ' + str(outcome_disabled))
            #if not re.search('disabled', outcome_class):
            # get odds if not disabled
            # disabled is none if not disabled
            if outcome_disabled is None:
                market_odds = outcome_odds #parts[-1].get_attribute('innerHTML')
            break

    
    # if not found bet in main lines
    # then search alternates
    alt_markets = ['run line', 'total runs']
    if market_odds == '' and market in alt_markets:
        # separate markets with only 1 option
        #if market != 'moneyline':
        # click Show list
        alt_btn = market_element.find_element('class name', 'KambiBC-outcomes-list__toggler-toggle-button')
        print('alt_btn: ' + alt_btn.get_attribute('innerHTML'))
        alt_btn.click()
        time.sleep(1)

        # get altered market element
        #print('\nMarket_element: ' + market_element.get_attribute('innerHTML'))
        # repeat check in outcomes list
        outcomes = market_element.find_elements('class name', 'KambiBC-betty-outcome')
        # see if given bet matches any of the outcomes
        
        for outcome in outcomes:

            outcome_label, outcome_odds = read_outcome_label(outcome, market)

            if outcome_label == bet_outcome:
                print('Found Outcome')
                outcome_disabled = outcome.get_attribute('disabled')
                print('outcome_disabled: ' + str(outcome_disabled))
                #if not re.search('disabled', outcome_class):
                # get odds if not disabled
                # disabled is none if not disabled
                if outcome_disabled is None:
                    market_odds = outcome_odds #parts[-1].get_attribute('innerHTML')
                break


    return market_odds

def read_market_section(market, website_name, pick_type):
    print('\n===Read Market Section===\n')
    print('Input: market = ' + market)
    print('Input: website_name = ' + website_name)
    print('\nOutput: market_title='', section_idx=0\n')

    section_idx = 0

    # need standard market for if statements
    # but need market title for each diff website
    market_title = market
    # if betrivers, team total
    # <team name> total -> Total Runs by <team name>
    # '[a-z]{3}\s[a-z]+\stotal'
    # space before total implies team total
    if website_name == 'betrivers':
        if re.search('\stotal', market):
            # section_name = 'team totals'
            section_idx = 2

            # oakland athletics -> oak athletics
            team_full_name = re.sub('\stotal', '', market).split()
            team_loc = team_full_name[0]
            loc_abbrev = converter.convert_team_loc_to_abbrev(team_loc, 'baseball')
            #team_name = team_full_name[1]
            team_name = loc_abbrev + ' ' + team_full_name[1]
            market_title = 'total runs by ' + team_name
        elif re.search('pitcher', market):
            # section_name = 'pitcher props'
            section_idx = 7

        elif pick_type == 'live':

            if re.search('run line|total runs', market):
                section_idx = 2


            

    print('market_title: ' + market_title)
    print('section_idx: ' + str(section_idx))
    return market_title, section_idx

def read_actual_odds(bet_dict, website_name, driver):
    print('\n===Read Actual Odds===\n')

    actual_odds = ''

    # get all categories on page
    # Betrivers:
    # Prematch:
    # -Most Popular
    # --Moneyline
    # --Run Line
    # --Total Runs
    # -Listed Pitcher
    # -Team Totals
    # --Total Runs
    # -Game Props
    # -Inning 1
    # -Innings
    # Live:
    # -Selected Markets
    # --Moneyline
    # --Run Line
    # --Total Runs
    # --Batter to record a Hit or Walk - Excluding Hit by Pitch
    # --Inning <#>
    # --Total Runs - Inning <#>
    # --Total Hits
    # --Result of Pitch Thrown
    # -Instant Betting
    # -Game Lines
    # -Innings
    # -Pitch by Pitch
    # -Batter Specials
    # -Races
    
    #selected_markets = ['moneyline', 'run line', 'total runs']

    section_idx = 0
    
    market = bet_dict['market'].lower()
    print('market: ' + market)

    market_title, section_idx = read_market_section(market, website_name)

    #offer_categories_element = driver.find_element('class', 'KambiBC-bet-offer-categories')
    sections = driver.find_elements('class name', 'KambiBC-bet-offer-category')
    # click if not expanded   
    # print('\nSections:') 
    # for section in sections:
    #     print('\nSection: ' + section.get_attribute('innerHTML'))
        
    if len(sections) > section_idx:
        section = sections[section_idx]
        #print('\nsection: ' + section.get_attribute('innerHTML'))
        # format makes it so it only opens but does not close with same element
        driver.execute_script("arguments[0].scrollIntoView(true);", section)
        section.click()
        print('\nOpened Section ' + str(section_idx))
        time.sleep(1)
            
        # Market
        found_offer = False
        markets = section.find_elements('class name', 'KambiBC-bet-offer-subcategory')
        # list_elements = section.find_elements('tag name', 'li')
        # alt_btns = section.find_elements('class name', 'KambiBC-outcomes-list__toggler-toggle-button')
        for market_idx in range(len(markets)):
            market_element = markets[market_idx]
            #list_element = list_elements[market_idx]
            #market = offer_categories[1]
            print('\nMarket_element: ' + market_element.get_attribute('innerHTML'))
            # print('\nouter market_element: ' + market_element.get_attribute('outerHTML'))
            # print('\nlist_element: ' + list_element.get_attribute('innerHTML'))
            # moneyline always first if available
            # but others might shift depending if moneyline or others are NA
            # so need to search for given offer in subcategory label
            offer_label = market_element.find_element('class name', 'KambiBC-bet-offer-subcategory__label').find_element('tag name', 'span').get_attribute('innerHTML').lower()
            print('\noffer_label: ' + offer_label)

            # easiest when = but not the case for player props
            if offer_label == market_title:
                print('Found Offer')
                found_offer = True

            # player props market label always has - with spaces on either side
            # KambiBC-outcomes-list__row-header KambiBC-outcomes-list__row-header--participant
            elif re.search(' - ', market):
                market_keyword = market.split(' - ')[1]
                market_keyword = re.sub('pitcher ', '', market_keyword)
                # if re.search('strikeout', market):
                #     keyword = keyword.split()[-1]
                print('market_keyword: ' + market_keyword)
                
                if re.search(market_keyword, offer_label):
                    print('Found Offer')
                    found_offer = True       


            if found_offer:
                actual_odds = read_market_odds(market, market_element, bet_dict)

                break # done after found market

    # find element by bet dict
    # first search for type element
    #offer_element = driver.find_element()

    print('actual_odds: ' + actual_odds)
    return actual_odds


website_name = 'betrivers'

# ensure actual odds match oddsview displayed odds
# open game page
#url = 'https://ny.betrivers.com/?page=sportsbook&feed=featured#home'
url = 'https://ny.betrivers.com/?page=sportsbook#event/1020374718'
#url = 'https://ny.betrivers.com/?page=sportsbook#event/live/1020374430'
driver = reader.open_react_website(url)

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


# before getting odds, need to login? 
# No, bc if not logged in and odds wrong then no need to login
# so if format changes after login, 
# need to make if statements for both formats
#logged_in = determine_logged_in(website_name)


# already on game page by default but error may need to start at sport page
# so we would need to include game in bet dict
# but first do simplest assume on game page
# Type: category we are looking for (eg moneyline, spread)
# Line: name of what you are betting on
# Odds: oddsview odds we are checking
bet_dict = {'market': 'run line', 'bet': 'chi cubs -4', 'odds': '-175'}
actual_odds = read_actual_odds(bet_dict, website_name, driver)

if actual_odds == bet_dict['odds']:
    # continue to place bet
    print('\nPlace Bet')
elif actual_odds == '':
    print('\nNo Bet')
else:
    print('\nOdds Mismatch')
    print('actual_odds: ' + actual_odds)
    print('init_odds: ' + bet_dict['odds'])

    # For EVs, need odds match so pass

    # For arbs, check arb cond
    # still check if |-odds1| < odds2

# Keep window open for manual testing
# click enter to move on
input('\nExit?')
print('Yes')
print('\nSave Cookies')
cookies = driver.get_cookies()
saved_cookies[website_name] = cookies
writer.write_json_to_file(saved_cookies, cookies_file)
print('Done')
exit()