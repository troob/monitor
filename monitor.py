# Web Monitor for constantly updating websites

import reader, writer, converter, determiner, time, beepy

import re, os

from slack_sdk import WebClient

from datetime import datetime

# TEST
test = False



# send email
# email vs text: which is faster???
# email has 15 second delay at least
# import smtplib, ssl

# port = 465 # for ssl
# password = input("Password: ")

# # Create a secure SSL context
# context = ssl.create_default_context()


# store as environment variable
slack_token = os.environ["SLACK_TOKEN"]
#print(slack_token)
test_msg = 'test'
# set up webclient with slack oauth token
client = WebClient(token=slack_token)

todays_date = datetime.today()



# === SETTINGS === 
# User Input
# When I am mobile, only send notifications that are valid
# so exclude limited sources
# BUT other ppl are not limited so we need different channels
# for limited sources, require higher profit to be worth it
limited_sources = ['BetMGM', 'Fanatics', 'Betrivers']
sources = ['Fanduel','Fliff','Draftkings','Betrivers','Caesars', 'Fanatics', 'BetMGM']
big_market_min = 0.5 # sharper big market but can put more down
# on slow days, need to accept player props at 0.4 on unlimited sources
# sometimes betmgm-fanduel home runs are worth taking at 0.3%?
min_value = 0.3
ideal_min_value = 0.7 # when only few sports/games today, accept down to 0.8 for unlimited player props
player_prop_min_val = 0.4 #1.2 # take big markets at 1% but need slightly higher val to take player prop???
# if value too high then likely too temp to hit or read error so avoid
# sources differ so provide list
normal_max_val = 5
max_value = 7 # 5-10?
alt_max_val = 8
betrivers_min_val = 1.5
limited_min_val = 2.5
new_pick_rules = {'normal max': normal_max_val, 
				 'max': max_value, 
				 'min': min_value,
				 'player min': player_prop_min_val, 
				 'betrivers min': betrivers_min_val,
				 'limited min': limited_min_val}


valid_sports = ['mlb']#,'hockey'] # big markets to stay subtle
arb_type = 'pre' # all/both/options, live, OR prematch/pre
monitor_ev = True

# Indexes for Data Scraped from Web
val_idx = 0
game_idx = 1
game_date_idx = 2
market_idx = 3
bet_idx = 4
odds_idx = 5
size_idx = 6
link_idx = 7
source_idx = 8




# Open the website on the bet page
# And navigate to bet if no direct link
def open_bet(ev_row, driver):
	print('\n===Open Bet===\n')
	print('Input: ev_row = ' + str(ev_row))
	print('\nOutput: ev_bet = [odds, size]\n')

	ev_bet = False

	link_idx = 7

	ev_url = ev_row[link_idx]

	# get size of window 1 to determine window 2 x
	size = driver.get_window_size()

	driver.switch_to.new_window(type_hint='window')
	window2_x = size['width'] + 1
	driver.set_window_position(window2_x, 0)
	driver.get(ev_url)

	# if real odds match source odds
	# then valid ev bet

	# to avoid detection
	# only open 1 window at a time
	# and close before opening new one on same source
	time.sleep(30) # wait before opening next page to seem human
	driver.close()

	print('ev_bet: ' + str(ev_bet))
	return ev_bet


# input all EVs read this scan
# output only valid EVs into proper channels
# so diff users only see arbs that apply to them
def monitor_new_evs(ev_data, init_ev_data, prev_ev_data, new_ev_rules, monitor_idx, valid_sports, driver):
	# print('\n===Monitor New EVs===\n')
	# print('Input: ev_data = [[...],...]')# + str(ev_data))
	# print('\nOutput: new_evs = [[%, $, ...], ...]\n')

	ev_type = 'pre-match'
	say_str = 'say "' + ev_type + ' E.V."'
	
	# if just check diff then will alert when arb disappears
	# which we do not want
	new_picks = []
	test_picks = []
	valid_ev_idx = 0
	for ev_idx in range(len(ev_data)):
		ev_row = ev_data[ev_idx]

		# TEST
		test_picks.append(ev_row)

        # instead of just checking if any diff
		# must be either 
		# 1. existing arb goes from below min val to above = Any Diff bc pick not added if below min val
		# 2. diff game and market
		if ev_row not in init_ev_data and ev_row not in prev_ev_data:


			# all criteria
			if not determiner.determine_valid_pick(ev_row, valid_sports, limited_sources, new_ev_rules, init_ev_data):
				continue


			# === Check Real Odds === 
			# only needed bc source is flawed but since opening window here, leave it open
			# and pass drivers to the writer
			# if not determiner.determine_valid_arb_odds(arb_row):
			# 	continue
			# INSTEAD of checking valid odds and closing window
			# simply check odds and return no arb if invalid
			# close window if invalid
			# we want to get the drivers for each website
			# so we can read info and press btns next step
			# return no arb bets if invalid odds
			# so we do not proceed to next step
			# and continue to next arb
			
			# if mobile only, then do not open website
			# instead open emulator
			ev_source = ev_row[source_idx]
			mobile_sources = ['Fanatics', 'Fliff']
			if ev_source not in mobile_sources:
				ev_bet = open_bet(ev_row, driver)
				if ev_bet is False:
					continue

			# only beep once on desktop after first arb so I can respond fast as possible
			# but send notification after each arb???
			# currently phone not used but ideally sends link to phone
			# so we want to handle one at a time ideally
			# so phone should get notice for each arb so it can start processing asap
			if valid_ev_idx == 0:
				os.system(say_str)
				# Also say if still need to check mobile only sources
				#os.system(say_mobile)
				print('\n' + str(monitor_idx) + ': Found New EVs')
				valid_ev_idx += 1


			# === Place Bet === 
			# to get limits
			# and then see min payout
			# and then calc other side based on limit on side with min payout
			# writer.place_arb_bets(arb_bets)

			# # format string to post
			# writer.write_arb_to_post(arb_row, client, True)

			# CHANGE so instead of batching
			# handle each arb 1 at a time to be as fast as possible
			# simple version: if any diff, notify
			# so open both side bet windows, check if valid
			# and then notify
			# and then fill in bet size (test limit and calc bet sizes)
			# and then keep those windows open
			# and move to the next arb
			new_picks.append(ev_row)

	# notify immediately after reading new live arbs
	# before checking prematch


	# Complete 1 Arb at a Time
	# Do NOT batch bc it is better to get 1 than 0
	# after getting new picks from oddsview source
	# open bet links in new windows
	# and if passes check then add to list of new picks to notify
	#notify_picks = open_new_arb_bets(new_picks)

	# notify user after opening and checking
	# BUT before placing bet
	# check 2 prev arb tables bc sometimes disappear and reappear so not new
	#if len(prematch_arb_data) > 0 and init_prematch_arb_data != prematch_arb_data and prev_prematch_arb_data != prematch_arb_data:
	if len(new_picks) > 0:

		# format string to post
		writer.write_evs_to_post(new_picks, client, True)

	


	return new_picks


# input all arbs read this scan
# output only valid arbs into proper channels
# so diff users only see arbs that apply to them
def monitor_new_arbs(arb_data, init_arb_data, prev_arb_data, new_arb_rules, monitor_idx, valid_sports):
	# print('\n===Monitor New Arbs===\n')
	# print('Input: arb_data = [[...],...]')# + str(arb_data))
	# print('\nOutput: new_arbs = [[%, $, ...], ...]\n')

	arb_type = 'pre-match'
	say_str = 'say "' + arb_type + ' Arb"'
	
	# if just check diff then will alert when arb disappears
	# which we do not want
	new_picks = []
	test_picks = []
	valid_arb_idx = 0
	for arb_idx in range(len(arb_data)):
		arb_row = arb_data[arb_idx]

		# TEST
		test_picks.append(arb_row)

        # instead of just checking if any diff
		# must be either 
		# 1. existing arb goes from below min val to above = Any Diff bc pick not added if below min val
		# 2. diff game and market
		if arb_row not in init_arb_data and arb_row not in prev_arb_data:


			# all criteria
			if not determiner.determine_valid_arb(arb_row, valid_sports, limited_sources, new_arb_rules, init_arb_data):
				continue


			# === Check Real Odds === 
			# only needed bc source is flawed but since opening window here, leave it open
			# and pass drivers to the writer
			# if not determiner.determine_valid_arb_odds(arb_row):
			# 	continue
			# INSTEAD of checking valid odds and closing window
			# simply check odds and return no arb if invalid
			# close window if invalid
			# we want to get the drivers for each website
			# so we can read info and press btns next step
			# return no arb bets if invalid odds
			# so we do not proceed to next step
			# and continue to next arb
			# arb_bets = open_arb_bets(arb_row)

			# if len(arb_bets) == 0:
			# 	continue

			# only beep once on desktop after first arb so I can respond fast as possible
			# but send notification after each arb???
			# currently phone not used but ideally sends link to phone
			# so we want to handle one at a time ideally
			# so phone should get notice for each arb so it can start processing asap
			if valid_arb_idx == 0:
				os.system(say_str)
				print('\n' + str(monitor_idx) + ': Found New Arbs')
				valid_arb_idx += 1


			# === Place Bets === 
			# to get limits
			# and then see min payout
			# and then calc other side based on limit on side with min payout
			# writer.place_arb_bets(arb_bets)

			# # format string to post
			# writer.write_arb_to_post(arb_row, client, True)

			# CHANGE so instead of batching
			# handle each arb 1 at a time to be as fast as possible
			# simple version: if any diff, notify
			# so open both side bet windows, check if valid
			# and then notify
			# and then fill in bet size (test limit and calc bet sizes)
			# and then keep those windows open
			# and move to the next arb
			new_picks.append(arb_row)

	# notify immediately after reading new live arbs
	# before checking prematch


	# Complete 1 Arb at a Time
	# Do NOT batch bc it is better to get 1 than 0
	# after getting new picks from oddsview source
	# open bet links in new windows
	# and if passes check then add to list of new picks to notify
	#notify_picks = open_new_arb_bets(new_picks)

	# notify user after opening and checking
	# BUT before placing bet
	# check 2 prev arb tables bc sometimes disappear and reappear so not new
	#if len(prematch_arb_data) > 0 and init_prematch_arb_data != prematch_arb_data and prev_prematch_arb_data != prematch_arb_data:
	if len(new_picks) > 0:
		#beepy.beep() # first notify so i can get moving
		#say_str = 'say "Go Fuck Yourself."'
		# list each arb details
		# arb_type = 'pre-match'
		# say_str = 'say "' + arb_type + ' pick"'
		# os.system(say_str)

		# print('\n' + str(monitor_idx) + ': Found New Picks')


		# post_arbs = []
		# for pick in new_picks:
		# 	arb_market = pick[market_idx]
		# 	if not re.search('Home Run', arb_market):
		# 		post_arbs.append(pick)



		# format string to post
		writer.write_arbs_to_post(new_picks, client, True)

	


	return new_picks

# use time of day to tell arb type
# if before first game, only pre
# if after last game started, only live
# else both
def monitor_arb_type(first_live_time, last_pre_time):
	# print('\n===Monitor Arb Type===\n')
	# print('first_live_time: ' + str(first_live_time))
	# print('last_pre_time: ' + str(last_pre_time))

	arb_type = 'pre'

	current_time = datetime.today().time()
	#print("current_time: " + str(current_time))

	if current_time > last_pre_time:
		arb_type = 'live'
	elif current_time > first_live_time:
		arb_type = 'all'

	#print('arb_type: ' + arb_type)
	return arb_type



# why does vol and freq setting not work???
# beepy.volume = 0.5
# beepy.frequency = 1

# already init on live arb page
#print('pre_btn: ' + pre_btn.get_attribute('innerHTML'))
# if arb_type == 'pre':
# 	pre_btn.click()

# need sleep to load dynamic data otherwise blank
#time.sleep(1)

# open, check, and close if false flag
# open all picks in separate windows
# and automate as much as possible to place bets
#for new_arb in new_arbs:
# TEST 1
def open_arb_bets(arb):
	print('\n===Open Arb Bets===\n')
	print('\n===')
	
	notify_arb = None

	# if len(bets) > 0:
	# 	new_arb = bets[0]

	market_idx = 2
	bet1_idx = 3
	bet2_idx = 4
	link1_idx = 7
	link2_idx = 8

	arb_url1 = arb[link1_idx]
	arb_url2 = arb[link2_idx]



	if not re.search('fliff|fanatics', arb_url1):
		arb_driver1 = reader.open_react_website(arb_url1)
	# if not re.search('fliff|fanatics', arb_url2):
	# 	arb_driver2 = reader.open_react_website(arb_url2)

	bet1 = arb[bet1_idx]
	bet2 = arb[bet2_idx]
	neg_odds = reader.read_bet_odds(bet1, arb_driver1)
	#pos_odds = reader.read_bet_odds(bet2, arb_url2)

	neg_odds = -105 #arb_driver1.find_element('id', 'odds')
	pos_odds = 100 #arb_driver2

	# read odds direct from webpage
	real_odds = (neg_odds, pos_odds)

	# notify as soon as we know 1 is valid
	# so we can immediately take it and not waste time checking others
	# bc by the time we are done checking a lot the first 1 will be gone
	if determiner.determine_valid_arb_odds(real_odds):
		notify_arb = arb

	return notify_arb

# open all arb windows at the same time
# open, check, and close if false flag
def open_new_arb_bets(new_arbs):
	print('\n===Open New Arb Bets===\n')
	
	notify_arbs = []
	
	for arb in new_arbs:
		notify_arb = open_arb_bets(arb)

		if notify_arb is not None:
			notify_arbs.append(notify_arb)


# open website once 
# and then loop over it 
# simulate human behavior to avoid getting blocked
def monitor_website(url):

	# include game times so we can find first and last
	# only need to read once per day, not every run
	# save team list and times separately
	# bc diff formats and we only need to get times once per day
	# todays_schedule_file = 'data/todays schedule.csv'
	# game_time_file = 'data/game times.txt' # first, last
	# init_todays_schedule = reader.extract_data(todays_schedule_file, header=True)
	# todays_schedule = reader.read_todays_schedule(sports)
	# game_teams = todays_schedule[0]
	# first_live_time = todays_schedule[1] # first game start
	# last_pre_time = todays_schedule[2] # last game start

	# get website driver all elements
	# and specific navigation buttons which remain on screen the whole time
	# no matter which page you navigate to
	website = reader.open_dynamic_website(url)
	# need to switch bt live and prematch on same page
	driver = website[0]
	arb_btn = website[1]
	pre_btn = website[2]
	ev_btn = website[3]

	# open new tabs for testing
	# so I can see live diff leagues and markets isolated
	# Window 2: Live Big Markets
	# OR TEST: see EVs 
	driver.switch_to.new_window()
	driver.get(url)
	time.sleep(1)

	# # Window 3: Live Small Markets
	# driver.switch_to.new_window()
	# driver.get(url)
	# time.sleep(1)

	driver.switch_to.window(driver.window_handles[0])

	monitor_idx = 1

	prev_arb_data = [] # first loop init=prev or None?
	prev_ev_data = []

	# if arb_type == 'pre':
	# 	pre_btn.click()

	# keep looping every 5 seconds for change
	while True:

		# DO we need to separate live and prematch in 2 files???
		# no bc just checking if any change overall
		# BUT we need to make diff notice for live vs prematch 
		# so we know which page to go to for link
		arb_data_file = 'data/arb data.csv'
		ev_data_file = 'data/ev data.csv'
		init_arb_data = reader.extract_data(arb_data_file, header=True)
		init_ev_data = reader.extract_data(ev_data_file, header=True)

		# only 1 file for efficiency but in file it separates live and prematch arbs
		# init_live_arb_data = init_arb_data[0]
		# init_prematch_arb_data = init_arb_data[1]

		if monitor_idx == 1:
			print('init_arb_data: ' + str(init_arb_data))
			print('init_ev_data: ' + str(init_ev_data))


		# use time of day to tell arb type
		# if before first game, only pre
		# if after last game started, only live
		# else both
		#arb_type = monitor_arb_type(first_live_time, last_pre_time)
		
		# first check Live and then Prematch
		# notify bt each so no delay for live arbs
		# read either live or pre, not both
		# === Monitor New Arb picks ===

		arb_data = []
		if arb_type == 'live':
			# if on pre-page, click live btn
			# init on live page so not extra btn to press
			arb_data = reader.read_live_arb_data(driver, sources)#, todays_date)
		elif arb_type == 'pre':
			# if on live-page, click pre btn
			arb_data = reader.read_prematch_arb_data(driver, pre_btn, arb_btn, sources)
		# live_arb_data = arb_data[0]
		# prematch_arb_data = arb_data[1]
		else: # both
			# read live twice before
			arb_data = reader.read_live_arb_data(driver, sources)#, todays_date)
		

		# if keyboard interrupt return blank so we know to break loop
		if arb_data == '':
			break

		if arb_data is not None:
		
			# monitor either live or pre, not both
			new_arbs = monitor_new_arbs(arb_data, init_arb_data, prev_arb_data, new_pick_rules, monitor_idx, valid_sports)
			
			# new_live_arbs = new_arbs[0]
			# new_prematch_arbs = new_arbs[1]

			# could save all arb data or just new picks
			# to compare bt loops
			prev_arb_data = init_arb_data # save last 2 in case glitch causes temp disappearance
			writer.write_data_to_file(arb_data, arb_data_file) # becomes init next loop


		

		#open_all_arbs_bets(new_arbs)


		# === Monitor New +EV picks ===

		ev_data = reader.read_prematch_ev_data(driver, pre_btn, ev_btn, sources)
		
		if ev_data == '': # if keyboard interrupt return blank so we know to break loop
			break
		if ev_data is not None:
			new_evs = monitor_new_evs(ev_data, init_ev_data, prev_ev_data, new_pick_rules, monitor_idx, valid_sports, driver)
			prev_ev_data = init_ev_data # save last 2 in case glitch causes temp disappearance
			writer.write_data_to_file(ev_data, ev_data_file) # becomes init next loop
		


		monitor_idx += 1 # used only for first loop
		
		
		# see middle cookies
		# cookies = driver.get_cookies()
		# print('cookies: ', cookies)

		# creds = driver.get_credentials()
		# print('creds:', creds)


		# if prematch, keep looping every 5 seconds for change
		# if live, loop every 2 seconds bc fast change
		time.sleep(4)



	# see final cookies
	# cookies = driver.get_cookies()
	# print('Final cookies: ', cookies)

	# creds = driver.get_credentials()
	# print('Final creds:', creds)



# diff from read react website bc we keep site open and loop read data
# oodsview was free but now charges
# So instead scrape sites directly
url = 'https://www.oddsview.com/odds'
#url = 'https://sportsbook.draftkings.com'
monitor_website(url)