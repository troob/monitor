# determine things

import converter, writer

import re, math
from datetime import datetime


# always player markets
# but accepts original market which includes player name
# also accepts market keyword
def determine_single_column_market(market, sport):

    #if re.search(' - ', market):
    #     market = market.split(' - ')[1]

    if re.search('home run', market):
        return True
    
    # ensure player points
    if sport == 'hockey':
        if market == 'point' or re.search(' - point', market):
            return True
    
    return False

def determine_valid_actual_odds(actual_odds, pick_odds, pick_type, driver, side_num, test, bet_dict):
    print('\n===Determine Valid Actual Odds===\n')
    print('pick_odds: ' + str(pick_odds))
    print('actual_odds: ' + str(actual_odds) + '\n')

    if pick_type == 'ev':
			
        # if not number, no bet
        # for now be specific to 'Closed' so we can see what else causes fail
        if actual_odds == None or actual_odds == 'Closed' or int(actual_odds) < int(pick_odds):
            if actual_odds == None or actual_odds == 'Closed':
                print('No Bet')
            # still accept better price
            else:
                print('Odds Mismatch')
                #print('actual_odds: ' + str(actual_odds) + '\n')
                actual_odds = None # invalid indicator

            writer.close_bet_windows(driver, side_num, test, bet_dict)

        else:
            # continue to place bet
            # First notify users before placing bet
            #print('\nPlace Bet or Find Limit')
            print('Valid Actual Odds, so continue to place EV bet\n')
    
    # if Arb, do not close unless gone or changed more than other side
    else:
        
        if actual_odds == None or actual_odds == 'Closed':
            print('No Bet')

            writer.close_bet_windows(driver, side_num, test, bet_dict)

        else:
            # continue to place bet
            # First notify users before placing bet
            print('Valid Actual Odds, so continue to find Arb limit\n')

    print('Actual Odds: ' + str(actual_odds) + '\n')
    # if actual_odds is not None:
    #     print('Valid Actual Odds: ' + str(actual_odds) + '\n')
    # else:
    #     print('Invalid Actual Odds: ' + str(actual_odds) + '\n')
    return actual_odds

def determine_window_idx(driver, side_num, arb, test):
    print('\n===Determine Window Idx===\n')
    print('side_num: ' + str(side_num))
    print('arb: ' + str(arb))

    window_idx = 0

    # Default window idx unless extra windows open
    num_monitor_windows = 2
    if test:
        num_monitor_windows = 1
    window_idx = num_monitor_windows # 1 or 2 currently based on desired manual testing setup we add 1 window on top of main monitor window
    if side_num == 2 and arb['actual odds1'] != '':
        window_idx = num_monitor_windows + 1

    source = arb['source1']
    if side_num == 2:
        source = arb['source2']

    init_num_windows = len(driver.window_handles)

    found_window = False
    while not found_window:

        if window_idx == init_num_windows:
            break

        print('Switch to Window Idx: ' + str(window_idx))
        driver.switch_to.window(driver.window_handles[window_idx])
        
        try:

            if source == 'betmgm':
                driver.find_element('tag name', 'vn-app')

            elif source == 'betrivers':
                driver.find_element('id', 'rsi-top-navigation')
                
            print('Found ' + source.title() + ' Window')
            found_window = True
                
        except:
            print('Not ' + source.title() + ' Window ' + str(window_idx))
            window_idx += 1
            print('Change to Window ' + str(window_idx))

        else:
            print('Unkown Source. Need to add source: ' + source)

    print('window_idx: ' + str(window_idx))
    return window_idx


def determine_half_auto(actual_odds1, actual_odds2):

    if actual_odds1 == '' and actual_odds2 != '':
        return True
    elif actual_odds1 != '' and actual_odds2 == '':
        return True
    else:
        return False
    
# if unsure of limit on certain markets
# be as safe as possible by
# using other side limit first
# BUT if do not know either side limit
# then use conservative limit based on similar markets
def determine_source_limit(source, market='', odds=''):
    print('\n===Determine Source Limit===\n')
    print('source: ' + source)
    print('market: ' + market)
    print('odds: ' + odds)
    print('\nOutput: limit = int\n')

    limit = 0

    big_markets = ['moneyline', 'home runs']

    if source == 'betmgm':
        limit = '$111' # actually $108.60
    elif source == 'betrivers':
        limit = '$333'
    elif source == 'draftkings':
        # time, league, market, side/odds
        # prematch, ncaaf, moneyline, unlikely +380: 10->50, win 40
        
        if market not in big_markets and int(odds) > -1000:
            limit = '$1111'

    elif source == 'caesars':
        # time, league, market, side/odds
        # prematch, ncaaf, moneyline, likely -365: 
        # - wager 900-940? -> 1147, to win 247+ (NEED to test wager $940 and win $250)
        # prematch, mlb, team total, likely -333:
        # - wager 90 to win 40

        # live, mlb, run line, likely -210:
        # - wager 900 to win 429
        # live, nfl, moneyline, likely -600:
        # - wager 1500-2000??? to win $250??? (TEST)
        # live, nfl, player prop, likely -121:
        # >135 to win >111 (TEST)
        # live, nhl, puck line, likely -190:
        # - wager 400?

        if market not in big_markets and int(odds) > -1000:
            limit = '$1111'

    # Fanduel
    # live, nfl, moneyline, likely -300:
    # - to win $1375
    # live, nfl, moneyline, unlikley +680:
     # - to win $2200



    print('limit: ' + limit)
    return limit

def determine_arb_bet_size(low_limit_payout, high_limit_odds, source):
    print('\n===Determine Arb Bet Size===\n')
    print('Input: low_limit_payout = float = ' + str(low_limit_payout))
    print('Input: high_limit_odds = int = ' + str(high_limit_odds))
    print('\nOutput: bet_size = float\n')

    high_limit_bet_size = 0

    # if high_limit_odds > 0:
    #     percent_odds = converter.round_half_up(100 / (high_limit_odds + 100) * 100, 1)
    # else:
    #     percent_odds = converter.round_half_up(high_limit_odds / (high_limit_odds - 100) * 100, 1)

    # bet size * odds = payout
    # => bet size = payout / odds
    high_limit_odds = converter.convert_american_to_decimal_odds(high_limit_odds)
    print('high_limit_odds: ' + str(high_limit_odds))

    high_limit_bet_size = converter.round_half_up(low_limit_payout / high_limit_odds, 2)

    # round based on source AND odds favored side
    # limited sources 2 decimals
    # partly limited sources round to whole number
    # unlimited sources:
    # - <100: round to 5
    # - <1000: round to 10
    # - <10000: round to 50
    high_limit_bet_size = converter.round_bet_size(high_limit_bet_size, source)

    print('high_limit_bet_size: ' + str(high_limit_bet_size))
    return high_limit_bet_size


def determine_arb_bet_sizes(arb):
    print('\n===Determine Arb Bet Sizes===\n')
    # print('Input: arb = {...} = ' + str(arb))
    # print('\nOutput: bet_size1, bet_size2 = float\n')

    bet1_limit = bet1_payout = None
    bet2_limit = bet2_payout = None

    bet1_odds = int(arb['odds1'])
    bet2_odds = int(arb['odds2'])

    # if half auto, use assumed odds on manual side
    # use auto side payout
    # if limit in arb keys then auto side
    if 'limit1' in arb.keys():
        bet1_limit = arb['limit1']
        bet1_payout = float(arb['payout1'])
        bet1_odds = int(arb['actual odds1'])
    if 'limit2' in arb.keys():
        bet2_limit = arb['limit2']
        bet2_payout = float(arb['payout2'])
        bet2_odds = int(arb['actual odds2'])

    print('Input: bet1_limit = ' + str(bet1_limit))
    print('Input: bet2_limit = ' + str(bet2_limit))
    print('Input: bet1_payout = ' + str(bet1_payout))
    print('Input: bet2_payout = ' + str(bet2_payout))
    print('Input: bet1_odds = ' + str(bet1_odds))
    print('Input: bet2_odds = ' + str(bet2_odds))

    # init both at limit
    # and then change lower payout side bet size
    bet1_size = bet1_limit
    bet2_size = bet2_limit

    bet1_source = arb['source1']
    bet2_source = arb['source2']

    # if side 1 is manual, use side 2 payout
    # to get side 1 bet size
    if bet1_limit is None:
        bet1_size = determine_arb_bet_size(bet2_payout, bet1_odds, bet1_source)
    elif bet2_limit is None:
        bet2_size = determine_arb_bet_size(bet1_payout, bet2_odds, bet2_source)

    else:

        # get side with smaller payout
        # smaller side stays same
        # and larger side must change to match
        #small_side_num = 1
        if bet2_payout < bet1_payout:
            #small_side_num = 2

            # lower large side to match small side payout
            # compute bet size needed to reach given payout at given odds
            bet1_size = determine_arb_bet_size(bet2_payout, bet1_odds, bet1_source)
        else:
            bet2_size = determine_arb_bet_size(bet1_payout, bet2_odds, bet2_source)

    print('bet1_size = ' + str(bet1_size))
    print('bet2_size = ' + str(bet2_size))
    return bet1_size, bet2_size


def determine_valid_hr_ev_arb(market, arb_source1, arb_source2):
    print('\n===Determine Valid HR EV Arb===\n')

    valid = False

    if re.search('home', market):
        print('Home Run Arb')

        # hr_under_sources = ['betrivers', 'betmgm']

        if arb_source1 == 'betmgm':
            valid_betmgm_hedges = ['fanduel']
            if arb_source2 in valid_betmgm_hedges:
                valid = True
            
        elif arb_source1 == 'betrivers':
            valid_betrivers_hedges = ['caesars', 'fanduel']
            if arb_source2 in valid_betrivers_hedges:
                valid = True
        
    return valid

# equal or matching keywords
def determine_matching_player_outcome(listed_name, listed_market, input_name, input_market):
    print('\n===Determine Matching Player Outcome===\n')
    print('listed_name: ' + listed_name)
    print('listed_market: ' + listed_market)
    print('input_name: ' + input_name)
    print('input_market: ' + input_market + '\n')

    # compare both listed and input names in same standard format
    # remove dashes, dots, accents, common words
    listed_name = converter.convert_name_to_standard_format(listed_name)
    input_name = converter.convert_name_to_standard_format(input_name)

    # listed market may be blank 
    # if unknown market title conversion
    if listed_market == '':
        print('\nERROR: Unknown market title so NEED to enable conversion!\n')
        return False

    match = False
    if listed_name == input_name or re.search(listed_name, input_name) or re.search(input_name, listed_name):
        if listed_market == input_market or re.search(listed_market, input_market) or re.search(input_market, listed_market):
            match = True

    if match:
        return True
    else:
        return False

# texas christian university -> tcu
# if name has 3 words in it, also test abbrev match if direct no direct match
def determine_matching_abbrev(bet_outcome_name, listed_name, league=''):
    print('\n===Determine Matching Abbrev===\n')
    print('bet_outcome_name: ' + bet_outcome_name)
    print('listed_name: ' + listed_name + '\n')

    # remove dash
    # texas - el paso
    bet_outcome_name = re.sub(' - ', ' ', bet_outcome_name)

    input_words = bet_outcome_name.split()

    if len(input_words) > 1: # or 2?
        abbrev = ''
        for word in input_words:
            abbrev += word[0]

        
        # cannot simply see if abbrv in listed name bc not correct
        # need to remove 'u' for university
        if listed_name == abbrev:# or abbrev in listed_name:
            print('Abbrev Match: ' + abbrev)
            return True
        elif listed_name[0] == 'u' and listed_name[1:] == abbrev:
            print('Abbrev Match: ' + abbrev)
            return True
        
        # try abbrev with u in front 
        # in case university removed from name earlier
        abbrev = 'u' + abbrev
        #print('try abbrev: ' + abbrev)
        if listed_name == abbrev:
            print('Abbrev Match: ' + abbrev)
            return True
        
        # louisiana monroe -> ul monroe
        abbrev = 'u' + input_words[0][0] + ' ' + input_words[1]  
        #print('try abbrev: ' + abbrev)
        if listed_name == abbrev:
            print('Abbrev Match: ' + abbrev)
            return True 
        
        # if name has state in it try abbrev all except state
        # north carolina state -> nc state
        if input_words[-1] == 'state':
            abbrev = ''
            for word in input_words[:-1]:
                abbrev += word[0]
            abbrev += ' ' + input_words[-1]
            #print('try abbrev: ' + abbrev)
            if listed_name == abbrev:
                print('Abbrev Match: ' + abbrev)
                return True

        # christian -> chrstn
        abbrev = re.sub('christian', 'chrstn', bet_outcome_name)
        if listed_name == abbrev:
            print('Abbrev Match: ' + abbrev)
            return True  

    
    
        
    return False

# equal or matching keywords
def determine_matching_outcome(outcome_label, bet_outcome):
    print('\n===Determine Matching Outcome===\n')
    print('Input: outcome_label: ' + outcome_label)
    print('Input: bet_outcome: ' + bet_outcome + '\n')
    #print('\nOutput: match = bool\n')

    # All
    # remove (...) unless player spread
    # bc 'who will win the most games in the match? (player spread)'
    if not re.search('player spread', outcome_label):
        outcome_label = re.sub(' \(.+\)', '', outcome_label)

    # Team Total
    # utep: team total points
    if re.search(':', outcome_label):
        listed_data = outcome_label.split(':')
        listed_name = listed_data[0] # 'utep'
        listed_market = listed_data[1] # ' team total points'

        bet_outcome_name = bet_outcome.split(listed_market)[0] # 'texas el paso'
        bet_outcome_market = bet_outcome.split(bet_outcome_name)[1] # ' team total points'

        print('bet_outcome_name: ' + bet_outcome_name)
        print('listed_name: ' + listed_name)
        print('bet_outcome_market: ' + bet_outcome_market)
        print('listed_market: ' + listed_market)

        if listed_name == bet_outcome_name or determine_matching_abbrev(listed_name, bet_outcome_name):
            print('Found Matching Name')
            if listed_market == bet_outcome_market:
                print('Found Matching Market')
                return True



    # split team name and spread 
    # in case team abbrev only used 1 side but also name not contained
    # if spread market, split spread name and num to match team abbrevs
    # both formats +0.5 and (0.5)
    elif re.search(' \+[0-9]| -[0-9]|[0-9]\)$', bet_outcome):
        bet_outcome_data = bet_outcome.rsplit(' ', 1)
        #bet_outcome_name = bet_outcome_data[0]
        # remove dash
        # texas - el paso
        bet_outcome_name = re.sub(' - ', ' ', bet_outcome_data[0])
        # add special \+ so it is not mistaken as 1 or more indicator
        bet_outcome_spread = re.sub('\+','\\+',bet_outcome_data[1])

        listed_data = outcome_label.rsplit(' ', 1)
        listed_name = listed_data[0]
        # remove extra letters from name, such as the 'u' in 'pittsburgh u'
        #listed_name = re.sub(' u', '', listed_name) already done in convert_bet_line_to_standard_format
        listed_spread = re.sub('\+','\\+',listed_data[1])

        print('bet_outcome_name: ' + bet_outcome_name)
        print('listed_name: ' + listed_name)
        print('bet_outcome_spread: ' + bet_outcome_spread)
        print('listed_spread: ' + listed_spread)

        
        if listed_name == bet_outcome_name or re.search(listed_name, bet_outcome_name) or re.search(bet_outcome_name, listed_name):
            # need exact match for spread
            if listed_spread == bet_outcome_spread:# or re.search(listed_spread, bet_outcome_spread) or re.search(bet_outcome_spread, listed_spread):
                return True
            
        # if name has 3 words in it, also test abbrev match if direct no direct match
        if determine_matching_abbrev(bet_outcome_name, listed_name):
            # need exact match for spread
            if listed_spread == bet_outcome_spread:# or re.search(listed_spread, bet_outcome_spread) or re.search(bet_outcome_spread, listed_spread):
                return True

    # o/u need exact match
    elif re.search('^under |^over |^yes$|^no$', bet_outcome):

        if outcome_label == bet_outcome:
            return True
        
        # if init attempt to match outcome label fails
        # try to convert format
        if bet_outcome == 'yes':
            bet_outcome = 'over 0.5'
        elif bet_outcome == 'no':
            bet_outcome = 'under 0.5'

        if outcome_label == bet_outcome:
            return True

        # only overs sometimes x+ format
        # over 2.5 -> 3+
        if re.search('over', bet_outcome):
            bet_line = str(math.ceil(float(bet_outcome.split('over ')[1])))
            print('bet_line: ' + bet_line)
            bet_outcome = bet_line + '+'

            if outcome_label == bet_outcome:
                return True
        
    elif outcome_label == bet_outcome or re.search(outcome_label, bet_outcome) or re.search(bet_outcome, outcome_label):
        return True
    
    # moneyline only?
    # texas christian university -> tcu
    elif determine_matching_abbrev(bet_outcome, outcome_label):
        return True
    


    # try removing 'alternate - '
    if re.search('alternate - ', bet_outcome):
        bet_outcome = re.sub('alternate - ', '', bet_outcome)
        if outcome_label == bet_outcome or re.search(outcome_label, bet_outcome) or re.search(bet_outcome, outcome_label):
            return True
    
    # after checking abbrev does not match
    # try match without university in name
    if re.search('university', bet_outcome):
        bet_outcome = re.sub('university of | university', '', bet_outcome)
        if outcome_label == bet_outcome or re.search(outcome_label, bet_outcome) or re.search(bet_outcome, outcome_label):
            return True
        
    # Input: outcome_label: club america mexico - total goals
    # Input: bet_outcome: america - total goals
    # split ' - ' and check both sides
    if re.search(' - ', bet_outcome) and re.search(' - ', outcome_label):
        outcome_label_data = re.split(' - ', outcome_label)
        outcome_label_name = outcome_label_data[0]
        outcome_label_market = outcome_label_data[1]

        bet_outcome_data = re.split(' - ', bet_outcome)
        bet_outcome_name = bet_outcome_data[0]
        bet_outcome_market = bet_outcome_data[1]

        # club america mexico -> america
        if re.search(bet_outcome_name, outcome_label_name) or re.search(outcome_label_name, bet_outcome_name):
            if outcome_label_market == bet_outcome_market:
                return True
    

    return False
    
# if EV, use optimal size
# if Arb, use maximum size
def determine_limit(bet_dict, website_name, pick_type, test):

    # === Find Limit === 
    # If EV, start with given wager size
    # If Arb, find limits on both sides
    bet_size = 0
    if not test and pick_type == 'ev':
        bet_size = converter.round_half_up(float(re.sub('\$','',bet_dict['size'])))
    else: # if arb
        # enter bet size into wager field
        # Test find limit with bet size guaranteed above limit
        # depends on source and market
        # for betrivers, $300 is max 
        # so if less than 300 available then need to set limits diff by market
        market = bet_dict['market']
        odds = bet_dict['actual odds']
        bet_size = determine_source_limit(website_name, market, odds)

    print('bet_size: ' + str(bet_size))
    return bet_size

def determine_game_year(game_date):
    print('\n===Determine Year===\n')
    print('Input: game_date = Jul 30 = ' + game_date)

    date_data = game_date.split(' ')
    game_mth = date_data[0]
    game_mth = converter.convert_month_abbrev_to_num(game_mth)
    cur_mth = datetime.month
    print('cur_mth: ' + str(cur_mth))
    cur_mth = datetime.strftime(cur_mth, '%b')
    print('cur_mth: ' + str(cur_mth))
    game_yr = datetime.year
    if game_mth < cur_mth:
        game_yr = str(int(game_yr) + 1)

    print('game_yr: ' + game_yr)
    return game_yr

# def determine_pick_min_val(pick, pick_type='ev'):

#     pick_market = pick['market']
    

#     # Oneil Cruz - Runs -> Runs
#     # bc home runs not included so need exact match
#     pick_market_group = ''
#     if re.search('-', pick_market):
#         pick_market_group = pick_market.split(' - ')[1]

#     # if prev arb val already greater than min val we already took prop so do not double take
#     min_val = 0.2

#     # === Valid EVs ===
#     ev_hit_min_val = 2
#     ev_small_market_min_val = 1 # % tune min val
#     ev_big_market_min_val = 0.3
#     ev_likely_hr_min_val = 0.8 # -2500 or lower
#     # for less likely cases, require higher val???
#     ev_ideal_min_val = 2 # if unlimited bankroll, what is ideal min val?
#     ev_likely_odds = -275 # this or less is considered likely??? no bc it should be gradient???


#     # >-275 odds need 2% min val as well
#     # min val sep by class
#     if pick_type == 'arb':
#         min_val = 0.3
#         limited_sources = ['betrivers', 'fanatics', 'betmgm']
#         if pick['source1'] in limited_sources or pick['source2'] in limited_sources:
#             min_val = 2
    
#     else:

#         pick_odds = int(pick['odds'])

#         # AVOID below val tuned to max profit
#         # Big markets
#         # take homers at -5000 w/ 0.3% val
#         if re.search('Home', pick_market) and pick_odds <= -5000:
#             min_val = ev_big_market_min_val # 0.3%

#         elif re.search('Home', pick_market) and pick_odds <= -3100:
#             min_val = ev_likely_hr_min_val # 0.8%
        
#         elif re.search('Moneyline|Spread|Total', pick_market):
#             min_val = ev_big_market_min_val # 0.3%
#         # batter hits and runs
#         elif re.search('Hit|RBI|Single|Double|Triple', pick_market) or pick_market_group == 'Runs': 
#             min_val = ev_hit_min_val # 2%
        
#         # this always runs if no specific exception yet???
#         # no bc if passed this far will have smaller ev so skip
#         # small markets
#         else:
#             min_val = ev_small_market_min_val # 1%

#     #print('min_val: ' + str(min_val))
#     return min_val


# Bets placed in middle of night early morning are in diff category
# bc they have skewed values
# possibly wrong readings bc other sources show odds but bets suspended so not real odds
# or just skewed init odds
def determine_min_pick_val(pick, pick_type='ev'):
    #print('\n===Determine Min Pick Val===\n')

    min_pick_val = 0.3 # absolute min to get any val???

    if pick_type == 'arb':
        return min_pick_val

    # >-275 odds need 2% min val as well
    # min val sep by class
    # === EV ===
    if 'odds' in pick.keys(): 
        pick_market = pick['market'].lower()
        pick_odds = int(pick['odds'])
        pick_source = pick['source']
        pick_bet = pick['bet'].lower()
        pick_sport = pick['sport']

        # Oneil Cruz - Runs -> Runs
        # bc home runs not included so need exact match
        pick_market_group = ''
        if re.search(' - ', pick_market):
            pick_market_group = pick_market.split(' - ')[1]

        # Make a list of the required min val for each range of odds
        # AVOID below val tuned to max profit

        if pick_sport == 'football':

            if pick_market == 'moneyline':

                # -inf < x <= -501
                if pick_odds <= -501:
                    return 0.3
                
                # -500 <= x <= -276
                if pick_odds <= -276:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.5, 0.9
                    else:
                        return 0.3
                
                # -275 <= x <= -261
                if pick_odds <= -261:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.5, 0.9
                    else:
                        return 0.3
                
                # -260 <= x <= -241
                if pick_odds <= -241:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.5, 0.9
                    elif pick_source == 'fanatics':
                        return 0.4 # 0.8
                    else:
                        return 0.3
                
                # -240 <= x <= -211
                elif pick_odds <= -211:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.5, 0.9
                    elif pick_source == 'fanatics':
                        return 0.5 # 1
                    else:
                        return 0.3
                    
                # -210 <= x <= -176
                elif pick_odds <= -176:
                    if pick_source == 'betmgm':
                        return 0.5 # 1.1
                    elif pick_source == 'fanatics':
                        return 0.5 # 1
                    else:
                        return 0.3
                    
                # -175 <= x < inf
                else:
                    if pick_source == 'betmgm':
                        return 0.5 # 1.1
                    elif pick_source == 'fanatics':
                        return 0.6 # 0.8
                    else:
                        return 0.3


            
            elif re.search('half moneyline', pick_market):

                # -inf < x <= -1201
                if pick_odds <= -1201:
                    return 0.3
                
                # -1200 <= x <= -376
                if pick_odds <= -376:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.4
                    else:
                        return 0.3
                    
                # -375 <= x <= -251
                if pick_odds <= -251:
                    if pick_source == 'betmgm':
                        return 0.5 # 0.6
                    else:
                        return 0.3
                    
                # -250 <= x <= -201
                if pick_odds <= -201:
                    if pick_source == 'betmgm':
                        return 0.6 # 0.8
                    else:
                        return 0.3
                    
                # -200 <= x <= -179
                if pick_odds <= -179:
                    if pick_source == 'betmgm':
                        return 0.7 # 0.9
                    else:
                        return 0.3
                    
                # -180 <= x <= -171
                if pick_odds <= -171:
                    if pick_source == 'betmgm':
                        return 0.7 # 0.9
                    elif pick_source == 'fanatics':
                        return 0.4 # 0.7
                    else:
                        return 0.3
                    
                # -170 <= x <= -151
                if pick_odds <= -151:
                    if pick_source == 'betmgm':
                        return 0.7 # 0.9
                    elif pick_source == 'fanatics':
                        return 0.5 # 1.6
                    else:
                        return 0.3
                
                # -150 <= x < inf
                else:
                    if pick_source == 'betmgm':
                        return 0.8 # 1.1
                    elif pick_source == 'fanatics':
                        return 0.5 # 1.6
                    else:
                        return 0.3
                    
            elif re.search('quarter moneyline', pick_market):

                # -inf < x <= -171
                if pick_odds <= -171:
                    return 0.3
                
                # -170 x <= +104
                if pick_odds <= 104:
                    if pick_source == 'fanatics':
                        return 2.3
                    else:
                        return 0.3
                
                # +105 <= x < inf
                else:
                    if pick_source == 'fanatics':
                        return 2.3
                    else:
                        return 0.3

            elif pick_market == 'spread':

                # Plus
                if re.search('\+', pick_bet):

                    # -inf < x <= -426
                    if pick_odds <= -426:
                        return 0.3
                    
                    # -425 <= x <= -241
                    if pick_odds <= -241:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.7
                        else:
                            return 0.3
                    
                    # -240 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.5 # 0.8
                        else:
                            return 0.3
                
                # Minus
                else:
                    # -inf < x <= +104
                    if pick_odds <= 104:
                        return 0.3
                    
                    # +105 <= x <= +124
                    elif pick_odds <= 124:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.6, 2
                        else:
                            return 0.3

                    # +125 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3
                        

            elif re.search('half spread', pick_market):

                # == + ==
                if re.search('\+', pick_bet):
                    
                    # -inf < x <= -126
                    if pick_odds <= -126:
                        return 0.3
                    
                    # -125 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 1.3
                        else:
                            return 0.3

                # == - ==
                else:
                    # -inf < x <= -121
                    if pick_odds <= -121:
                        return 0.3
                    
                    # -120 x <= +109
                    if pick_odds <= 109:
                        if pick_source == 'betrivers':
                            return 1.1
                        else:
                            return 0.3
                    
                    # +110 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 1.1
                        elif pick_source == 'fanatics':
                            return 1.5
                        else:
                            return 0.3
                        
            elif re.search('quarter spread', pick_market):

                # == + ==
                if re.search('\+', pick_bet):
                    
                    # -inf < x <= -181
                    if pick_odds <= -181:
                        return 0.3
                    
                    # -180 <= x <= -101
                    elif pick_odds <= -101:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.2
                        else:
                            return 0.3

                    # +100 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'fanatics':
                            return 0.5 # 2.3
                        else:
                            return 0.3
                        
                    # +110 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.6 # 1.3, 3.4 # big jump but could be warranted so get more samples
                        else:
                            return 0.3

                # == - ==
                else:
                    # -inf < x <= +139
                    if pick_odds <= 139:
                        return 0.3
                    
                    # +140 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.4 # 4.3 # Big Jump
                        else:
                            return 0.3
                        

            elif pick_market == 'total':

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= -401
                    if pick_odds <= -401:
                        return 0.3
                    
                    # -400 <= x <= -116
                    if pick_odds <= -116:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.7
                        else:
                            return 0.3
                    
                    # -115 <= x <= +104
                    if pick_odds <= 104:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.7
                        elif pick_source == 'fanatics':
                            return 0.4 # 2.7 big jump
                        else:
                            return 0.3
                    
                    # +105 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.7
                        elif pick_source == 'fanatics':
                            return 0.4 # 2.7 big jump
                        else:
                            return 0.3

                # == Unders ==
                else:
                    
                    return 0.3
                
            # quarter total
            elif re.search('quarter total', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= -106
                    if pick_odds <= -106:
                        return 0.3
                    
                    # -105 <= x <= -101
                    if pick_odds <= -101:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.2 jump
                        else:
                            return 0.3
                    
                    # +100 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.2 jump
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.3 jump
                        else:
                            return 0.3

                    # +105 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.2 jump
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.4, 2.1
                        else:
                            return 0.3

                # == Unders ==
                else:
                    # -inf < x <= +129
                    if pick_odds <= 129:
                        return 0.3
                    
                    # +130 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.3 jump
                        else:
                            return 0.3

            # quarter Team total  
            elif re.search('quarter .+ total', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    return 0.3

                # == Unders ==
                else:
                    
                    # -inf < x <= +104
                    if pick_odds <= 104:
                        return 0.3

                    # +105 <= x <= +119
                    if pick_odds <= 119:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.9
                        else:
                            return 0.3
                    
                    # +120 <= x <= +124
                    if pick_odds <= 124:
                        if pick_source == 'fanatics':
                            return 0.5 # 3.1 jump
                        else:
                            return 0.3
                        
                    # +125 <= x <= +139
                    if pick_odds <= 139:
                        if pick_source == 'fanatics':
                            return 0.5 # 3.1 jump
                        else:
                            return 0.3
                    
                    # +140 <= x <= +144
                    elif pick_odds <= 144:
                        if pick_source == 'fanatics':
                            return 0.5 # 3.1 jump
                        else:
                            return 0.3
                        
                    # +145 <= x <= +149
                    elif pick_odds <= 149:
                        if pick_source == 'fanatics':
                            return 0.6 # 2.3
                        else:
                            return 0.3
                        
                    # +150 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.7 # 4.5 jump
                        else:
                            return 0.3
                
            # half total  
            elif re.search('half total', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= +109
                    if pick_odds <= 109:
                        return 0.3
                    
                    # +110 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.9 jump
                        else:
                            return 0.3

                # == Unders ==
                else:
                    
                    return 0.3
                
            # half Team total  
            elif re.search('half .+ total', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    return 0.3

                # == Unders ==
                else:
                    
                    # -inf < x <= +129
                    if pick_odds <= 129:
                        return 0.3
                    
                    # +130 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.5
                        else:
                            return 0.3
                        
            # Team total  
            elif re.search('\stotal', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= -241
                    if pick_odds <= -241:
                        return 0.3
                    
                    # -240 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'fanatics':
                            return 0.4 # 2.2 jump
                        else:
                            return 0.3
                        
                    # +110 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3  

                # == Unders ==
                else:
                    # -inf < x <= -201
                    if pick_odds <= -201:
                        return 0.3
                    
                    # -200 <= x <= -171
                    elif pick_odds <= -171:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.8
                        else:
                            return 0.3
                        
                    # -170 <= x <= -166
                    elif pick_odds <= -166:
                        if pick_source == 'fanatics':
                            return 0.5 # 2.5
                        else:
                            return 0.3

                    # -165 <= x <= -161
                    elif pick_odds <= -161:
                        if pick_source == 'fanatics':
                            return 0.6 # 0.8
                        else:
                            return 0.3
                        
                    # -160 <= x <= -121
                    elif pick_odds <= -121:
                        if pick_source == 'fanatics':
                            return 0.7 # 0.7
                        else:
                            return 0.3
                        
                    # -120 <= x <= -116
                    elif pick_odds <= -116:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.7 # 0.7
                        else:
                            return 0.3

                    # -115 <= x <= -106
                    elif pick_odds <= -106:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.7 # 0.7
                        else:
                            return 0.3
                        
                    # -105 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.8 # 1.9
                        else:
                            return 0.3

                    # +105 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.4
                        elif pick_source == 'fanatics':
                            return 1 # 2, 2.1, 2.3
                        else:
                            return 0.3
                        

            elif pick_market_group == 'touchdowns':

                # Over
                if re.search('o', pick_bet):

                    # -inf < x <= +104
                    if pick_odds <= 104:
                        return 0.3
                    
                    # +105 <= x <= +154
                    if pick_odds <= 154:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.9, 2.2
                        else:
                            return 0.3
                    
                    # +155 <= x <= +474
                    elif pick_odds <= 474:
                        if pick_source == 'fanatics':
                            return 0.5 # 3.7
                        else:
                            return 0.3
                        
                    # +475 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.6 # 5.1
                        else:
                            return 0.3
                
                # Under
                else:
                    return 0.3

            elif pick_market_group == 'passing touchdowns':

                # Over
                if re.search('o', pick_bet):

                    # -inf < x <= -116
                    if pick_odds <= -116:
                        return 0.3
                    
                    # -115 <= x <= +104:
                    if pick_odds <= 104:
                        if pick_source == 'fanatics':
                            return 0.4 # 2.4
                        else:
                            return 0.3
                        
                    # +105 <= x <= +119:
                    if pick_odds <= 119:
                        if pick_source == 'fanatics':
                            return 0.5 # 3.7
                        else:
                            return 0.3
                        
                    # +120 <= x <= +164:
                    if pick_odds <= 164:
                        if pick_source == 'fanatics':
                            return 0.6 # 3.6
                        else:
                            return 0.3
                        
                    # +165 <= x <= +199:
                    if pick_odds <= 199:
                        if pick_source == 'fanatics':
                            return 0.7 # 2.7
                        else:
                            return 0.3
                    
                    # +200 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.8 # 2, 4.8
                        else:
                            return 0.3
                
                # Under
                else:
                    # -inf < x <= -131
                    if pick_odds <= -131:
                        return 0.3
                    
                    # -130 <= x <= +139
                    if pick_odds <= 139:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.3 jump
                        else:
                            return 0.3
                    
                    # +140 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.5 # 2 jump
                        else:
                            return 0.3
                        
            elif pick_market_group == 'passing yards':

                # Over
                if re.search('o', pick_bet):
                    # -inf < x <= +119
                    if pick_odds <= 119:
                        return 0.3
                    
                    # +120 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 5.6
                        else:
                            return 0.3
                
                # Under
                else:
                    return 0.3
                        
            elif pick_market_group == 'receiving yards':

                # Over
                if re.search('o', pick_bet):
                    # -inf < x <= +104
                    if pick_odds <= 104:
                        return 0.3

                    # +105 <= x <= +109
                    if pick_odds <= 109:
                        if pick_source == 'betmgm':
                            return 0.4 # 4
                        else:
                            return 0.3
                    
                    # +110 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.5 # 2
                        else:
                            return 0.3
                
                # Under
                else:
                    # -inf < x <= +104
                    if pick_odds <= 104:
                        return 0.3
                    
                    # +105 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.5, 2.9
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.4, 1.5, 1.6
                        else:
                            return 0.3
                        

            elif pick_market_group == 'receptions made':

                # Over
                if re.search('o', pick_bet):
                    # -inf < x <= -121
                    if pick_odds <= -121:
                        return 0.3
                    
                    # -120 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.1 jump
                        else:
                            return 0.3
                        
                    # +110 <= x <= +154
                    elif pick_odds <= 154:
                        if pick_source == 'betmgm':
                            return 0.4 # 5.1 jump
                        elif pick_source == 'betrivers':
                            return 0.5 # 1.9
                        else:
                            return 0.3
                        
                    # +155 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 5.1 jump
                        elif pick_source == 'betrivers':
                            return 0.6 # 5.1
                        else:
                            return 0.3
                
                # Under
                else:
                    
                    # -inf < x <= -119
                    if pick_odds <= -119:
                        return 0.3

                    # -118 <= x <= +109
                    if pick_odds <= 109:
                        if pick_source == 'betrivers':
                            return 0.4 # 2.8
                        else:
                            return 0.3
                    
                    # +110 <= x <= +114
                    if pick_odds <= 114:
                        if pick_source == 'betrivers':
                            return 0.5 # 1.3
                        else:
                            return 0.3
                        
                    # +115 <= x <= +127
                    if pick_odds <= 127:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.3
                        elif pick_source == 'betrivers':
                            return 0.5 # 1.3
                        else:
                            return 0.3
                    
                    # +128 <= x <= +154
                    elif pick_odds <= 154:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.3
                        elif pick_source == 'betrivers':
                            return 0.6 # 4.6
                        else:
                            return 0.3
                        
                    # +155 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.3
                        elif pick_source == 'betrivers':
                            return 0.7 # 5.2
                        else:
                            return 0.3

            elif pick_market_group == 'longest reception':

                # Over
                if re.search('o', pick_bet):

                    # -inf < x <= -101
                    if pick_odds <= -101:
                        return 0.3
                    
                    # +100 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 3.3
                        else:
                            return 0.3
                
                # Under
                else:
                    
                    return 0.3
                        
            elif pick_market_group == 'rushing yards':

                # Over
                if re.search('o', pick_bet):
                    # -inf < x <= -111
                    if pick_odds <= -111:
                        return 0.3
                    
                    # -110 <= x <= -101
                    if pick_odds <= -101:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                    
                    # +100 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.5
                        else:
                            return 0.3
                        
                    # +105 <= x <= +114
                    elif pick_odds <= 114:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.5
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                        
                    # +115 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.6 # 4.2
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                
                # Under
                else:
                    # -inf < x <= -101
                    if pick_odds <= -101:
                        return 0.3

                    # +100 <= x <= +104
                    if pick_odds <= 104:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.5
                        else:
                            return 0.3
                        
                    # +105 <= x <= +109
                    if pick_odds <= 109:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.9
                        else:
                            return 0.3
                    
                    # +110 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.6 # 2, 2.2
                        else:
                            return 0.3
                        
            elif pick_market_group == 'rushing attempts':

                # Over
                if re.search('o', pick_bet):

                    # -inf < x <= -106
                    if pick_odds <= -106:
                        return 0.3
                    
                    # -105 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.3
                        else:
                            return 0.3
                
                # Under
                else:
                    
                    return 0.3
                        

        elif pick_sport == 'hockey':

            if pick_market == 'spread':

                # Plus
                if re.search('\+', pick_bet):

                    # -inf < x <= -551
                    if pick_odds <= -551:
                        return 0.3
                    
                    # -550 <= x <= -451
                    if pick_odds <= -451:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.7
                        else:
                            return 0.3
                    
                    # -450 <= x <= -351
                    elif pick_odds <= -351:
                        
                        if pick_source == 'betmgm':
                            return 0.5 # 0.6
                        else:
                            return 0.3

                    # -350 <= x <= -276
                    elif pick_odds <= -276:
                        
                        if pick_source == 'betmgm':
                            return 0.6 # 1.6
                        else:
                            return 0.3
                        
                    # -275 <= x <= -226
                    elif pick_odds <= -226:
                        
                        if pick_source == 'betmgm':
                            return 0.7 # 0.6, 0.9
                        else:
                            return 0.3
                        
                    # -225 <= x <= -211
                    elif pick_odds <= -211:
                        
                        if pick_source == 'betmgm':
                            return 0.8 # 2.6
                        else:
                            return 0.3
                        
                    # -210 <= x < inf
                    else:
                        
                        if pick_source == 'betmgm':
                            return 0.9 # 1.5
                        else:
                            return 0.3
                        
                # Minus
                else:

                    # -inf < x <= -126
                    if pick_odds <= -126:
                        return 0.3
                    
                    # -125 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1
                        else:
                            return 0.3
                    
            elif pick_market_group == 'assists':

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= +124
                    if pick_odds <= 124:
                        return 0.3
                    
                    # +125 <= x <= +149
                    if pick_odds <= 149:
                        if pick_source == 'fanatics':
                            return 0.4 # 3.7, 6.2
                        else:
                            return 0.3
                    
                    # +150 <= x <= +174
                    if pick_odds <= 174:
                        if pick_source == 'fanatics':
                            return 0.5 # 1.7, 4.6
                        else:
                            return 0.3

                    # +175 <= x <= +199
                    elif pick_odds <= 199:
                        if pick_source == 'fanatics':
                            return 0.6 # 2.3
                        else:
                            return 0.3

                    # +200 <= x <= +224
                    elif pick_odds <= 224:
                        if pick_source == 'fanatics':
                            return 0.7 # 2.4, 4.7
                        else:
                            return 0.3
                        
                    # +225 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.8 # 5.4
                        else:
                            return 0.3

                else:
                    return 0.3
                
            elif pick_market_group == 'goals':

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= +137
                    if pick_odds <= 137:
                        return 0.3
                    
                    # +138 <= x <= +144
                    if pick_odds <= 144:
                        if pick_source == 'betrivers':
                            return 0.4 # 7.1
                        else:
                            return 0.3
                        
                    # +145 <= x <= +154
                    if pick_odds <= 154:
                        if pick_source == 'betmgm':
                            return 0.4 # 6.3
                        elif pick_source == 'betrivers':
                            return 0.4 # 7.1
                        else:
                            return 0.3

                    # +155 <= x <= +194
                    if pick_odds <= 194:
                        if pick_source == 'betmgm':
                            return 0.4 # 6.3
                        elif pick_source == 'betrivers':
                            return 0.5 # 7
                        else:
                            return 0.3
                        
                    # +195 <= x <= +199
                    if pick_odds <= 199:
                        if pick_source == 'betmgm':
                            return 0.4 # 6.3
                        elif pick_source == 'betrivers':
                            return 0.6 # 4.4
                        else:
                            return 0.3

                    # +200 <= x <= +214
                    if pick_odds <= 214:
                        if pick_source == 'betrivers':
                            return 0.7 # 2.6
                        elif pick_source == 'betmgm':
                            return 0.4 # 2.6
                        else:
                            return 0.3

                    # +215 <= x <= +219
                    if pick_odds <= 219:
                        if pick_source == 'betrivers':
                            return 0.8 # 4.1
                        elif pick_source == 'betmgm':
                            return 0.4 # 2.6
                        else:
                            return 0.3
                        
                    # +220 <= x <= +239
                    if pick_odds <= 239:
                        if pick_source == 'betrivers':
                            return 0.8 # 4.1
                        elif pick_source == 'betmgm':
                            return 0.5 # 5.8
                        else:
                            return 0.3
                        
                    # +240 <= x <= +264
                    if pick_odds <= 264:
                        if pick_source == 'betrivers':
                            return 0.9 # 4.9
                        elif pick_source == 'betmgm':
                            return 0.5 # 5.8
                        else:
                            return 0.3
                        
                    # +265 <= x <= +279
                    if pick_odds <= 279:
                        if pick_source == 'betrivers':
                            return 1 # 5.2
                        elif pick_source == 'betmgm':
                            return 0.5 # 5.8
                        else:
                            return 0.3
                    
                    # +280 <= x <= +349
                    if pick_odds <= 349:
                        if pick_source == 'betrivers':
                            return 1.1 # 3.8
                        elif pick_source == 'betmgm':
                            return 0.5 # 5.8, 6.2
                        else:
                            return 0.3

                    # +350 <= x <= +359
                    if pick_odds <= 359:
                        if pick_source == 'betrivers':
                            return 1.2 # 3.9
                        elif pick_source == 'betmgm':
                            return 0.5 # 5.8, 6.2
                        else:
                            return 0.3
                        
                    # +360 <= x <= +399
                    if pick_odds <= 399:
                        if pick_source == 'betrivers':
                            return 1.2 # 3.9
                        elif pick_source == 'betmgm':
                            return 0.6 # 4.5
                        else:
                            return 0.3
                        
                    # +400 <= x <= +459
                    if pick_odds <= 459:
                        if pick_source == 'betrivers':
                            return 1.2 # 3.9
                        elif pick_source == 'betmgm':
                            return 0.7 # 6.3
                        else:
                            return 0.3
                        
                    # +460 <= x <= +499
                    if pick_odds <= 499:
                        if pick_source == 'betrivers':
                            return 1.3 # 6.6
                        elif pick_source == 'betmgm':
                            return 0.7 # 6.3
                        else:
                            return 0.3
                    
                    # +500 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 1.3 # 6.6
                        elif pick_source == 'betmgm':
                            return 0.7 # 6.3
                        elif pick_source == 'fanatics':
                            return 0.4 # 6.8
                        else:
                            return 0.3

                else:
                    return 0.3

            elif pick_market_group == 'shots':

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= -137
                    if pick_odds <= -137:
                        return 0.3
                    
                    # -136 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 3.2
                        else:
                            return 0.3

                # under
                else:
                    # -inf < x <= -158
                    if pick_odds <= -158:
                        return 0.3
                    
                    # -157 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 2.3
                        else:
                            return 0.3
                    
            elif pick_market == 'total':

                # == Overs ==
                if re.search('o', pick_bet):
                    # -inf < x <= +117
                    if pick_odds <= 117:
                        return 0.3

                    # +118 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.3
                        else:
                            return 0.3

                # == Unders ==
                else:
                    # -inf < x <= +109
                    if pick_odds <= 109:
                        return 0.3

                    # +110 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.8
                        else:
                            return 0.3

            # period total
            elif re.search('period total', pick_market):  

                return 0.3
            
            # period team total
            elif re.search('period .+ total', pick_market):  

                return 0.3
             
            # team total
            elif re.search('\stotal', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    return 0.3

                # == Unders ==
                else:
                    # -inf < x <= -401
                    if pick_odds <= -401:
                        return 0.3

                    # -400 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                        

        elif pick_sport == 'soccer':

            if pick_market == 'moneyline':
                
                # -inf < x <= -301
                if pick_odds <= -301:
                    return 0.3
                
                # -300 <= x <= -276
                if pick_odds <= -276:
                    if pick_source == 'betmgm':
                        return 0.4 # 1.2
                    else:
                        return 0.3
                
                # -275 <= x <= -211
                if pick_odds <= -211:
                    if pick_source == 'betmgm':
                        return 0.5 # 0.8
                    else:
                        return 0.3
                
                # -210 <= x <= -191
                elif pick_odds <= -191:
                    if pick_source == 'betmgm':
                        return 0.6 # 0.7
                    else:
                        return 0.3

                # -190 <= x <= -166
                elif pick_odds <= -166:
                    if pick_source == 'betmgm':
                        return 0.6 # 0.7
                    else:
                        return 0.3
                    
                # -165 <= x <= -146
                elif pick_odds <= -146:
                    if pick_source == 'betmgm':
                        return 0.7 # 0.8
                    else:
                        return 0.3
                    
                # -145 <= x <= +169
                elif pick_odds <= 169:
                    if pick_source == 'betmgm':
                        return 0.8 # 1.1
                    else:
                        return 0.3
                    
                # +170 <= x <= +349
                elif pick_odds <= 349:
                    if pick_source == 'betmgm':
                        return 0.8 # 1.1
                    elif pick_source == 'betrivers':
                        return 0.4 # 3
                    else:
                        return 0.3
                    
                # Draw, consider separating
                # +350 <= x < inf
                else: #
                    if pick_source == 'betmgm':
                        return 0.8 # 1.1
                    elif pick_source == 'betrivers':
                        return 0.5 # 5.4
                    else:
                        return 0.3
                
            # just Spread
            elif pick_market == 'spread':

                # need to search for + not - bc - might be in name?
                # no actually should not be in name bc team names dont usually have dashes but they could

                # == + ==
                if re.search('\+', pick_bet):

                    # -inf < x <= -551
                    if pick_odds <= -551:
                        return 0.3

                    # -550 <= x <= -189
                    elif pick_odds <= -189:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.9 jump
                        else:
                            return 0.3
                        
                    # -190 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'fanatics':
                            return 0.5 # 2.8 jump
                        else:
                            return 0.3

                    # +105 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.6 # 3.2
                        else:
                            return 0.3
                        
                # == - ==
                else:
                    
                    return 0.3

                
            elif pick_market == 'total':

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= -5001
                    if pick_odds <= -5001:
                        return 0.3

                    # -5000 x <= -2501
                    if pick_odds <= -2501:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.4
                        else:
                            return 0.3
                        
                    # -2500 <= x <= -1401
                    if pick_odds <= -1401:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.4
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.6
                        else:
                            return 0.3
                        
                    # -1400 <= x <= -351
                    elif pick_odds <= -351:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.4
                        elif pick_source == 'fanatics':
                            return 0.5 # 0.7
                        else:
                            return 0.3
                        
                    # -350 <= x <= -261
                    elif pick_odds <= -261:
                        if pick_source == 'betmgm':
                            return 0.5 # 2.2 
                        elif pick_source == 'fanatics':
                            return 0.5 # 0.7
                        else:
                            return 0.3
                        
                    # -260 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.5 # 2.2 
                        elif pick_source == 'fanatics':
                            return 0.5 # 0.7
                        else:
                            return 0.3

                # == Unders ==
                else:
                    
                    # -inf < x <= -3501
                    if pick_odds <= -3501:
                        return 0.3
                    
                    # -3500 <= x <= -2501
                    if pick_odds <= -2501:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.5
                        else:
                            return 0.3
                    
                    # -2500 <= x <= -2001
                    if pick_odds <= -2001:
                        if pick_source == 'fanatics':
                            return 0.5 # 0.5
                        else:
                            return 0.3
                        
                    # -2000 <= x <= -1701
                    if pick_odds <= -1701:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.5 # 0.5
                        else:
                            return 0.3

                    # -1700 <= x <= -1301
                    if pick_odds <= -1301:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.6 # 1
                        else:
                            return 0.3
                    
                    # -1300 <= x <= -1101
                    elif pick_odds <= -1101:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.7 # 1, 1.2
                        else:
                            return 0.3
                        
                    # -1100 <= x <= -801
                    elif pick_odds <= -801:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.8 # 1.1 jump
                        else:
                            return 0.3
                    
                    # -800 <= x <= -611
                    elif pick_odds <= -611:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.9 # 1.2 jump
                        else:
                            return 0.3
                    
                    # -610 <= x <= -551
                    elif pick_odds <= -551:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.9 # 1.2 jump
                        else:
                            return 0.3

                    # -550 <= x <= -351
                    elif pick_odds <= -211:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 1 # 2.2
                        else:
                            return 0.3

                    # -350 <= x <= -301
                    elif pick_odds <= -301:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 1 # 2.2
                        else:
                            return 0.3
                        
                    # -300 <= x <= -211
                    elif pick_odds <= -211:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.5
                        elif pick_source == 'fanatics':
                            return 1 # 2.2
                        else:
                            return 0.3
                    
                    # -210 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.5
                        elif pick_source == 'fanatics':
                            return 1 # 2.2
                        else:
                            return 0.3
                        
                    # +105 <= x <= +259
                    elif pick_odds <= 259:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.5
                        elif pick_source == 'fanatics':
                            return 1.1 # 2
                        else:
                            return 0.3
                        
                    # +260 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.5
                        elif pick_source == 'betrivers':
                            return 0.4 # 5.2
                        elif pick_source == 'fanatics':
                            return 1.1 # 2
                        else:
                            return 0.3


            elif re.search('half total', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= -251
                    if pick_odds <= -251:
                        return 0.3
                    
                    # -250 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.9
                        else:
                            return 0.3

                    # +110 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.9
                        elif pick_source == 'fanatics':
                            return 0.4 # 3
                        else:
                            return 0.3

                # == Unders ==
                else:
                    
                    # -inf < x <= +104
                    if pick_odds <= 104:
                        return 0.3
                    
                    # +105 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.4 # 2.2
                        else:
                            return 0.3

            elif re.search('half .+ total', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= +129
                    if pick_odds <= 129:
                        return 0.3
                    
                    # +130 <= x <= +159
                    if pick_odds <= 159:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.3
                        else:
                            return 0.3
                    
                    # +160 <= x <= +199
                    elif pick_odds <= 199:
                        if pick_source == 'fanatics':
                            return 0.5 # 2.2
                        else:
                            return 0.3
                        
                    # +200 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.6 # 3.1
                        else:
                            return 0.3

                # == Unders ==
                else:
                    
                    return 0.3
                
            elif re.search('\stotal', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    return 0.3

                # == Unders ==
                else:
                    
                    return 0.3

        # Basketball   
        elif pick_sport == 'basketball':

            if pick_market == 'moneyline':

                # -inf < x <= +119
                if pick_odds <= 119:
                    return 0.3
                
                # +120 <= x <= +239
                elif pick_odds <= 239:
                    if pick_source == 'betmgm':
                        return 0.4 # 1.3 jump
                    else:
                        return 0.3
                    
                # +240 <= x < inf
                else:
                    if pick_source == 'betmgm':
                        return 0.5 # 2.6 jump
                    else:
                        return 0.3

            elif pick_market == 'spread':

                # === + ===
                if re.search('\+', pick_bet):

                    # -inf < x <= -109
                    if pick_odds <= -109:
                        return 0.3
                    
                    # -110 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.5 jump
                        else:
                            return 0.3
                
                # === - ===
                else:

                    return 0.3

            elif pick_market_group == 'points': # player points
                # == Overs ==
                if re.search('o', pick_bet):
                    # -inf < x <= -111
                    if pick_odds <= -111:
                        return 0.3
                    
                    # -110 <= x <= -101
                    elif pick_odds <= -101:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                        
                    # +100 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'fanatics':
                            return 0.5 # 2
                        else:
                            return 0.3
                        
                    # +105 <= x <= +114
                    elif pick_odds <= 114:
                        if pick_source == 'betmgm':
                            return 0.4 # 3
                        elif pick_source == 'fanatics':
                            return 0.5 # 2
                        else:
                            return 0.3
                        
                    # +115 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.6
                        elif pick_source == 'fanatics':
                            return 0.5 # 2
                        else:
                            return 0.3
                
                # === Unders === 
                else:
                    # -inf < x <= -116
                    if pick_odds <= -116:
                        return 0.3
                    
                    # -115 <= x <= -106
                    elif pick_odds <= -106:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.5 
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.4 
                        else:
                            return 0.3
                        
                    # -105 <= x <= -101
                    elif pick_odds <= -101:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.5 
                        elif pick_source == 'fanatics':
                            return 0.5 # 3.8
                        else:
                            return 0.3
                        
                    # +100 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.5 
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 4.9
                        else:
                            return 0.3
                        
                    # +105 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.7, 2.7
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 4.9
                        else:
                            return 0.3
                        
                    # +110 <= x <= +114
                    elif pick_odds <= 114:
                        if pick_source == 'betmgm':
                            return 0.6 # 4.3
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 4.9
                        else:
                            return 0.3
                    
                    # +115 <= x <= +119
                    elif pick_odds <= 119:
                        if pick_source == 'betmgm':
                            return 0.7 # 3.5
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 4.9
                        else:
                            return 0.3
                        
                    # +120 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.7 # 3.5
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 4.9
                        else:
                            return 0.3
                        
            elif re.search('assist', pick_market):

                if re.search('o', pick_bet):

                    # -inf < x <= -126
                    if pick_odds <= -126:
                        return 0.3
                    
                    # -125 <= x <= -116
                    if pick_odds <= -116:
                        if pick_source == 'fanatics':
                            return 0.4 # 4.3
                        else:
                            return 0.3
                        
                    # -115 <= x <= -106
                    if pick_odds <= -106:
                        if pick_source == 'fanatics':
                            return 0.5 # 5.7
                        else:
                            return 0.3
                    
                    # -105 <= x <= +119
                    elif pick_odds <= 119:
                        if pick_source == 'fanatics':
                            return 0.6 # 5.1
                        else:
                            return 0.3
                        
                    # +120 <= x <= +134
                    elif pick_odds <= 134:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.3
                        elif pick_source == 'fanatics':
                            return 0.7 # 3.8, 5.1
                        else:
                            return 0.3
                        
                    # +135 <= x <= +139
                    elif pick_odds <= 139:
                        if pick_source == 'betmgm':
                            return 0.5 # 1.7
                        elif pick_source == 'fanatics':
                            return 0.7 # 3.8, 5.1
                        else:
                            return 0.3
                        
                    # +140 <= x <= +144
                    elif pick_odds <= 144:
                        if pick_source == 'betmgm':
                            return 0.6 # 4.6
                        elif pick_source == 'fanatics':
                            return 0.7 # 3.8, 5.1
                        else:
                            return 0.3
                        
                    # +145 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.6 # 4.6
                        elif pick_source == 'fanatics':
                            return 0.8 # 4.3
                        else:
                            return 0.3
                
                else: # under

                    # -inf < x <= -116
                    if pick_odds <= -116:
                        return 0.3
                    
                    # -115 <= x <= -106
                    if pick_odds <= -106:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.3
                        else:
                            return 0.3
                        
                    # -105 <= x <= -101
                    if pick_odds <= -101:
                        if pick_source == 'fanatics':
                            return 0.5 # 7.1
                        else:
                            return 0.3
                    
                    # +100 <= x <= +119
                    elif pick_odds <= 119:
                        if pick_source == 'fanatics':
                            return 0.6 # 1.4
                        else:
                            return 0.3
                        
                    # +120 <= x <= +124
                    elif pick_odds <= 124:
                        if pick_source == 'fanatics':
                            return 0.7 # 1.7
                        else:
                            return 0.3
                        
                    # +125 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.8 # 3.8
                        else:
                            return 0.3
                        
            elif re.search('rebound', pick_market):

                if re.search('o', pick_bet):

                    # -inf < x <= -101
                    if pick_odds <= -101:
                        return 0.3
                    
                    # +100 <= x <= +129
                    if pick_odds <= 129:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.9
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.8
                        else:
                            return 0.3
                        
                    # +130 <= x <= +134
                    if pick_odds <= 134:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.9
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.8
                        elif pick_source == 'fanatics':
                            return 0.4 # 4.8
                        else:
                            return 0.3
                    
                    # +135 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.9
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.8
                        elif pick_source == 'fanatics':
                            return 0.5 # 4.3
                        else:
                            return 0.3
                
                else: # under

                    # -inf < x <= -130
                    if pick_odds <= -130:
                        return 0.3
                    
                    # -129 <= x <= -116
                    if pick_odds <= -116:
                        if pick_source == 'betrivers':
                            return 0.4 # 2
                        else:
                            return 0.3
                    
                    # -115 <= x <= -101
                    if pick_odds <= -101:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.6
                        elif pick_source == 'betrivers':
                            return 0.4 # 2
                        elif pick_source == 'fanatics':
                            return 0.4 # 2
                        else:
                            return 0.3
                    
                    # +100 <= x <= +109
                    if pick_odds <= 109:
                        if pick_source == 'betmgm':
                            return 0.5 # 2.5
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.6
                        elif pick_source == 'fanatics':
                            return 0.4 # 2
                        else:
                            return 0.3
                    
                    # +110 <= x <= +114
                    if pick_odds <= 114:
                        if pick_source == 'betmgm':
                            return 0.5 # 2.5
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.6
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.8, 2
                        else:
                            return 0.3
                        
                    # +115 <= x <= + 119
                    elif pick_odds <= 119:
                        if pick_source == 'betmgm':
                            return 0.5 # 2.5
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.6
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.8, 2
                        else:
                            return 0.3

                    # +120 <= x <= + 129
                    elif pick_odds <= 129:
                        if pick_source == 'betmgm':
                            return 0.5 # 2.5
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.6
                        elif pick_source == 'fanatics':
                            return 0.5 # 5.3
                        else:
                            return 0.3
                        
                    # +130 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.6 # 4.4
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.6
                        elif pick_source == 'fanatics':
                            return 0.5 # 5.3
                        else:
                            return 0.3
                        
            elif re.search('three', pick_market):

                if re.search('o', pick_bet):

                    # -inf < x <= -131
                    if pick_odds <= -131:
                        return 0.3
                    
                    # -130 <= x <= +109
                    if pick_odds <= 109:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.3
                        else:
                            return 0.3
                    
                    # +110 <= x <= +134
                    if pick_odds <= 134:
                        if pick_source == 'betmgm':
                            return 0.4 # 2
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.3
                        else:
                            return 0.3

                    # +135 <= x <= +139
                    if pick_odds <= 139:
                        if pick_source == 'betmgm':
                            return 0.5 # 3.5
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.3
                        else:
                            return 0.3
                    
                    # +140 <= x <= +149
                    if pick_odds <= 149:
                        if pick_source == 'betmgm':
                            return 0.5 # 3.5
                        elif pick_source == 'fanatics':
                            return 0.5 # 6.8
                        else:
                            return 0.3
                        
                    # +150 <= x <= +164
                    if pick_odds <= 164:
                        if pick_source == 'betmgm':
                            return 0.6 # 4.4, 4.8
                        elif pick_source == 'fanatics':
                            return 0.5 # 6.8
                        else:
                            return 0.3

                    # +165 <= x <= +179
                    elif pick_odds <= 179:
                        if pick_source == 'betmgm':
                            return 0.7 # 4.7
                        elif pick_source == 'fanatics':
                            return 0.5 # 6.8
                        else:
                            return 0.3
                        
                    # +180 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.7 # 4.7
                        elif pick_source == 'betrivers':
                            return 0.4 # 6
                        elif pick_source == 'fanatics':
                            return 0.5 # 6.8
                        else:
                            return 0.3
                
                else: # under

                    # -inf < x <= -168
                    if pick_odds <= -168:
                        return 0.3
                    
                    # -167 <= x <= -136
                    if pick_odds <= -136:
                        if pick_source == 'betrivers':
                            return 0.4 # 2.1
                        else:
                            return 0.3
                    
                    # -135 <= x <= -126
                    elif pick_odds <= -126:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.1
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.1
                        else:
                            return 0.3
                        
                    # -125 <= x <= +119
                    elif pick_odds <= 119:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.1
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.1
                        elif pick_source == 'fanatics':
                            return 0.4 # 3.6
                        else:
                            return 0.3
                        
                    # +120 <= x <= +124
                    elif pick_odds <= 124:
                        if pick_source == 'betmgm':
                            return 0.5 # 2.2
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.1
                        elif pick_source == 'fanatics':
                            return 0.4 # 3.6
                        else:
                            return 0.3
                        
                    # +125 <= x <= +129
                    elif pick_odds <= 129:
                        if pick_source == 'betmgm':
                            return 0.6 # 2.7
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.1
                        elif pick_source == 'fanatics':
                            return 0.4 # 3.6
                        else:
                            return 0.3
                        
                    # +130 <= x <= +139
                    elif pick_odds <= 139:
                        if pick_source == 'betmgm':
                            return 0.7 # 2.9
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.1
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.3
                        else:
                            return 0.3
                        
                    # +140 <= x <= +144
                    elif pick_odds <= 144:
                        if pick_source == 'betmgm':
                            return 0.7 # 2.9
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.1
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.6
                        else:
                            return 0.3
                        
                    # +145 <= x <= +174
                    elif pick_odds <= 174:
                        if pick_source == 'betmgm':
                            return 0.7 # 2.9
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.1
                        elif pick_source == 'fanatics':
                            return 0.7 # 2.9
                        else:
                            return 0.3
                        
                    # +175 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.7 # 2.9
                        elif pick_source == 'betrivers':
                            return 0.4 # 2.1
                        elif pick_source == 'fanatics':
                            return 0.8 # 3.1, 4.2
                        else:
                            return 0.3
                        
                        
        elif pick_sport == 'baseball':

            # Big markets
            # take homers at -5000 w/ 0.3% val
            # Accept super likely picks at lower val?
            if pick_market == 'moneyline':
                
                # -inf < x <= -160
                if pick_odds <= -160:
                    return 0.3
                
                # -159 <= x <= -116
                elif pick_odds <= -116:
                    if pick_source == 'betrivers':
                        return 0.4 # 1
                    else:
                        return 0.3

                # -115 <= x < inf
                else:
                    if pick_source == 'betmgm':
                        return 0.4 # 1.6
                    elif pick_source == 'betrivers':
                        return 0.4 # 1
                    else:
                        return 0.3

            # just Spread
            elif pick_market == 'spread':
                
                # Plus
                if re.search('\+', pick_bet):
                    # -inf < x <= -451
                    if pick_odds <= -451:
                        return 0.3
                    
                    # -450 <= x <= -201
                    if pick_odds <= -201:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.6
                        else:
                            return 0.3
                    
                    # -200 <= x <= -191
                    if pick_odds <= -191:
                        if pick_source == 'fanatics':
                            return 0.5 # 0.9
                        else:
                            return 0.3
                        
                    # -190 <= x <= -181
                    if pick_odds <= -181:
                        if pick_source == 'fanatics':
                            return 0.6 # 1.1
                        else:
                            return 0.3
                    
                    # -180 <= x <= -121
                    elif pick_odds <= -121:
                        if pick_source == 'fanatics':
                            return 0.7 # 1.1
                        else:
                            return 0.3
                        
                    # -120 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.1
                        elif pick_source == 'fanatics':
                            return 0.7 # 1.1
                        else:
                            return 0.3
                # Minus
                else:

                    # -inf < x <= +109
                    if pick_odds <= 109:
                        return 0.3
                    
                    # +110 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.5
                        else:
                            return 0.3

            # Does Oddsview return "spread" or "run line"? spread
            # or both interchangeable??? noticed both but not sure why
            # elif pick_market == 'run line': # see spread
            #     return 0.3
                
            elif pick_market == 'total':

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    # -inf < x <= -276
                    if pick_odds <= -276:
                        return 0.3
                    
                    # -275 <= x <= -251
                    if pick_odds <= -251:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.8
                        else:
                            return 0.3
                    
                    # -250 <= x <= -241
                    elif pick_odds <= -241:
                        if pick_source == 'fanatics':
                            return 0.5 # 1
                        else:
                            return 0.3
                        
                    # -240 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'fanatics':
                            return 0.6 # 1.3
                        else:
                            return 0.3
                        
                    # +110 <= x <= +114
                    elif pick_odds <= 114:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.3
                        else:
                            return 0.3
                        
                    # +115 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.7 # 1.9
                        else:
                            return 0.3

                # == Unders ==
                else:
                    
                    # -inf < x <= -426
                    if pick_odds <= -426:
                        return 0.3
                    
                    # -425 <= x <= -401
                    elif pick_odds <= -401:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -400 <= x <= -276
                    elif pick_odds <= -276:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -275 <= x <= -196
                    elif pick_odds <= -196:
                        if pick_source == 'fanatics':
                            return 0.5 # 1
                        else:
                            return 0.3
                        
                    # -195 <= x <= -156
                    elif pick_odds <= -156:
                        if pick_source == 'betrivers':
                            return 0.4 # 0.5
                        elif pick_source == 'fanatics':
                            return 0.5 # 1
                        else:
                            return 0.3
                        
                    # -155 <= x <= -101
                    elif pick_odds <= -101:
                        if pick_source == 'betrivers':
                            return 0.5 # 1.5
                        elif pick_source == 'fanatics':
                            return 0.5 # 1
                        else:
                            return 0.3
                        
                    # +100 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'betrivers':
                            return 0.6 # 1.9
                        elif pick_source == 'fanatics':
                            return 0.5 # 1
                        else:
                            return 0.3
                        
                    # +110 <= x <= +164
                    elif pick_odds <= 164:
                        if pick_source == 'betrivers':
                            return 0.6 # 1.9
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.6
                        else:
                            return 0.3
                        
                    # +165 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.6 # 2.5
                        elif pick_source == 'betrivers':
                            return 0.7 # 1.5
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.6
                        else:
                            return 0.3
                    
            # First Inning Moneyline 3 way, draw
            elif re.search('first inning moneyline 3 way', pick_market) and pick_bet == 'draw':
                
                # -inf < x <= -116
                if pick_odds <= -116:
                    return 0.3
                
                # -115 <= x < inf
                else:

                    if pick_source == 'betrivers':
                        return 0.4 # 1.2
                    else:
                        return 0.3
                    
            # First Inning Moneyline
            elif re.search('first inning moneyline', pick_market):
                
                # -inf < x <= -108
                if pick_odds <= -108:
                    return 0.3
                
                # -107 <= x < inf
                else:

                    if pick_source == 'betrivers': # Night Before
                        return 0.4 # 1.5
                    else:
                        return 0.3
                        
            # Other Innings Moneyline
            elif re.search('innings moneyline', pick_market):
                
                # -inf < x <= -301
                if pick_odds <= -301:
                    return 0.3
                
                # -300 <= x <= -226
                if pick_odds <= -226:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    else:
                        return 0.3
                
                # -225 <= x <= -123
                if pick_odds <= -123:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers': # Night Before
                        return 0.4 # 1.4
                    else:
                        return 0.3
                    
                # -122 <= x <= -108
                if pick_odds <= -108:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers': # Night Before
                        return 0.5 # 1.9
                    else:
                        return 0.3

                # -107 <= x <= +129
                if pick_odds <= 129:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers':
                        return 0.6 # 2.4
                    else:
                        return 0.3
                    
                # +130 <= x <= +154
                if pick_odds <= 154:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers':
                        return 0.6 # 2.4
                    elif pick_source == 'fanatics':
                        return 0.4 # 2.2
                    else:
                        return 0.3
                    
                # +155 <= x <= +194
                if pick_odds <= 194:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers':
                        return 0.7 # 2.8
                    elif pick_source == 'fanatics':
                        return 0.4 # 2.2
                    else:
                        return 0.3

                # +195 <= x < inf
                else:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers':
                        return 0.8 # 4.2
                    elif pick_source == 'fanatics':
                        return 0.4 # 2.2
                    else:
                        return 0.3
                    

            # First Inning Spread
            elif re.search('first inning spread', pick_market):
                
                # Plus
                if re.search('\+', pick_bet):
                    return 0.3
                
                # Minus
                else:
                    return 0.3
                        
            # Other Innings Spread
            elif re.search('innings spread', pick_market):
                
                # Plus
                if re.search('\+', pick_bet):
                    # -inf < x <= -276
                    if pick_odds <= -276:
                        return 0.3
                    
                    # -275 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                
                # Minus
                else:
                    # -inf < x <= +109
                    if pick_odds <= 109:
                        return 0.3
                    
                    # +110 <= x <= +119
                    elif pick_odds <= 119:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.3
                        else:
                            return 0.3
                        
                    # +120 <= x <= +124
                    elif pick_odds <= 124:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.3
                        elif pick_source == 'betrivers':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                    
                    # +125 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.3
                        elif pick_source == 'betrivers':
                            return 0.4 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.5
                        else:
                            return 0.3

            # First Inning Total
            elif re.search('first inning total', pick_market):
                
                # == Overs ==
                if re.search('o', pick_bet):
                    # -inf < x <= +113
                    if pick_odds <= 113:
                        return 0.3

                    # +114 x <= +115
                    if pick_odds <= 115:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.9
                        else:
                            return 0.3
                    
                    # +116 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.5 # 2.2
                        else:
                            return 0.3

                # == Unders ==
                else:
                    # -inf < x <= +124
                    if pick_odds <= 124:
                        return 0.3
                    
                    # +125 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 2.2
                        else:
                            return 0.3
                        
            # First Inning Team Total
            elif re.search('first inning .+ total', pick_market):
                
                # == Overs ==
                if re.search('o', pick_bet):
                    # -inf < x <= +239
                    if pick_odds <= 239:
                        return 0.3
                    
                    # +240 <= x <= +269
                    elif pick_odds <= 269:
                        if pick_source == 'fanatics':
                            return 0.4 # 2.4
                        else:
                            return 0.3
                        
                    # +270 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.5 # 2.8
                        else:
                            return 0.3

                # == Unders ==
                else:
                    # -inf < x <= -376
                    if pick_odds <= -376:
                        return 0.3
                    
                    # -375 <= x <= -351
                    if pick_odds <= -351:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.7
                        else:
                            return 0.3

                    # -350 <= x <= -301
                    if pick_odds <= -301:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.4
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.7
                        else:
                            return 0.3
                    
                    # -300 <= x <= -279
                    if pick_odds <= -279:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.4
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3
                    
                    # -278 <= x <= -276
                    if pick_odds <= -276:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.4
                        elif pick_source == 'betrivers':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3
                    
                    # -275 <= x <= -251
                    elif pick_odds <= -251:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.6
                        elif pick_source == 'betrivers':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3
                        
                    # -250 <= x <= -246
                    elif pick_odds <= -246:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.6
                        elif pick_source == 'betrivers':
                            return 0.5 # 0.5
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3
                        
                    # -245 <= x <= -226
                    elif pick_odds <= -226:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.6
                        elif pick_source == 'betrivers':
                            return 0.6 # 0.7
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3
                        
                    # -225 <= x <= -181
                    elif pick_odds <= -181:
                        if pick_source == 'betmgm':
                            return 0.6 # 0.8
                        elif pick_source == 'betrivers':
                            return 0.6 # 0.7
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3
                        
                    # -180 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.6 # 0.8
                        elif pick_source == 'betrivers':
                            return 0.7 # 1.1
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.7
                        else:
                            return 0.3
                        
            # Other Inning Total
            elif re.search('innings total', pick_market):
                
                # == Overs ==
                if re.search('o', pick_bet):
                    # -inf < x <= -130
                    if pick_odds <= -130:
                        return 0.3
                    
                    # -129 <= x <= -114
                    elif pick_odds <= -114:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.1
                        else:
                            return 0.3

                    # -113 <= x <= -111
                    elif pick_odds <= -111:
                        if pick_source == 'betrivers':
                            return 0.5 # 1.2
                        else:
                            return 0.3

                    # -110 <= x <= -109
                    elif pick_odds <= -109:
                        if pick_source == 'betrivers':
                            return 0.6 # 1.3
                        else:
                            return 0.3
                        
                    # -108 <= x <= -106
                    elif pick_odds <= -106:
                        if pick_source == 'betrivers':
                            return 0.7 # 1.6
                        else:
                            return 0.3
                        
                    # -105 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'betrivers':
                            return 0.8 # 2.9
                        else:
                            return 0.3
                        
                    # +110 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.8 # 2.9
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.9
                        else:
                            return 0.3

                # == Unders ==
                else:
                    # -inf < x <= -111
                    if pick_odds <= -111:
                        return 0.3
                    
                    # -110 <= x <= +134
                    elif pick_odds <= 134:
                        if pick_source == 'fanatics':
                            return 0.3 # 1.4
                        else:
                            return 0.3
                        
                    # +135 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.4 # 6.6
                        else:
                            return 0.3
                

            # Other Inning Team Total
            elif re.search('innings .+ total', pick_market):
                
                # == Overs ==
                if re.search('o', pick_bet):
                    # -inf < x <= -101
                    if pick_odds <= -101:
                        return 0.3
                    
                    # +100 <= x <= +119
                    if pick_odds <= 119:
                        if pick_source == 'fanatics':
                            return 0.4 # 2.4
                        else:
                            return 0.3
                        
                    # +120 <= x <= +129
                    if pick_odds <= 129:
                        if pick_source == 'fanatics':
                            return 0.5 # 2.8
                        else:
                            return 0.3
                    
                    # +130 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.5 # 2.8
                        else:
                            return 0.3

                # == Unders ==
                else:
                    # -inf < x <= -113
                    if pick_odds <= -113:
                        return 0.3
                    
                    # -112 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.3
                        else:
                            return 0.3
                        
                    # +105 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.3
                        elif pick_source == 'fanatics':
                            return 0.4 # 4.2
                        else:
                            return 0.3
                        
            


            # Team Total
            elif re.search('\stotal', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):
                    
                    return 0.3

                # == Unders ==
                else:
                    
                    return 0.3
                    
            elif re.search('home', pick_market):

                # == Overs ==
                if re.search('o', pick_bet):

                    # -inf < x <= +539
                    if pick_odds <= 539:
                        return 0.3
                    
                    # +540 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 7
                        else:
                            return 0.3

                else:
                
                    # -inf < x <= -5000
                    if pick_odds <= -5000:
                        return 0.3 # any source min

                    # -4999 <= x <= -3100
                    if pick_odds <= -3100:
                        return 0.3 # need source

                    # -3099 <= x <= -1668
                    if pick_odds <= -1668:
                        return 0.3 # need source
                    
                    # -1667 <= x <= -1601
                    if pick_odds <= -1601:
                        if pick_source == 'betrivers':
                            return 0.4 # 0.5
                        else:
                            return 0.3 
                    
                    # -1600 <= x <= -1201
                    if pick_odds <= -1201:
                        if pick_source == 'betmgm':
                            return 0.4
                        elif pick_source == 'betrivers':
                            return 0.4 # 0.5
                        else:
                            return 0.3 
                        
                    # -1200 <= x <= -1116
                    if pick_odds <= -1116:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.8
                        elif pick_source == 'betrivers':
                            return 0.4 # 0.5
                        else:
                            return 0.3 
                    
                    # -1115 <= x <= -1101
                    if pick_odds <= -1001:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.8, 0.9
                        elif pick_source == 'betrivers':
                            return 0.5 # 0.5, 0.6
                        else:
                            return 0.3 
                        
                    # -1100 <= x <= -1001
                    if pick_odds <= -1001:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.8, 0.9
                        elif pick_source == 'betrivers':
                            return 0.5 # 0.5, 0.6
                        elif pick_source == 'fanatics':
                            return 0.4
                        else:
                            return 0.3 
                    
                    # -1000 <= x <= -836
                    if pick_odds <= -836:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.8, 0.9
                        elif pick_source == 'betrivers':
                            return 0.6 # 1.1
                        elif pick_source == 'fanatics':
                            return 0.4
                        else:
                            return 0.3

                    # -835 <= x <= -801
                    if pick_odds <= -801:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.8, 0.9
                        elif pick_source == 'betrivers':
                            return 0.7 # 1.7, 2.1
                        elif pick_source == 'fanatics':
                            return 0.4
                        else:
                            return 0.3
                        
                    # -800 <= x <= -751
                    if pick_odds <= -751:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.8, 0.9
                        elif pick_source == 'betrivers':
                            return 0.7 # 1.7, 2.1
                        elif pick_source == 'fanatics':
                            return 0.4
                        else:
                            return 0.3
                        
                    # -750 <= x <= -716
                    if pick_odds <= -716:
                        if pick_source == 'betmgm':
                            return 0.6 # 0.9
                        elif pick_source == 'betrivers':
                            return 0.7 # 1.7, 2.1
                        elif pick_source == 'fanatics':
                            return 0.4 # 2.5
                        else:
                            return 0.3
                        
                    # -715 <= x <= -701
                    if pick_odds <= -701:
                        if pick_source == 'betmgm':
                            return 0.6 # 0.9
                        elif pick_source == 'betrivers':
                            return 0.7 # 1.7, 2.1
                        elif pick_source == 'fanatics':
                            return 0.4 # 2.5
                        else:
                            return 0.3

                    # -700 <= x <= -671
                    if pick_odds <= -671:
                        if pick_source == 'betmgm':
                            return 0.7 # 1.3
                        elif pick_source == 'betrivers':
                            return 0.7 # 1.7, 2.1
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.5, 2.2, 2.9
                        else:
                            return 0.3
                        
                    # Avoid Odds -450, Betmgm, Val 1.1% R Lewis 8/12/24
                    # -670 <= x <= -576
                    if pick_odds <= -576:
                        if pick_source == 'betmgm':
                            return 0.7 # 1.3
                        elif pick_source == 'betrivers':
                            return 0.8 # 1.8
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.5, 2.2, 2.9
                        else:
                            return 0.3
                        
                    # -575 <= x <= -531
                    if pick_odds <= -531:
                        if pick_source == 'betmgm':
                            return 0.7 # 1.3
                        elif pick_source == 'betrivers':
                            return 0.8 # 1.8
                        elif pick_source == 'fanatics':
                            return 0.6 # 3.6
                        else:
                            return 0.3
                        
                    # -530 <= x <= -451
                    if pick_odds <= -451:
                        if pick_source == 'betmgm':
                            return 0.7 # 1.3
                        elif pick_source == 'betrivers':
                            return 0.9 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 3.6
                        else:
                            return 0.3

                    # -450 <= x <= -421
                    if pick_odds <= -421:
                        if pick_source == 'betmgm':
                            return 0.8 # 1.4
                        elif pick_source == 'betrivers':
                            return 0.9 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 3.6
                        else:
                            return 1.1
                        
                    # -420 <= x <= -401
                    if pick_odds <= -401:
                        if pick_source == 'betmgm':
                            return 0.8 # 1.4
                        elif pick_source == 'betrivers':
                            return 0.9 # 2.2
                        elif pick_source == 'fanatics':
                            return 0.6 # 3.6
                        else:
                            return 1.1
                        
                    # -400 <= x <= -351
                    if pick_odds <= -351:
                        if pick_source == 'betmgm':
                            return 0.8 # 1.4
                        elif pick_source == 'betrivers':
                            return 1 # 2.4
                        elif pick_source == 'fanatics':
                            return 0.6 # 3.6
                        else:
                            return 1.1

                    # -350 <= x <= -346
                    if pick_odds <= -346:
                        if pick_source == 'betmgm':
                            return 0.8 # 1.4
                        elif pick_source == 'betrivers':
                            return 1 # 2.4
                        elif pick_source == 'fanatics':
                            return 0.7 # 3.3
                        else:
                            return 1.1
                        
                    # -345 <= x <= -181
                    elif pick_odds <= -181:
                        if pick_source == 'betmgm':
                            return 0.8 # 1.4
                        elif pick_source == 'betrivers':
                            return 1 # 2.4
                        elif pick_source == 'fanatics':
                            return 0.7 # 3.3
                        else:
                            return 0.3
                        
                    # -180 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.8 # 1.4
                        elif pick_source == 'betrivers':
                            return 1 # 2.4
                        elif pick_source == 'fanatics':
                            return 0.8 # 2.2
                        else:
                            return 0.3
                    
                    # Consider Home Run overs as well
                    # Test reliable EV vals
            
            # Strikeouts, Odds -150, source fanatics -> Min Val 2.4%
            elif re.search('strikeout', pick_market):
                
                if re.search('o', pick_bet): # over
                    # -inf < x <= -151
                    if pick_odds <= -151:
                        return 0.3

                    # -150 <= x <= -141
                    if pick_odds <= -141:
                        if pick_source == 'fanatics':
                            return 0.4 # 1
                        else:
                            return 0.3
                    
                    # -140 <= x <= -126
                    if pick_odds <= -126:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.9
                        elif pick_source == 'fanatics':
                            return 0.4 # 1
                        else:
                            return 0.3
                        
                    # -125 <= x <= -121
                    if pick_odds <= -121:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.9
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.2
                        else:
                            return 0.3
                    
                    # -120 <= x <= -115
                    if pick_odds <= -115:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.8
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.2
                        else:
                            return 0.3
                        
                    # -114 <= x <= -107
                    if pick_odds <= -107:
                        if pick_source == 'betrivers':
                            return 0.5 # 2.8
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.2
                        else:
                            return 0.3
                        
                    # -106 <= x <= -101
                    if pick_odds <= -101:
                        if pick_source == 'betrivers':
                            return 0.5 # 2.8
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.2
                        else:
                            return 0.3
                        
                    # +100 <= x <= +109
                    if pick_odds <= 109:
                        if pick_source == 'betrivers':
                            return 0.6 # 4.4
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.2
                        else:
                            return 0.3
                        
                    # +110 <= x <= +119
                    if pick_odds <= 119:
                        if pick_source == 'betrivers':
                            return 0.6 # 4.4
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.2
                        else:
                            return 0.3
                        
                    # +120 <= x <= +124
                    if pick_odds <= 124:
                        if pick_source == 'betrivers':
                            return 0.6 # 4.4
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4
                        else:
                            return 0.3
                        
                    # +125 <= x <= +137
                    if pick_odds <= 137:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.9
                        elif pick_source == 'betrivers':
                            return 0.6 # 4.4
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4
                        else:
                            return 0.3

                    # +138 <= x <= +139
                    if pick_odds <= 139:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.9
                        elif pick_source == 'betrivers':
                            return 0.7 # 5.5
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4
                        else:
                            return 0.3
                        
                    # +140 <= x <= +144
                    if pick_odds <= 144:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.9
                        elif pick_source == 'betrivers':
                            return 0.7 # 5.5
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4
                        else:
                            return 0.3
                    
                    # +145 <= x <= +154
                    elif pick_odds <= 154:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.9
                        elif pick_source == 'betrivers':
                            return 0.7 # 5.5
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4
                        else:
                            return 0.3

                    # +155 <= x <= +162
                    elif pick_odds <= 162:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.9
                        elif pick_source == 'betrivers':
                            return 0.7 # 5.5
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4
                        else:
                            return 0.3

                    # +163 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.9
                        elif pick_source == 'betrivers':
                            return 0.8 # 6
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4
                        else:
                            return 0.3
                
                else: # === Under === 
                    # -inf < x <= -166
                    if pick_odds <= -166:
                        return 0.3
                    
                    # -165 <= x <= -156
                    if pick_odds <= -156:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        else:
                            return 0.3
                    
                    # -155 <= x <= -144
                    elif pick_odds <= -144:

                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        else:
                            return 0.3
                        
                    # -143 <= x <= -131
                    elif pick_odds <= -131:

                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.4 # 1.1
                        else:
                            return 0.3
                        
                    # -130 <= x <= -111
                    elif pick_odds <= -111:

                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.4 # 1.1
                        elif pick_source == 'fanatics':
                            return 0.4 # 1
                        else:
                            return 0.3
                        
                    # -110 <= x <= -101
                    elif pick_odds <= -101:

                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.4 # 1.1
                        elif pick_source == 'fanatics':
                            return 0.4 # 1
                        else:
                            return 0.3
                        
                    # +100 <= x <= +104
                    elif pick_odds <= 104:

                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.9
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.4
                        else:
                            return 0.3

                    # +105 <= x <= +107
                    elif pick_odds <= 107:

                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.9
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.4
                        else:
                            return 0.3
                        
                    # +108 <= x <= +109
                    elif pick_odds <= 109:

                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.6 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.4
                        else:
                            return 0.3
                            
                    # +110 <= x < +119
                    elif pick_odds <= 119:

                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.6 # 1.4
                        if pick_source == 'fanatics':
                            return 0.5 # 1.4
                        else:
                            return 0.3
                        
                    # +120 <= x < +127
                    elif pick_odds <= 127:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.6 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.4
                        else:
                            return 0.3
                        
                    # +128 <= x < +134
                    elif pick_odds <= 134:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.6 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.4
                        else:
                            return 0.3
                        
                    # +135 <= x < +139
                    elif pick_odds <= 139:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.7 # 2.6
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.7
                        else:
                            return 0.3
                        
                    # +140 <= x < +154
                    elif pick_odds <= 154:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.7 # 2.6
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.7
                        else:
                            return 0.3
                        
                    # +155 <= x < +159
                    elif pick_odds <= 174:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.8 # 3.3
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.7
                        else:
                            return 0.3
                        
                    # +160 <= x < +164
                    elif pick_odds <= 164:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.8 # 3.3
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.7
                        else:
                            return 0.3
                        
                    # +165 <= x < +174
                    elif pick_odds <= 174:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.9 # 3.4
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.7
                        else:
                            return 0.3

                    # +175 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.6
                        elif pick_source == 'betrivers':
                            return 0.9 # 3.4
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.7
                        else:
                            return 0.3
                        
            elif re.search('pitcher out', pick_market):

                if re.search('o', pick_bet):

                    # -inf < x <= -176
                    if pick_odds <= -176:
                        return 0.3

                    # -175 <= x <= -166
                    if pick_odds <= -166:
                        if pick_source == 'betrivers':
                            return 0.4 # 0.6
                        else:
                            return 0.3
                    
                    # -165 <= x <= -158
                    elif pick_odds <= -158:

                        if pick_source == 'betrivers':
                            return 0.5 # 1.6
                        else:
                            return 0.3

                    # -157 <= x <= -142
                    elif pick_odds <= -142:

                        if pick_source == 'betrivers':
                            return 0.6 # 1.7
                        else:
                            return 0.3
                        
                    # -141 <= x <= -125
                    elif pick_odds <= -125:

                        if pick_source == 'betrivers':
                            return 0.6 # 1.7
                        else:
                            return 0.3
                        
                    # -124 <= x <= +111
                    elif pick_odds <= 111:

                        if pick_source == 'betrivers':
                            return 0.7 # 1.9
                        else:
                            return 0.3
                            
                    # +112 <= x < inf
                    else:

                        if pick_source == 'betrivers':
                            return 0.8 # 5.7
                        else:
                            return 0.3
                        
                else: # === Under ===

                    # -inf < x <= -160
                    if pick_odds <= -160:
                        return 0.3
                    
                    # -159 <= x <= -158
                    if pick_odds <= -158:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.5
                        else:
                            return 0.3
                    
                    # -157 <= x <= -156
                    elif pick_odds <= -156:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.5
                        else:
                            return 0.3
                        
                    # -155 <= x <= -130
                    elif pick_odds <= -130:
                        if pick_source == 'betrivers':
                            return 0.5 # 2.6
                        else:
                            return 0.3
                        
                    # -129 <= x <= -116
                    elif pick_odds <= -116:
                        if pick_source == 'betrivers':
                            return 0.6 # 4.4
                        else:
                            return 0.3
                        
                    # -115 <= x <= +101
                    elif pick_odds <= 101:
                        if pick_source == 'betrivers':
                            return 0.6 # 4.4
                        else:
                            return 0.3
                    
                    # 102 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.6 # 4.4
                        else:
                            return 0.3


            elif pick_market_group == 'hits + runs + rbis':

                if re.search('o', pick_bet): # over
                    return 0.3
                
                else: # under
                    # -inf < x <= -111
                    if pick_odds <= -111:
                        return 0.3
                    
                    # -110 <= x <= -106
                    elif pick_odds <= -106:
                        if pick_source == 'betmgm':
                            return 0.4 # 2.6
                        else:
                            return 0.3
                        
                    # -105 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.5 # 3.9
                        else:
                            return 0.3

            elif pick_market_group == 'runs':

                if re.search('o', pick_bet):
                    
                    # -inf < x <= -137
                    if pick_odds <= -137:
                        return 0.3
                    
                    # -136 <= x <= -133
                    if pick_odds <= -133:
                        if pick_odds == 'betrivers':
                            return 0.4 # 2.3
                        else:
                            return 0.3

                    # -132 <= x <= -118
                    if pick_odds <= -118:
                        if pick_odds == 'betrivers':
                            return 0.5 # 2.2
                        else:
                            return 0.3
                    
                    # -117 <= x <= -105
                    if pick_odds <= -105:
                        if pick_odds == 'betrivers':
                            return 0.6 # 4.2
                        else:
                            return 0.3

                    # -104 <= x <= +101
                    if pick_odds <= 101:
                        if pick_odds == 'betrivers':
                            return 0.6 # 4.2
                        else:
                            return 0.3

                    # +102 <= x <= +105
                    if pick_odds <= 105:
                        if pick_odds == 'betrivers':
                            return 0.7 # 2.4
                        else:
                            return 0.3
                    
                    # +106 <= x <= +106
                    elif pick_odds <= 106:
                        if pick_odds == 'betrivers':
                            return 0.7 # 2.4
                        else:
                            return 0.3
                        
                    # x = +107
                    elif pick_odds == 107:
                        if pick_odds == 'betrivers':
                            return 0.8 # 1.5
                        else:
                            return 0.3
                        
                    # +108 <= x <= +111
                    elif pick_odds <= 111:
                        if pick_odds == 'betrivers':
                            return 0.8 # 1.5
                        else:
                            return 0.3
                    
                    # +112 <= x <= +131
                    elif pick_odds <= 131:
                        if pick_source == 'betrivers':
                            return 0.8 # 1.5
                        else:  
                            return 0.3
                        
                    # +132 <= x <= +134
                    elif pick_odds <= 134:
                        if pick_source == 'betrivers':
                            return 0.8 # 1.5
                        else:
                            return 0.3

                    # +135 <= x <= +174
                    elif pick_odds <= 174:
                        if pick_source == 'betrivers':
                            return 0.8 # 1.5
                        else:
                            return 0.3

                    # +175 <= x <= +209
                    elif pick_odds <= 209:
                        if pick_source == 'betmgm':
                            return 0.4 # 3.2
                        elif pick_source == 'betrivers':
                            return 0.8 # 1.5
                        else:
                            return 0.3

                    # +210 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.5 # 4.2
                        elif pick_source == 'betrivers':
                            return 0.8 # 1.5
                        else:
                            return 0.3
                
                else: # under

                    # -inf < x <= -187
                    if pick_odds <= -187:
                        return 0.3
                    
                    # -186 <= x <= -178
                    elif pick_odds <= -178:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.1
                        else:
                            return 0.3
                        
                    # -177 <= x <= -126
                    elif pick_odds <= -126:
                        if pick_source == 'betrivers':
                            return 0.5 # 3
                        else:
                            return 0.3
                        
                    # -125 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.2
                        elif pick_source == 'betrivers':
                            return 0.5 # 3
                        else:
                            return 0.3
                            
                    # +110 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 1.2
                        elif pick_source == 'betrivers':
                            return 0.6 # 3.7
                        else:
                            return 0.3
                    
            
                    
            elif pick_market_group == 'bases':

                if re.search('o', pick_bet):

                    # -inf < x <= -156
                    if pick_odds <= -156:
                        return 0.3

                    # -155 <= x <= -141
                    if pick_odds <= -141:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.8, 1
                        else:
                            return 0.3

                    # -140 <= x <= -108
                    if pick_odds <= -108:
                        if pick_source == 'fanatics':
                            return 0.5 # 1.3
                        else:
                            return 0.3
                    
                    # -107 <= x <= -101
                    elif pick_odds <= -101:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.3
                        else:
                            return 0.3
                    
                    # +100 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'betrivers':
                            return 0.5 # 1.5
                        elif pick_source == 'fanatics':
                            return 0.5 # 1.3
                        else:
                            return 0.3
                        
                    # x = +105
                    elif pick_odds == 105:
                        if pick_source == 'betrivers':
                            return 0.5 # 1.5
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4, 3.3, 3.8
                        else:
                            return 0.3
                    
                    # +106 <= x <= +139
                    elif pick_odds <= 139:
                        if pick_source == 'betrivers':
                            return 0.6 # 2.3
                        elif pick_source == 'fanatics':
                            return 0.6 # 1.4, 3.3, 3.8
                        else:
                            return 0.3
                        
                    # +140 <= x <= +154
                    elif pick_odds <= 154:
                        if pick_source == 'betrivers':
                            return 0.7 # 2.5
                        elif pick_source == 'fanatics':
                            return 0.7 # 1.9
                        else:
                            return 0.3

                    # +155 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.8 # 3.8
                        elif pick_source == 'fanatics':
                            return 0.7 # 1.9
                        else:
                            return 0.3
                
                else: # under

                    # -inf < x <= -176
                    if pick_odds <= -176:
                        return 0.3

                    # -175 <= x <= -133
                    elif pick_odds <= -133:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        else:
                            return 0.3
                            
                    # -132 <= x <= -128
                    elif pick_odds <= -128:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'betrivers':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -127 <= x <= +119
                    elif pick_odds <= 119:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.7
                        else:
                            return 0.3

                    # +120 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'betrivers':
                            return 0.5 # 2.7
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.4
                        else:
                            return 0.3

            elif pick_market_group == 'rbi':

                if re.search('o', pick_bet):

                    # -inf < x <= +132
                    if pick_odds <= 132:
                        return 0.3
                    
                    # +133 <= x <= +144
                    elif pick_odds <= 144:
                        if pick_source == 'betrivers':
                            return 0.4 # 6.7
                        else:
                            return 0.3
                    
                    # +145 <= x <= +154
                    elif pick_odds <= 154:
                        if pick_source == 'betrivers':
                            return 0.4 # 6.7
                        else:
                            return 0.3
                        
                    # +155 <= x <= +174
                    elif pick_odds <= 174:
                        if pick_source == 'betrivers':
                            return 0.4 # 6.7
                        else:
                            return 0.3
                    
                    # +175 <= x <= +187
                    elif pick_odds <= 187:
                        if pick_source == 'betrivers':
                            return 0.4 # 6.7
                        else:
                            return 0.3
                        
                    # +188 <= x <= 194
                    elif pick_odds <= 194:
                        if pick_source == 'betrivers':
                            return 0.4 # 6.7
                        else:
                            return 0.3
                        
                    # 195 <= x <= 204
                    elif pick_odds <= 204:
                        if pick_source == 'betrivers':
                            return 0.4 # 6.7
                        else:
                            return 0.3
                    
                    # 205 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 6.7
                        else:
                            return 0.3
                
                else: # under

                    # -inf < x <= -376
                    if pick_odds <= -376:
                        return 0.3

                    # -375 <= x <= -336
                    if pick_odds <= -336:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                    
                    # -335 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 1
                        elif pick_source == 'fanatics':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                

            elif re.search('hits', pick_market_group):

                if re.search('o', pick_bet):

                    # -inf < x <= -196
                    if pick_odds <= -196:
                        return 0.3
                    
                    # -195 <= x <= -181
                    elif pick_odds <= -181:
                        if pick_source == 'betrivers':
                            return 0.4 # 0.6
                        else:
                            return 0.3
                        
                    # -180 <= x <= -168
                    elif pick_odds <= -168:
                        if pick_source == 'betrivers':
                            return 0.4 # 0.6
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -167 <= x <= -156
                    elif pick_odds <= -156:
                        if pick_source == 'betrivers':
                            return 0.5 # 1.3
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                    
                    # -155 <= x <= -153
                    elif pick_odds <= -153:
                        if pick_source == 'betrivers':
                            return 0.6 # 1.9
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -152 <= x <= -151
                    elif pick_odds <= -151:
                        if pick_source == 'betrivers':
                            return 0.7 # 2.9
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -150 <= x <= -149
                    elif pick_odds <= -149:
                        if pick_source == 'betrivers':
                            return 0.8 # 1, 3.6
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -148 <= x <= -144
                    elif pick_odds <= -144:
                        if pick_source == 'betrivers':
                            return 0.9 # 3.7
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -143 <= x <= -138
                    elif pick_odds <= -138:
                        if pick_source == 'betrivers':
                            return 1 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3

                    # x = -137
                    elif pick_odds == -137:
                        if pick_source == 'betrivers':
                            return 1.1 # 4
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -136 <= x <= -126
                    elif pick_odds <= -126:
                        if pick_source == 'betrivers':
                            return 1.1 # 4
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # x = -125
                    elif pick_odds == -125:
                        if pick_source == 'betrivers':
                            return 1.2 # 4.8
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -124 <= x <= -122
                    elif pick_odds <= -122:
                        if pick_source == 'betrivers':
                            return 1.3 # 5.4
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -121 <= x <= -115
                    elif pick_odds <= -115:
                        if pick_source == 'betrivers':
                            return 1.3 # 5.4
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                     # x = -114
                    elif pick_odds == -114:
                        if pick_source == 'betrivers':
                            return 1.4 # 1.7
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # -113 <= x <= +179
                    elif pick_odds <= 179:
                        if pick_source == 'betrivers':
                            return 1.4 # 1.7
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                        
                    # +180 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 1.4 # 1.7
                        elif pick_source == 'fanatics':
                            return 0.4 # 0.9
                        else:
                            return 0.3
                
                else: # under

                    # -inf < x <= -276
                    if pick_odds <= -276:
                        return 0.3

                    # -275 <= x <= -261
                    elif pick_odds <= -261:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.2
                        else:
                            return 0.3
                    
                    # -260 <= x <= -251
                    elif pick_odds <= -251:
                        if pick_source == 'fanatics':
                            return 0.5 # 1.9
                        else:
                            return 0.3
                    
                    # -250 <= x <= -241
                    elif pick_odds <= -241:
                        if pick_source == 'fanatics':
                            return 0.5 # 1.9
                        else:
                            return 0.3
                        
                    # -240 <= x <= -166
                    elif pick_odds <= -166:
                        if pick_source == 'fanatics':
                            return 0.5 # 1.9
                        else:
                            return 0.3
                        
                    # -165 <= x <= -116
                    elif pick_odds <= -116:
                        if pick_source == 'fanatics':
                            return 0.6 # 1.5
                        else:
                            return 0.3

                    # -115 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'fanatics':
                            return 0.7 # 1.5
                        else:
                            return 0.3
                    
                    # +105 <= x <= +119
                    elif pick_odds <= 119:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.4
                        elif pick_source == 'fanatics':
                            return 0.9 # 2.6, 3.3, 4.2, 6.2
                        else:
                            return 0.3

                    # +120 <= x <= +124
                    elif pick_odds <= 124:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.4
                        elif pick_source == 'fanatics':
                            return 1 # 2.6, 4.3
                        else:
                            return 0.3
                        
                    # +125 <= x <= +129
                    elif pick_odds <= 129:
                        if pick_source == 'betrivers':
                            return 0.5 # 3
                        elif pick_source == 'fanatics':
                            return 1.1 # 2.1, 2.6
                        else:
                            return 0.3
                        
                    # +130 <= x <= +134
                    elif pick_odds <= 134:
                        if pick_source == 'betrivers':
                            return 0.5 # 3
                        elif pick_source == 'fanatics':
                            return 1.2 # 3.1
                        else:
                            return 0.3

                    # +135 <= x <= +154
                    elif pick_odds <= 154:
                        if pick_source == 'betrivers':
                            return 0.5 # 3
                        elif pick_source == 'fanatics':
                            return 1.3 # 7.1
                        else:
                            return 0.3

                    # +155 <= x <= +169
                    elif pick_odds <= 169:
                        if pick_source == 'betrivers':
                            return 0.5 # 3
                        elif pick_source == 'fanatics':
                            return 1.4 # 6.7
                        else:
                            return 0.3
                        
                    # +170 <= x <= +189
                    elif pick_odds <= 189:
                        if pick_source == 'betrivers':
                            return 0.5 # 3
                        elif pick_source == 'fanatics':
                            return 1.5 # 2.8
                        else:
                            return 0.3
                        
                    # +190 <= x <= +194
                    elif pick_odds <= 194:
                        if pick_source == 'betrivers':
                            return 0.6 # 5.4
                        elif pick_source == 'fanatics':
                            return 1.5 # 2.8
                        else:
                            return 0.3
                        
                    # +195 <= x <= +204
                    elif pick_odds <= 204:
                        if pick_source == 'betmgm':
                            return 0.4 # 4.5
                        elif pick_source == 'betrivers':
                            return 0.6 # 5.4
                        elif pick_source == 'fanatics':
                            return 1.5 # 2.8
                        else:
                            return 0.3
                        
                    # +205 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 4.5
                        elif pick_source == 'betrivers':
                            return 0.6 # 5.4
                        elif pick_source == 'fanatics':
                            return 1.5 # 2.8
                        else:
                            return 0.3

            elif pick_market_group == 'doubles':

                if re.search('o', pick_bet):

                    return 0.3
                
                else: # under

                    # -inf < x <= -701
                    if pick_odds <= -701:
                        return 0.3
                    
                    # -700 <= x <= -591
                    if pick_odds <= -591:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        else:
                            return 0.3
                    
                    # -590 <= x <= -456
                    elif pick_odds <= -456:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'betrivers':
                            return 0.4 # 0.5
                        else:
                            return 0.3
                    
                    # -455 <= x <= -451
                    elif pick_odds <= -451:
                        if pick_source == 'betmgm':
                            return 0.4 # 0.6
                        elif pick_source == 'betrivers':
                            return 0.5 # 1.3
                        else:
                            return 0.3
                    
                    # -450 <= x <= -401
                    elif pick_odds <= -401:
                        if pick_source == 'betmgm':
                            return 0.5 # 0.7
                        elif pick_source == 'betrivers':
                            return 0.5 # 1.3
                        else:
                            return 0.3

                    # -400 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.6 # 0.9
                        elif pick_source == 'betrivers':
                            return 0.5 # 1.3
                        else:
                            return 0.3

            elif pick_market_group == 'singles':

                if re.search('o', pick_bet):

                    # -inf < x <= -131
                    if pick_odds <= -131:
                        return 0.3
                    
                    # -130 <= x <= -121
                    if pick_odds <= -121:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.1, 1.6
                        else:
                            return 0.3

                    # -120 <= x <= -116
                    if pick_odds <= -116:
                        if pick_source == 'fanatics':
                            return 0.5 # 3.9
                        else:
                            return 0.3
                        
                    # -115 <= x <= -111
                    if pick_odds <= -111:
                        if pick_source == 'fanatics':
                            return 0.6 # 2.2
                        else:
                            return 0.3
                    
                    # -110 <= x <= -106
                    elif pick_odds <= -106:
                        if pick_source == 'fanatics':
                            return 0.7 # 1.6
                        else:
                            return 0.3
                    
                    # -105 <= x <= +104
                    elif pick_odds <= 104:
                        if pick_source == 'fanatics':
                            return 0.8 # 2.9
                        else:
                            return 0.3
                        
                    # +105 <= x <= +109
                    elif pick_odds <= 109:
                        if pick_source == 'fanatics':
                            return 1 # 1.3, 3.4, 5.9
                        else:
                            return 0.3
                        
                    # +110 <= x <= +114
                    elif pick_odds <= 114:
                        if pick_source == 'fanatics':
                            return 1.1 # 1.3, 3.5
                        else:
                            return 0.3
                        
                    # +115 <= x <= +119
                    elif pick_odds <= 119:
                        if pick_source == 'betmgm':
                            return 0.4 # 4.9
                        elif pick_source == 'fanatics':
                            return 1.2 # 3.9, 5.9
                        else:
                            return 0.3
                    
                    # +120 <= x <= +124
                    elif pick_odds <= 124:
                        if pick_source == 'betmgm':
                            return 0.4 # 4.9
                        elif pick_source == 'fanatics':
                            return 1.4 # 1.6, 2.8, 3.3
                        else:
                            return 0.3

                    # +125 <= x <= +129
                    elif pick_odds <= 129:
                        if pick_source == 'betmgm':
                            return 0.4 # 4.9
                        elif pick_source == 'fanatics':
                            return 1.5 # 1.2, 4.1
                        else:
                            return 0.3
                        
                    # +130 <= x <= +154
                    elif pick_odds <= 154:
                        if pick_source == 'betmgm':
                            return 0.4 # 4.9
                        elif pick_source == 'fanatics':
                            return 1.6 # 2.3, 6.3
                        else:
                            return 0.3

                    # +155 <= x < inf
                    else:
                        if pick_source == 'betmgm':
                            return 0.4 # 4.9
                        elif pick_source == 'fanatics':
                            return 1.7 # 2.5
                        else:
                            return 0.3
                
                else: # under

                    # -inf < x <= -121
                    if pick_odds <= -121:
                        return 0.3
                    
                    # -120 <= x <= -116
                    if pick_odds <= -116:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.8
                        else:
                            return 0.3
                    
                    # -115 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.5 # 1.6
                        else:
                            return 0.3
                        
                        
            elif re.search('triple', pick_market): 
                
                return 0.3
            

        elif pick_sport == 'mma':

            if pick_market == 'moneyline':
                
                # -inf < x <= -151
                if pick_odds <= -151:
                    return 0.3
                
                # -150 <= x < inf
                else:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.9, 1.8
                    else:
                        return 0.3
                    
            
        elif pick_sport == 'tennis':

            if pick_market == 'moneyline':
                
                # -inf < x <= -421
                if pick_odds <= -421:
                    return 0.3
                
                # -420 <= x <= -201
                if pick_odds <= -201:
                    if pick_source == 'betrivers':
                        return 0.4 # 0.4
                    else:
                        return 0.3
                
                # -200 <= x <= -161
                if pick_odds <= -161:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers':
                        return 0.4 # 0.4   
                    else:
                        return 0.3
                
                # -160 <= x <= -133
                elif pick_odds <= -133:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers':
                        return 0.4 # 0.4  
                    elif pick_source == 'fanatics':
                        return 0.4 # 0.9
                    else:
                        return 0.3
                    
                # -132 <= x < inf
                else:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    elif pick_source == 'betrivers':
                        return 0.5 # 1.8
                    elif pick_source == 'fanatics':
                        return 0.4 # 0.9
                    else:
                        return 0.3
                    
            elif pick_market == 'set 1 winner':
                
                # -inf < x <= -251
                if pick_odds <= -251:
                    return 0.3
                
                # -250 <= x <= -221
                elif pick_odds <= -221:
                    if pick_source == 'betrivers':
                        return 0.4 # 0.7
                    else:
                        return 0.3

                # -220 <= x <= -187
                elif pick_odds <= -187:
                    if pick_source == 'betrivers':
                        return 0.5 # 2.2
                    else:
                        return 0.3
                    
                # -186 <= x < inf
                else:
                    if pick_source == 'betrivers':
                        return 0.6 # 0.7
                    else:
                        return 0.3
                    

            # Unique to Tennis???
            elif pick_market == 'set spread':

                # Plus
                if re.search('\+', pick_bet):
                    # -inf < x <= -251
                    if pick_odds <= -251:
                        return 0.3
                    # -250 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.4 # 0.7
                        else:
                            return 0.3
                # Minus
                else:
                    # -inf < x <= -149
                    if pick_odds <= -149:
                        return 0.3
                    
                    # -148 <= x < inf
                    else:
                        if pick_source == 'betrivers':
                            return 0.4 # 1.5
                        else:
                            return 0.3

            elif pick_market == 'game spread':
                
                # Plus
                if re.search('\+', pick_bet):

                    # -inf < x <= +109
                    if pick_odds <= 109:
                        return 0.3
                    
                    # +110 <= x < inf
                    else:
                        if pick_source == 'fanatics':
                            return 0.4 # 1.4
                        else:
                            return 0.3
                # Minus
                else:
                    
                    return 0.3
                
            elif re.search('to win at least 1', pick_market):
                
                # -inf < x <= -211
                if pick_odds <= -211:
                    return 0.3
                
                # -210 <= x <= -161
                if pick_odds <= -161:
                    if pick_source == 'betmgm':
                        return 0.4 # 0.7
                    else:
                        return 0.3
                    
                # -160 <= x <= -101
                if pick_odds <= -101:
                    if pick_source == 'betmgm':
                        return 0.5 # 1.5
                    else:
                        return 0.3
                
                # +100 <= x < inf
                else:
                    if pick_source == 'betmgm':
                        return 0.6 # 2.9
                    else:
                        return 0.3
            
        else:
            
            print('Warning: Unknown Sport in determine min pick val! ' + pick_sport)

            
        

    # === Arb ===
    else: 
        # pick_odds1 = int(pick['odds1'])
        # pick_source1 = pick['source1']
        # pick_bet1 = pick['bet1']
        # pick_odds2 = int(pick['odds2'])
        # pick_source2 = pick['source2']
        # pick_bet2 = pick['bet2']

        limited_sources = ['betrivers', 'fanatics', 'betmgm']
        if pick['source1'] in limited_sources or pick['source2'] in limited_sources:
            min_pick_val = 2


    return min_pick_val


def determine_min_odds(pick):
    min_odds = -150

    # player props
    # batter runs > -167 betrivers
    pick_source = pick['source']
    pick_market = pick['market']

    pick_market_group = ''
    if re.search('-', pick_market):
        pick_market_group = pick_market.split(' - ')[1] # keep title format bc easier to read

    if pick_market_group == 'Runs' and pick_source == 'betrivers':
        min_odds = -168

    elif pick_market == 'Moneyline':
        min_odds = -226

    elif pick_market == 'Game Spread':
        min_odds = -171

    elif pick_market == 'Spread':
        min_odds = -205

    elif pick_market == 'Total':
        min_odds = -280
        if re.search('O', pick['bet']):
            min_odds = -250
        

    return min_odds

# list of criteria for valid bet
# depends on type of bettor: new user or limited user
def determine_valid_pick(pick, valid_sports, valid_leagues, limited_sources, new_pick_rules, init_picks, todays_date, pick_type='ev'):
    # print('\n===Determine Valid Pick===\n')
    # # print('Input: pick = {...} = ' + str(pick))
    # print('Input: init_picks = {0:{...},...} = ' + str(init_picks))
    # print('Input: valid_sports = ' + str(valid_sports))
    # print('Input: limited_sources = ' + str(limited_sources))
    # print('Input: new_pick_rules = ' + str(new_pick_rules))
    # print('\nOutput: valid = True or False\n')

    valid_pick = True

    
    pick_type_str = pick_type.title()
    if pick_type == 'ev':
        pick_type_str = pick_type.upper()

    # complex version:
    # check if existing game and market
    pick_game = pick['game'] #converter.convert_game_teams_to_abbrevs(pick['game'])
    #print('pick_game: ' + str(pick_game))

    # AVOID baseball player Home Run props 
    # bc most common market inefficiency so obvious honeypot
    pick_market = pick['market']#.lower() # do not lower here bc want title format to display and compare to saved picks
    # if re.search('Home Run', arb_market):
    # 	print('AVOID arb_market: ' + str(arb_market))
    # 	continue

    arb_source1 = arb_source2 = None
    if pick_type == 'arb':
        arb_source1 = pick['source1']
        arb_source2 = pick['source2']

    # For now we take all sports for +EV but only limited sources 
	# to avoid always beating closing line on unlimited sources
    pick_sport = pick['sport']
    pick_league = pick['league']

    if pick_type == 'arb':
        
        # avoid small leagues for unlimited sources
        # only allow small leagues for limited sources
        if pick_sport not in valid_sports or pick_league not in valid_leagues:
            if arb_source1 not in limited_sources or arb_source2 not in limited_sources:
                print('Avoid ' + pick_type + ' pick: ' + pick_market + ', sport league in unlimited source: ' + pick_sport.title() + ', ' + pick_league.title() + ', ' + arb_source1.title() + ', ' + arb_source2.title())
                return False
        
    
    #if valid_pick:
    # EV picks take any day but only limited sources
    # Arb picks check if game today
    # game_date_data = game_date_str.split()
    # game_mth = game_date_data[1]
    # game_day = game_date_data[2][:-1] # remove comma
    # game_date_str = game_mth + ' ' + game_day
    # print('game_date_str: ' + str(game_date_str))
    # # need month and day of month to check same day, assuming same yr for all
    # game_date = datetime.strptime(game_date_str, '%b %d')
    # print('game_date: ' + str(game_date))
    # if game_date != todays_date:
    # recently added date to arb row
    if pick_type == 'arb':
        # tue aug 24 2024
        game_date_str = pick['game date']
        game_date = datetime.strptime(game_date_str, '%a %b %d %Y').date()
        # print('game_date: ' + str(game_date))
        # print('todays_date: ' + str(todays_date))
        #if not re.search('Today', game_date):
        if game_date != todays_date:
            # if either side is unlimited source, 
            # avoid game not today bc suspicious
            # but if both sides already limited 
            # then need to take all available, even diff days
            if arb_source1 not in limited_sources or arb_source2 not in limited_sources:
                print('AVOID ' + pick_type + ' pick: ' + pick_market + ', Game Not Today: ' + pick_game.title() + ', ' + game_date_str)
                return False


    # if arb_game not in todays_schedule:
    # 	# check reverse away home teams bc sometimes labeled backwards
    # 	arb_game = (arb_game[1], arb_game[0])
    # 	if arb_game not in todays_schedule:
    # 		# if either side still not limited, avoid future games
    # 		# bc obvious red flag
    # 		if arb_bet1 not in limited_sources or arb_bet2 not in limited_sources:
    # 			print('AVOID arb_game: ' + str(arb_game))
    # 			continue

    

    

    # AVOID small markets
    # AVOID non-star role player props
    # especially low rebound numbers
    # How to tell if main player
    # for basketball, based on minutes or specific stat level
    # bc players may have large minutes but low rebounds or assists 
    # so still small market
    # So use specific stat level

    # === All Valid Picks
    # AVOID glitchy leagues

    pick_bet = ''
    if pick_type == 'ev':
        pick_bet = pick['bet']
    else:
        pick_bet = pick['bet1']

    # AVOID val too low bc not worth it
    # AVOID val too high bc glitch
    pick_val = float(pick['value'])
    #print('pick_val: ' + str(pick_val))
    if pick_val < new_pick_rules['min'] or pick_val > new_pick_rules['max']:
        print('AVOID ' + pick_type + ' pick: ' + pick_market + ', ' + pick_type_str + ' pick_val: ' + str(pick_val) + ', ' + pick_market.title() + ', ' + str(pick_bet))
        return False

    

    # === Valid EVs ===
    ev_hit_min_val = 2
    ev_small_market_min_val = 1 # % tune min val
    ev_big_market_min_val = 0.3
    ev_likely_hr_min_val = 0.8 # -2500 or lower
    # for less likely cases, require higher val???
    ev_ideal_min_val = 2 # if unlimited bankroll, what is ideal min val?
    ev_likely_odds = -275 # this or less is considered likely??? no bc it should be gradient???

    min_pick_val = determine_min_pick_val(pick, pick_type)

    if pick_type == 'ev':

        # Dont just account for odds
        # Also account for value so take high value at lower odds
        # AVOID odds > -150
        #pick_odds = int(pick['odds'])

        # min_odds = determine_min_odds(pick)
        # if pick_odds > min_odds: # -150
        #     print('AVOID EV pick_odds: ' + str(pick_odds) + ', ' + str(pick_market) + ', ' + str(pick_bet))
        #     return False

        # AVOID unlimited sources
        pick_source = pick['source']
        if pick_source not in limited_sources:
            print('AVOID ' + pick_type + ' pick: ' + pick_market + ', EV pick_source: ' + str(pick_source) + ', ' + str(pick_bet))
            return False
        
        # AVOID women's (and men's???) tennis on fanatics bc never actually available
        # if league starts or ends with 'w'
        # such as wta or itf (w)
        if pick_source == 'fanatics' and pick_sport == 'tennis' and re.search('^w|w\)$', pick_league):#and pick_league[0] == 'w':
            print('Avoid ' + pick_type + ' pick: ' + pick_market + ', Fanatics W Tennis: ' + pick_league)
            return False
        
        # Avoid betrivers soccer spread bc cannot find on page
        if pick_source == 'betrivers' and pick_sport == 'soccer' and re.search('Spread', pick_market):
            print('AVOID ' + pick_type + ' pick: ' + pick_market + ', Betrivers Soccer Spread: ' + str(pick_val) + ', ' + str(pick_bet))
            return False 

        # Avoid Betrivers college football player props bc not on page
        if pick_source == 'betrivers' and pick_league == 'ncaaf' and re.search(' - ', pick_market):
            print('AVOID ' + pick_type + ' pick: ' + pick_market + ', Betrivers NCAAF Player Prop: ' + str(pick_val) + ', ' + str(pick_bet))
            return False 

        # AVOID bet size < $3 bc not enough advantage???
        pick_size = pick['size']
        pick_float = float(pick_size.strip('$'))
        if pick_float < 2.5:
            print('AVOID ' + pick_type + ' pick: ' + pick_market + ', EV pick_size: ' + str(pick_size) + ', ' + str(pick_bet))
            return False

        # AVOID Betrivers Soccer Spread bc cannot find on page after thorough search
        # soccer_leagues = ['leagues cup']
        # if pick_source == 'betrivers' and pick['sport'] in soccer_leagues:
        #     print('AVOID EV Soccer Spread Betrivers: ' + str(pick_odds) + ', ' + str(pick_market) + ', ' + str(pick_bet))
        #     return False


        
        
        if pick_val < min_pick_val: 
            print('AVOID ' + pick_type + ' pick: ' + str(pick_market) + ', ' + str(pick_val) + ', ' + str(pick_bet))
            return False 

    # Arb
    else:

        # Avoid betrivers soccer spread bc cannot find on page
        if arb_source1 == 'betrivers' or arb_source2 == 'betrivers':
            if pick_sport == 'soccer' and re.search('Spread', pick_market):
                print('AVOID ' + pick_type + ' pick: ' + pick_market + ', Betrivers Soccer Spread: ' + str(pick_val) + ', ' + str(pick_bet))
                return False 
            

        # Avoid Caesars 2nd half bc only 3 way winner available
        if arb_source1 == 'caesars' or arb_source2 == 'caesars':
            if pick_league == 'ncaaf' and re.search('2nd Half', pick_market):
                print('AVOID ' + pick_type + ' pick: ' + pick_market + ', Caesars NCAAF 2nd Half: ' + str(pick_val) + ', ' + str(pick_bet))
                return False 


            # prematch only
            # ncaaf caesars no team totals prematch but yes live
            if pick_league == 'ncaaf' and re.search('\stotal', pick_market) and not re.search('quarter|half', pick_market):
                print('AVOID ' + pick_type + ' pick: ' + pick_market + ', Prematch Caesars NCAAF Team Total: ' + str(pick_val) + ', ' + str(pick_bet))
                return False 


    

    # if player prop, need higher min val to justify use 
    # but still allow home runs if already limited on other markets
    if pick_type == 'arb' and not re.search('Moneyline|Spread|Total|Home|Base', pick_market) and pick_val < new_pick_rules['player min']:
        print('AVOID ' + pick_type + ' pick: ' + pick_market + ', arb_val: ' + str(pick_val))
        return False


    # betrivers is usually off by 5 odds so need higher limit to avoid false alarm
    # if limited by betrivers only take >3%
    # EXCEPT big markets, moneyline, spread, total bc higher limits
    if pick_type == 'arb':
        if arb_source1 == 'betrivers' or arb_source2 == 'betrivers':
            # less limited markets such as home runs bc very extreme odds
            # so accept lower min bc invest more
            
            if pick_val < new_pick_rules['betrivers min'] and not re.search('Moneyline|Spread|Total|Home|Base', pick_market):
                print('AVOID ' + pick_type + ' pick: ' + pick_market + ', betrivers arb_val: ' + str(pick_val))
                return False


        # limited sites need higher val to be worth it
        if arb_source1 in limited_sources or arb_source2 in limited_sources:
            # allow if limit allows at least 10c profit on both sides???
            
            if pick_val < new_pick_rules['limited min'] and not re.search('Moneyline|Spread|Total|Home|Base', pick_market):
                print('AVOID ' + pick_type + ' pick: ' + pick_market + ', limited arb_val: ' + str(pick_val) + ', ' + arb_source1 + ', ' + arb_source2)
                #valid_pick = False
                return False

    # if still valid at this point, after passing checks,
    # check not already added
    if valid_pick:

        # Simply check log if already hit

        # OR

        # check all read possible picks and confirm also valid

        #print('\nCheck Same')
        # print('Pick: ' + str(pick))
        # print('min_pick_val: ' + str(min_pick_val))
        # AVOID picking same prop twice bc obvious strategy suspicious
        # also glitch where pick disappears and reappears for no reason
        same_pick = False
        for init_pick_id, init_pick_row in init_picks.items():
            # compare original game title, not abbrevs
            init_pick_game = init_pick_row['game'] #converter.convert_game_teams_to_abbrevs(init_pick_row['game'])
            init_pick_market = init_pick_row['market']
            init_pick_source = init_pick_source1 = init_pick_source2 =''
            if pick_type == 'ev':
                init_pick_source = init_pick_row['source']
            else:
                init_pick_source1 = init_pick_row['source1']
                init_pick_source2 = init_pick_row['source2']
            # print('\npick_game: ' + str(pick_game))
            # print('pick_market: ' + str(pick_market))
            # print('init_pick_game: ' + str(init_pick_game))
            # print('init_pick_market: ' + str(init_pick_market))
            # compare original game title, not abbrevs
            # source must match too bc if diff source may accept ev
            if pick_game == init_pick_game and pick_market == init_pick_market:
                #print('Found Matching Game and Market')
                # Do we take double down on other sources???
                # No bc the fact multiple sources agree means less value
                same_source = False
                # for now, for ev only take 1 source, assuming allowed up to limit
                # later combine sources up to desired size
                if pick_type == 'ev':# and pick_source == init_pick_source:
                    same_source = True
                elif pick_type == 'arb' and arb_source1 == init_pick_source1 and arb_source2 == init_pick_source2:
                    same_source = True
                
                if same_source:
                    #print('Same Source')
                    init_pick_val = init_pick_row['value']
                    #print(init_pick_id + ' init_pick_val: ' + str(init_pick_val))
                    # ' + str(init_pick_row))
                    
                    # if prev arb val already greater than min val we already took prop so do not double take
                    #min_val = determine_pick_min_val(pick, pick_type)

                    if float(init_pick_val) >= min_pick_val:
                        #print('Same Pick')
                        # print('\nFound Same ' + pick_type_str)
                        # print('pick_game: ' + str(pick_game))
                        # print('init_pick_game: ' + str(init_pick_game))
                        # print('pick_market: ' + str(pick_market))
                        # print('init_pick_market: ' + str(init_pick_market))
                        same_pick = True
                        break

            # else:
            #     # not same pick
            #     print('\n==DIFFERENT Pick===')
            #     print('pick_game: ' + str(pick_game))
            #     print('pick_market: ' + str(pick_market))
                    
        if same_pick:	
            
            print('AVOID same ' + pick_type_str + ' pick: ' + str(pick_val) + ', ' + str(pick_game) + ', ' + str(pick_market) + ', ' + str(pick_bet))
            # print('pick_game: ' + str(pick_game))
            # print('init_pick_game: ' + str(init_pick_game))
            # print('pick_market: ' + str(pick_market))
            # print('init_pick_market: ' + str(init_pick_market))
            return False

    # if valid_pick:
    #     print('Valid Pick')
    return valid_pick

# list of criteria for valid bet
# depends on type of bettor: new user or limited user
# def determine_valid_arb(arb, valid_sports, limited_sources, new_arb_rules, init_arbs):
#     print('\n===Determine Valid Arb===\n')
#     print('Input: arb = {...} = ' + str(arb))
#     print('Input: init_arbs = {0:{...},...} = ' + str(init_arbs))
#     print('Input: valid_sports = ' + str(valid_sports))
#     print('Input: limited_sources = ' + str(limited_sources))
#     print('\nOutput: valid = True or False\n')

#     valid_arb = True

#     val_idx = 0
#     game_idx = 1
#     market_idx = 2
#     bet1_idx = 3
#     bet2_idx = 4
#     game_date_idx = 11
#     sport_idx = 12

#     # complex version:
#     # check if existing game and market
#     arb_game = converter.convert_game_teams_to_abbrevs(arb['game'])
#     #print('arb_game: ' + str(arb_game))

#     arb_source1 = arb['source1']
#     arb_source2 = arb['source2']
#     print('arb_source1: ' + str(arb_source1))
#     print('arb_source2: ' + str(arb_source2))

#     sport = arb['sport']
#     print('sport: ' + str(sport))
#     if sport not in valid_sports:
#         if arb_source1 not in limited_sources or arb_source2 not in limited_sources:
#             print('Avoid sport: ' + sport)
#             valid_arb = False


#     # check if game today
#     # game_date_data = game_date_str.split()
#     # game_mth = game_date_data[1]
#     # game_day = game_date_data[2][:-1] # remove comma
#     # game_date_str = game_mth + ' ' + game_day
#     # print('game_date_str: ' + str(game_date_str))
#     # # need month and day of month to check same day, assuming same yr for all
#     # game_date = datetime.strptime(game_date_str, '%b %d')
#     # print('game_date: ' + str(game_date))
#     # if game_date != todays_date:
#     # recently added date to arb row
#     game_date = arb['game date']
#     #print('game_date: ' + game_date)
#     if not re.search('Today', game_date):
#         # if either side is unlimited source, 
#         # avoid game not today bc suspicious
#         # but if both sides already limited 
#         # then need to take all available, even diff days
#         if arb_source1 not in limited_sources or arb_source2 not in limited_sources:
#             print('AVOID Game Not Today: ' + str(arb_game) + ', ' + game_date)
#             valid_arb = False

#     # if arb_game not in todays_schedule:
#     # 	# check reverse away home teams bc sometimes labeled backwards
#     # 	arb_game = (arb_game[1], arb_game[0])
#     # 	if arb_game not in todays_schedule:
#     # 		# if either side still not limited, avoid future games
#     # 		# bc obvious red flag
#     # 		if arb_bet1 not in limited_sources or arb_bet2 not in limited_sources:
#     # 			print('AVOID arb_game: ' + str(arb_game))
#     # 			continue

#     # AVOID baseball player Home Run props 
#     # bc most common market inefficiency so obvious honeypot
#     arb_market = arb['market']
#     # if re.search('Home Run', arb_market):
#     # 	print('AVOID arb_market: ' + str(arb_market))
#     # 	continue

#     # AVOID small markets
#     # AVOID non-star role player props
#     # especially low rebound numbers
#     # How to tell if main player
#     # for basketball, based on minutes or specific stat level
#     # bc players may have large minutes but low rebounds or assists 
#     # so still small market
#     # So use specific stat level



    
#     # bc otherwise short term profit not worth long term loss due to obvious samples with edge
#     arb_val = float(arb['value'])
#     if arb_val < new_arb_rules['min'] or arb_val > new_arb_rules['max']:
#         print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
#         valid_arb = False

#     # if player prop, need higher min val to justify use 
#     # but still allow home runs if already limited on other markets
#     if not re.search('Moneyline|Spread|Total|Home|Base', arb_market) and arb_val < new_arb_rules['player min']:
#         print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
#         valid_arb = False


#     # betrivers is usually off by 5 odds so need higher limit to avoid false alarm
#     # if limited by betrivers only take >3%
#     # EXCEPT big markets, moneyline, spread, total bc higher limits
    
#     if arb_bet1 == 'betrivers' or arb_bet2 == 'betrivers':
#         # less limited markets such as home runs bc very extreme odds
#         # so accept lower min bc invest more
        
#         if arb_val < new_arb_rules['betrivers min'] and not re.search('Moneyline|Spread|Total|Home|Base', arb_market):
#             print('AVOID betrivers arb_val: ' + str(arb_val) + ', ' + str(arb_market))
#             valid_arb = False


#     # limited sites need higher val to be worth it
#     if arb_bet1 in limited_sources or arb_bet2 in limited_sources:
#         if arb_val < new_arb_rules['limited min'] and not re.search('Moneyline|Spread|Total|Home|Base', arb_market):
#             print('AVOID limited arb_val: ' + str(arb_val) + ', ' + str(arb_market))
#             valid_arb = False

#     # AVOID picking same prop twice bc obvious strategy suspicious
#     same_arb = False
#     for init_arb_row in init_arbs.values():
#         init_arb_game = converter.convert_game_teams_to_abbrevs(init_arb_row['game'])
#         init_arb_market = init_arb_row['market']
#         # print('\narb_game: ' + str(arb_game))
#         # print('arb_market: ' + str(arb_market))
#         # print('init_arb_game: ' + str(init_arb_game))
#         # print('init_arb_market: ' + str(init_arb_market))
#         if arb_game == init_arb_game and arb_market == init_arb_market:
#             init_arb_val = init_arb_row['value']
#             #print('init_arb_val: ' + str(init_arb_val))
#             # if prev arb val already greater than min val we already took prop so do not double take
#             if float(init_arb_val) > 2:
#                 #print('Found Same Arb')
#                 same_arb = True
#                 break
                
#     if same_arb:	
#         print('AVOID same arb: ' + str(arb_val) + ', ' + str(arb_game) + ', ' + str(arb_market))
#         valid_arb = False


#     return valid_arb


# double check init read odds from source
# given source oddsview and others will always have glitches 
# and may change bt init read and placing bet
# check that |+odds1| > |-odds2|
# if able to read actual odds 1 side 
# use that paired with assumed odds on manual side
def determine_valid_arb_odds(arb, updated_odds1='', updated_odds2=''):
    print('\n===Determine Valid Arb Odds==\n')
    # print('Input: arb = ' + str(arb))
    # # print('Input: odds1 = \'-x\' = ' + str(odds1))
    # # print('Input: odds2 = \'+x\' = ' + str(odds2))
    # print('\nOutput: valid arbs odds bool\n')

    valid_arb = False

    assumed_odds1 = arb['odds1']
    assumed_odds2 = arb['odds2']
    actual_odds1 = arb['actual odds1']
    actual_odds2 = ''
    if 'actual odds2' in arb.keys():
        actual_odds2 = arb['actual odds2']

    print('assumed_odds1: ' + str(assumed_odds1))
    print('assumed_odds2: ' + str(assumed_odds2))
    print('actual_odds1: ' + str(actual_odds1))
    print('actual_odds2: ' + str(actual_odds2))

    # if updated odds given, use it instead of actual odds
    # bc updated actual odds

    # neg_odds = real_odds[0]
    # pos_odds = real_odds[1]

    # if abs(neg_odds) < pos_odds:
    #     valid_arb = True

    odds1 = actual_odds1
    odds2 = actual_odds2
    if actual_odds1 == '':
        odds1 = assumed_odds1
    if actual_odds2 == '':
        odds2 = assumed_odds2

    # if given blank '' odds, then we cannot assume invalid
    # so say valid so it goes for manual review
    # actually better to use assumed odds bc usually odds will not change in favor
    print('odds1: ' + str(odds1))
    print('odds2: ' + str(odds2))

    try:
        odds1 = int(odds1)
        odds2 = int(odds2)
    except Exception as e:
        print('\nERROR: Failed to Read Odds\n')
        return False

    # if odds2 changed to negative then we know invalid
    if odds2 < 0:
        return False

    # if both sides positive, 
    # need at least 100 and 101
    if odds1 > 0: # >= +100
        # we know odds1 > 100
        # so if odds2 also >100 we know valid
        if odds2 >= 100:
            if odds1 > 100 or odds2 > 100:
                valid_arb = True
                print('Valid Arb')

    elif abs(odds1) < odds2:
        valid_arb = True
        print('Valid Arb')

    return valid_arb