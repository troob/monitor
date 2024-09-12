# Web Monitor for constantly updating websites

import reader, writer, isolator, determiner, time, beepy

import re, os

from slack_sdk import WebClient

from datetime import datetime

import pyautogui # screenshot
import cv2 # computer vision, screen record
from multiprocessing import Process # run while recording
import numpy as np # convert img to array

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

todays_date = datetime.today().date()



# === SETTINGS === 
# User Input
# When I am mobile, only send notifications that are valid
# so exclude limited sources
# BUT other ppl are not limited so we need different channels
# for limited sources, require higher profit to be worth it
limited_sources = ['betmgm', 'fanatics', 'betrivers']
sources = ['fanduel','fliff','draftkings','betrivers','caesars', 'fanatics', 'betmgm']
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
limited_min_val = 2.4
new_pick_rules = {'normal max': normal_max_val, 
				 'max': max_value, 
				 'min': min_value,
				 'player min': player_prop_min_val, 
				 'betrivers min': betrivers_min_val,
				 'limited min': limited_min_val}


valid_sports = ['baseball', 'football']#,'hockey', 'basketball] # big markets to stay subtle
valid_leagues = ['mlb', 'nfl', 'ncaaf'] # 10/8, 10/22

arb_type = 'pre' # all/both/options, live, OR prematch/pre

monitor_ev = True


# def record_screen():
# 	print('\n===Record Screen===\n')
# 	# Record Screen Specs
# 	# Specify resolution
# 	resolution = (1920, 1080)
	
# 	# Specify video codec
# 	codec = cv2.VideoWriter_fourcc(*"XVID")
	
# 	# Specify name of Output file
# 	filename = "data/Recording.avi"
	
# 	# Specify frames rate. We can choose any 
# 	# value and experiment with it
# 	fps = 60.0

# 	# Creating a VideoWriter object
# 	out = cv2.VideoWriter(filename, codec, fps, resolution)
	
# 	# Create an Empty window
# 	cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
	
# 	# Resize this window
# 	cv2.resizeWindow("Live", 480, 270)
	
# 	while True:
# 		# Take screenshot using PyAutoGUI
# 		img = pyautogui.screenshot()
	
# 		# Convert the screenshot to a numpy array
# 		frame = np.array(img)
	
# 		# Convert it from BGR(Blue, Green, Red) to
# 		# RGB(Red, Green, Blue)
# 		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	
# 		# Write it to the output file
# 		out.write(frame)
		
# 		# Optional: Display the recording screen
# 		#cv2.imshow('Live', frame)

# 		if stop_record:
# 			print('Stop Record')
# 			break

# 	# Release the Video writer
# 	out.release()
# 	# Destroy all windows
# 	cv2.destroyAllWindows()


# def read_and_place_bet(ev_row, ev_source, driver, pick_time_group, pick_type, monitor_idx, test):
# 	print('\n===Read and Place Bet===\n')

# 	actual_odds, final_outcome, cookies_file, saved_cookies = reader.read_actual_odds(ev_row, ev_source, driver, pick_time_group)
				
# 	# Next level: accept different as long as still less than fair odds
# 	pick_odds = ev_row['odds']
# 	if actual_odds != pick_odds:
# 		if actual_odds == '':
# 			print('\nNo Bet')
# 		# still accept better price
# 		elif int(actual_odds) < int(pick_odds):
# 			print('\nOdds Mismatch')
# 			print('init_odds: ' + ev_row['odds'])
# 			print('actual_odds: ' + actual_odds)
			

# 		driver.close()
# 		driver.switch_to.window(driver.window_handles[0])

# 		# stop recording before continuing to next bet
# 		stop_record = True
# 		print('Stop Record')

# 		#return # continue
# 	else:
# 		# continue to place bet
# 		# First notify users before placing bet
# 		print('\nPlace Bet')

# 		# only beep once on desktop after first arb so I can respond fast as possible
# 		# but send notification after each arb???
# 		# currently phone not used but ideally sends link to phone
# 		# so we want to handle one at a time ideally
# 		# so phone should get notice for each arb so it can start processing asap
# 		if valid_ev_idx == 0:
# 			ev_type = 'pre-match'
# 			say_str = 'say "' + ev_type + ' E.V."'
# 			os.system(say_str)
# 			# Also say if still need to check mobile only sources
# 			#os.system(say_mobile)
# 			print('\n' + str(monitor_idx) + ': Found New EVs')
			
			
# 		new_picks[valid_ev_idx] = ev_row
# 		valid_ev_idx += 1


# 		# notify before placing bet so other devices can start placing bets
# 		# format string to post
# 		writer.write_ev_to_post(ev_row, client, True)

# 		# === Place Bet === 
# 		# if actual odds is none then we know not enabled to place bet
# 		if actual_odds is not None:
# 			writer.place_bet(ev_row, ev_source, driver, final_outcome, cookies_file, saved_cookies, pick_type, test)
		
# 			# === Stop Recording after place bet ===
# 			stop_record = True
# 			print('Stop Record')



# input all EVs read this scan
# output only valid EVs into proper channels
# so diff users only see arbs that apply to them
def monitor_new_evs(ev_data, init_evs, new_ev_rules, monitor_idx, valid_sports, driver, test, pick_time_group='prematch', pick_type='ev'):
	# print('\n===Monitor New EVs===\n')
	# print('Input: ev_data = [[...],...]')# + str(ev_data))
	# print('\nOutput: new_evs = [[%, $, ...], ...]\n')

	ev_type = 'pre-match'
	say_str = 'say "' + ev_type + ' E.V."'

	# if just check diff then will alert when arb disappears
	# which we do not want
	new_picks = {}
	valid_ev_idx = 0
	#test_picks = []
	for ev_idx in range(len(ev_data)):
		ev_row = ev_data[ev_idx]

		# TEST
		#test_picks.append(ev_row)

        # instead of just checking if any diff
		# must be either 
		# 1. existing arb goes from below min val to above = Any Diff bc pick not added if below min val
		# 2. diff game and market
		if ev_row in init_evs.values():# and ev_row not in prev_ev_data:
			continue


		# all criteria
		#if not test: ensure test meets criteria
		# or else need to analyze test ev separate to run tests while running live odds
		if not determiner.determine_valid_pick(ev_row, valid_sports, valid_leagues, limited_sources, new_ev_rules, init_evs, todays_date):
			continue


		# === Check Real Odds === 
		# and pass driver/buttons to the writer
		
		# if mobile only, then do not open website
		# instead open emulator

		# TEST
		#ev_row = {'market': 'run line', 'bet': 'chi cubs -4', 'odds': '-175'}

		ev_source = ev_row['source']

		# Fanduel has bot blockers so take extra precaution
		# mobile_sources = ['Fanatics', 'Fliff', 'Fanduel']
		# if ev_source not in mobile_sources:
		# 	ev_bet = open_bet(ev_row, driver)
		# 	if ev_bet is False:
		# 		continue

		# Make sure source enabled
		enabled_sources = ['betrivers', 'betmgm'] # ['betmgm'] #
		# how can we tell if no odds bc they disappeared or just failed to read?
		# bc if fails to read will be set none
		
		cookies_file = 'data/cookies.json'
		saved_cookies = [] # init as blank bc will only get filled if enabled to read actual odds
		
		# can init blank '' bc if enabled auto source but na then will set None
		actual_odds = ''
		final_outcome = None

		if ev_source in enabled_sources:

			#actual_odds, final_outcome, cookies_file, saved_cookies = reader.read_actual_odds(ev_row, driver, pick_time_group, pick_type)
			actual_odds_data = reader.read_actual_odds(ev_row, driver, pick_time_group, pick_type)
			actual_odds = actual_odds_data[0]
			final_outcome = actual_odds_data[1]

		#if not test:
		# if actual odds is set none then we know not valid to place bet
		if actual_odds is None:
			continue
				
		# only beep once on desktop after first arb so I can respond fast as possible
		# but send notification after each arb
		if valid_ev_idx == 0:
			os.system(say_str)
			# Also say if still need to check mobile only sources
			#os.system(say_mobile)
			print('\n' + str(monitor_idx) + ': Found New EVs')
			
			
		new_picks[valid_ev_idx] = ev_row
		valid_ev_idx += 1


		# notify before placing bet so other devices can start placing bets
		# format string to post
		writer.write_ev_to_post(ev_row, client, True)


		# === Place Bet === 
		# if actual odds blank '' then we know valid pick but not enabled for auto pick so cannot place bet
		if actual_odds == '':
			continue
		
		writer.place_bet(ev_row, driver, final_outcome, cookies_file, saved_cookies, pick_type, test)
	


	return new_picks


# input all arbs read this scan
# output only valid arbs into proper channels
# so diff users only see arbs that apply to them
def monitor_new_arbs(arb_data, init_arbs, new_arb_rules, monitor_idx, valid_sports, driver, manual_arbs=False, test=False, pick_time_group='prematch', pick_type='arb'):
	# print('\n===Monitor New Arbs===\n')
	# print('Input: arb_data = [{...},...]')# + str(arb_data))
	# print('Input: init_arbs = {0:{...},...}')
	# print('\nOutput: new_arbs = [{%, $, ...}, ...]\n')

	arb_type = 'pre-match'
	say_str = 'say "' + arb_type + ' Arb"'
	
	# if just check diff then will alert when arb disappears
	# which we do not want
	new_picks = {}
	#test_picks = []
	valid_arb_idx = 0
	for arb_idx in range(len(arb_data)):
		arb_row = arb_data[arb_idx]

		# TEST
		#test_picks.append(arb_row)

        # instead of just checking if any diff
		# must be either 
		# 1. existing arb goes from below min val to above = Any Diff bc pick not added if below min val
		# 2. diff game and market
		# if no init arb data, then first loop so we eval all arbs
		# init_arb_data is None or ()
		if arb_row in init_arbs.values():# and arb_row not in prev_arb_data:
			continue

		# all criteria
		if not determiner.determine_valid_pick(arb_row, valid_sports, valid_leagues, limited_sources, new_arb_rules, init_arbs, todays_date, pick_type='arb'):
			continue


		# === Check Real Odds === 
		# and pass driver/buttons to the writer

		# either likely source valid hr enabled
		# OR both sources enabled

		market = arb_row['market'].lower()
		print('market: ' + market)

		arb_source1 = arb_row['source1']
		arb_source2 = arb_row['source2']

		final_outcome1 = None
		final_outcome2 = None
		final_outcomes = (final_outcome1, final_outcome2)
		
		actual_odds1 = actual_odds2 = ''
		#actual_odds = (actual_odds1, actual_odds2)

		cookies_file = 'data/cookies.json'
		saved_cookies = [] # init as blank bc will only get filled if enabled to read actual odds

		enabled_sources = ['betrivers', 'betmgm']
		bet1_dict = {}
		bet2_dict = {}

		# === If Treat As EV ===
		treat_ev = False
		# if valid home run ev arb
		# arb source 1 is always more likely
		if determiner.determine_valid_hr_ev_arb(market, arb_source1, arb_source2) and arb_source1 in enabled_sources:
			print('\nValid HR EV Arb\n')
			# treat as ev
			treat_ev = True

			# final outcome is bet btn if not already in betslip
			# bc no need to click if mismatched odds
			bet1_dict = arb_row
			bet1_dict['bet'] = arb_row['bet1']
			bet1_dict['odds'] = arb_row['odds1']
			bet1_dict['source'] = arb_row['source1']
			bet1_dict['link'] = arb_row['link1']
			bet1_dict['size'] = determiner.determine_source_limit(bet1_dict['source'])
			#actual_odds1, final_outcome1, cookies_file, saved_cookies = reader.read_actual_odds(bet1_dict, driver, pick_time_group, pick_type)
			actual_odds_data = reader.read_actual_odds(bet1_dict, driver, pick_time_group, pick_type='ev')
			actual_odds1 = actual_odds_data[0]
			final_outcome1 = actual_odds_data[1]

		# === If Treat As Arb ===
		else:
			print('\nTreat as Arb\n')

			# If both arbs enabled for auto, attempt to place both bets
			# if only 1 side enabled for auto, stop after find limit

			# 1. both arbs enabled
			# if arb_source1 in enabled_sources and arb_source2 in enabled_sources:
			# 	print('\nBoth Sides Auto Arb\n')

			# if arb_source1 in enabled_sources or arb_source2 in enabled_sources:
			# 	print('\nAuto Arb\n')

			# check first side to make sure odds still valid arb
			if arb_source1 in enabled_sources:
				print('\nAuto Check Side 1 Odds\n')
				bet1_dict = arb_row
				bet1_dict['bet'] = arb_row['bet1']
				bet1_dict['odds'] = arb_row['odds1']
				bet1_dict['source'] = arb_row['source1']
				bet1_dict['link'] = arb_row['link1']
				bet1_dict['size'] = determiner.determine_source_limit(bet1_dict['source'])

				# side num defines placement of window
				# actual_odds1, final_outcome1, cookies_file, saved_cookies = 
				actual_odds_data = reader.read_actual_odds(bet1_dict, driver, pick_time_group, pick_type, side_num=1)
				actual_odds1 = actual_odds_data[0]
				final_outcome1 = actual_odds_data[1]

				# if actual odds 1 = none then no need to check side 2
				if actual_odds1 is None:
					continue

			# even if first side changed, 
			# need to check second side to make sure invalid
			if arb_source2 in enabled_sources:
				print('\nAuto Check Side 2 Odds\n')
				bet2_dict = arb_row
				bet2_dict['bet'] = arb_row['bet2']
				bet2_dict['odds'] = arb_row['odds2']
				bet2_dict['source'] = arb_row['source2']
				bet2_dict['link'] = arb_row['link2']
				bet2_dict['size'] = determiner.determine_source_limit(bet2_dict['source'])

				# actual_odds2, final_outcome2, cookies_file, saved_cookies
				actual_odds_data = reader.read_actual_odds(bet2_dict, driver, pick_time_group, pick_type, side_num=2)
				actual_odds2 = actual_odds_data[0]
				final_outcome2 = actual_odds_data[1]

				# if actual odds 2 = none then invalid so continue
				if actual_odds2 is None:
					continue

			final_outcomes = (final_outcome1, final_outcome2)
			print('final_outcomes: ' + str(final_outcomes))

			# check if arb sides odds still valid
			# if + side 2 abs val > - side 1 abs val, then valid
			# if + side 2 abs val <= - side 1 abs val, then invlaid
			# if - side 1 abs val >= + side 2 abs val, then invalid
			#if abs(bet2_odds) <= bet1_odds:
			if not determiner.determine_valid_arb_odds(actual_odds1, actual_odds2):
				print('Arb Odds Changed to Invalid: ' + actual_odds1 + ', ' + actual_odds2)
				print('\nClose Both Arb Windows\n')
				# close last window, either idx 2 or 3
				driver.close()
				# if both odds auto read, 
				# also close third window, idx 2
				if actual_odds1 != '' and actual_odds2 != '':
					driver.switch_to.window(driver.window_handles[2])
					driver.close()
				# relinquish control to monitor window
				driver.switch_to.window(driver.window_handles[0])
				continue

			



		# if actual odds is set none then we know not valid to place bet
		if treat_ev and actual_odds1 is None:
			continue	


		# if actual odds is set none then we know not valid to place bet
		# already checked
		# if actual_odds1 is None or actual_odds2 is None:
		# 	continue

		# only beep once on desktop after first arb so I can respond fast as possible
		# but send notification after each arb
		if valid_arb_idx == 0:
			os.system(say_str)
			print('\n' + str(monitor_idx) + ': Found New Arbs')
			
			
		# add arb to new picks and go to next idx
		new_picks[valid_arb_idx] = arb_row
		valid_arb_idx += 1


		# notify before placing bet so other devices can start placing bets
		# format string to post
		writer.write_arb_to_post(arb_row, client, True)


		# === Place Bet === 
		# if actual odds blank '' then we know valid pick but not enabled for auto pick so cannot place bet
		if treat_ev and actual_odds1 == '':
			continue

		if treat_ev:
			writer.place_bet(bet1_dict, driver, final_outcome1, cookies_file, saved_cookies, pick_type, test)
		
		else: # Arb
			# If both sides auto, then place bets and continue
			# If neither side auto, then continue
			# If half auto, then find auto side limit
			# -If present, then wait for cmd to continue
			# -If absent, then continue

			# 1. both sides auto
			if actual_odds1 != '' and actual_odds2 != '':
				writer.place_arb_bets(arb_row, driver, final_outcomes, cookies_file, saved_cookies, pick_type, test)

			# 2. neither side auto, pass

			# 3. half auto

			# if 1 side actual odds is blank bc manual 
			# but other side auto read confirmed
			# then find limit on auto side
			# then keep auto window open but switch control to monitor window
			# if absent, we cannot handle manual part of half auto
			# so no need to find limit
			elif determiner.determine_half_auto(actual_odds1, actual_odds2) and manual_arbs:
				# find limit
				print('Find Auto Side Limit')
				

				# if able to manually place other side
				# keep open until manual cmd given

				# if auto only, then notify manual picks and continue

				print('Done Half Auto Arb')
				# give control to main window 
				# while waiting for user input to continue
				#driver.switch_to.window(driver.window_handles[0])

				# close window
				driver.close()
				# finally, switch back to main window
				driver.switch_to.window(driver.window_handles[0])

		# if onyl odds1 populated, then place single bet
		# if actual_odds2 == '' and treat_ev:
		# 	writer.place_bet(bet1_dict, driver, final_outcome1, cookies_file, saved_cookies, pick_type, test)
	
		# # if both odds given, then place both bets
		# else:
		# 	writer.place_arb_bets(arb_row, driver, final_outcomes, cookies_file, saved_cookies, pick_type, test)


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
	# if len(new_picks) > 0:
	# 	# format string to post
	# 	writer.write_arbs_to_post(new_picks, client, True)

	


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
# def open_arb_bets(arb):
# 	print('\n===Open Arb Bets===\n')
# 	print('\n===')
	
# 	notify_arb = None

# 	# if len(bets) > 0:
# 	# 	new_arb = bets[0]

# 	market_idx = 2
# 	bet1_idx = 3
# 	bet2_idx = 4
# 	link1_idx = 7
# 	link2_idx = 8

# 	arb_url1 = arb[link1_idx]
# 	arb_url2 = arb[link2_idx]



# 	if not re.search('fliff|fanatics', arb_url1):
# 		arb_driver1 = reader.open_react_website(arb_url1)
# 	# if not re.search('fliff|fanatics', arb_url2):
# 	# 	arb_driver2 = reader.open_react_website(arb_url2)

# 	bet1 = arb[bet1_idx]
# 	bet2 = arb[bet2_idx]
# 	neg_odds = reader.read_bet_odds(bet1, arb_driver1)
# 	#pos_odds = reader.read_bet_odds(bet2, arb_url2)

# 	neg_odds = -105 #arb_driver1.find_element('id', 'odds')
# 	pos_odds = 100 #arb_driver2

# 	# read odds direct from webpage
# 	real_odds = (neg_odds, pos_odds)

# 	# notify as soon as we know 1 is valid
# 	# so we can immediately take it and not waste time checking others
# 	# bc by the time we are done checking a lot the first 1 will be gone
# 	if determiner.determine_valid_arb_odds(real_odds):
# 		notify_arb = arb

# 	return notify_arb

# # open all arb windows at the same time
# # open, check, and close if false flag
# def open_new_arb_bets(new_arbs):
# 	print('\n===Open New Arb Bets===\n')
	
# 	notify_arbs = []
	
# 	for arb in new_arbs:
# 		notify_arb = open_arb_bets(arb)

# 		if notify_arb is not None:
# 			notify_arbs.append(notify_arb)


# open website once 
# and then loop over it 
# simulate human behavior to avoid getting blocked
def monitor_website(url, test, test_ev, absent=True, max_retries=3):
	print('\n===Monitor Website===\n')

	cur_yr = str(todays_date.year)
	#print('cur_yr: ' + cur_yr)

	# loop until keyboard interrupt
	retries = 0
	driver = None
	while retries < max_retries:
		try:

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



			


			# time.sleep(100) # wait before opening next page to seem human
			# cookies = driver.get_cookies()
			# print('cookies:\n' + str(cookies))

			# open new tabs for testing
			# so I can see live diff leagues and markets isolated
			# Window 2: Live Big Markets
			# OR TEST: see EVs 

			# === COMMENT OUT FOR TEST ===
			if not test:
				driver.switch_to.new_window()
				driver.get(url)
				time.sleep(1)

			# # # Window 3: Live Small Markets
			# # driver.switch_to.new_window()
			# # driver.get(url)
			# # time.sleep(1)

			driver.switch_to.window(driver.window_handles[0])

			# display all select elements
			# None Here which makes sense bc not shown in html
			# so try to get combobox
			# select_elements = driver.find_elements('xpath', '//button[@role="combobox"]')
			# print('Select Elements')
			# for se in select_elements:
			# 	print('select element: ' + se.get_attribute('outerHTML'))
			
			
			monitor_idx = 1

			# prev_arb_data = [] # first loop init=prev or None?
			# prev_ev_data = []

			# if arb_type == 'pre':
			# 	pre_btn.click()

			init_evs, init_arbs = reader.read_current_data(todays_date)

			# keep looping every 5 seconds for change
			while True:

				try:

					# DO we need to separate live and prematch in 2 files???
					# no bc just checking if any change overall
					# BUT we need to make diff notice for live vs prematch 
					# so we know which page to go to for link
					# arb_data_file = 'data/arb data.csv'
					# ev_data_file = 'data/ev data.csv' # todays_date not needed bc simply keep all in 1 file and remove rows of past games in first loop
					arbs_file = 'data/arbs.json'
					evs_file = 'data/evs.json'
					
					# if no file yet today, then delete file from yesterday
					# bc we know first loop
					# init_arb_data = reader.extract_data(arb_data_file, header=True)
					# init_ev_data = reader.extract_data(ev_data_file, header=True)
					# unique row for every item read today
					# including invalid picks
					# no duplicates
					#print('Read Init Picks')
					# first loop init as current data but after can read from json direct
					if monitor_idx != 1:
						init_arbs = reader.read_json(arbs_file)
						init_evs = reader.read_json(evs_file)	


					# only 1 file for efficiency but in file it separates live and prematch arbs
					# init_live_arb_data = init_arb_data[0]
					# init_prematch_arb_data = init_arb_data[1]

					# if monitor_idx == 1:
					# 	# print('init_arb_data: ' + str(init_arb_data))
					# 	# print('init_ev_data: ' + str(init_ev_data))
					# 	print('init_arbs: ' + str(init_arbs))
					# 	print('init_evs: ' + str(init_evs))

						# # simply keep all in 1 file and remove rows of past games in first loop
						# init_arbs = isolator.isolate_future_games(init_arbs, todays_date)
						# init_evs = isolator.isolate_future_games(init_evs, todays_date)

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
						# all arbs read this loop, incuding invalid picks
						arb_data = reader.read_prematch_arb_data(driver, pre_btn, arb_btn, cur_yr, sources)
						#arb_dict = reader.read_prematch_arb_dict(driver, pre_btn, arb_btn, sources)
					# live_arb_data = arb_data[0]
					# prematch_arb_data = arb_data[1]
					else: # both
						# read live twice before
						arb_data = reader.read_live_arb_data(driver, sources)#, todays_date)
					
					if arb_data == 'reboot':
						print('Reboot')
						driver.quit()
						break

					# if arb_data is None:
					# 	# exit
					# 	print('Arb Data None')
					# 	print('Exit')
					# 	exit()

					# if keyboard interrupt return blank so we know to break loop
					if arb_data == '':
						break

					if arb_data is not None:
					
						# monitor either live or pre, not both
						new_arbs = monitor_new_arbs(arb_data, init_arbs, new_pick_rules, monitor_idx, valid_sports, driver, manual_arbs, test)
						
						# new_live_arbs = new_arbs[0]
						# new_prematch_arbs = new_arbs[1]

						# could save all arb data or just new picks
						# to compare bt loops
						#prev_arb_data = init_arb_data # save last 2 in case glitch causes temp disappearance
						#writer.write_data_to_file(arb_data, arb_data_file) # becomes init next loop

						# init final arbs as init arbs in case no new arbs
						all_arbs = init_arbs
						# add uid for reference
						# 0 is first, N is last
						arb_idx = len(all_arbs)

						for arb in arb_data:
							if arb in all_arbs.values():
								#sprint('Found saved arb')
								continue
						
							all_arbs[arb_idx] = arb
							arb_idx += 1

						# for new_arb in new_arbs.values():
						# 	all_arbs[arb_idx] = new_arb
						# 	arb_idx += 1
						# save new arbs as json and remove if past
						writer.write_json_to_file(all_arbs, arbs_file)
					

					#open_all_arbs_bets(new_arbs)


					# === Monitor New +EV picks ===

					ev_data = reader.read_prematch_ev_data(driver, pre_btn, ev_btn, cur_yr, sources)
					if ev_data == 'reboot':
						print('Reboot')
						driver.quit()
						break

					# if ev_data is None:
					# 	# exit
					# 	print('EV Data None')
					# 	print('Exit')
					# 	exit()

					# === START TEST ===
					if test:
						# add test ev to actual data 
						# so we can test and run code at same time
						# If Test and Run same time
						#ev_data.append(test_ev)#[test_ev] 

						# If Only Test EV
						ev_data = [test_ev] 
					# === END TEST ===

					#print('ev_data: ' + str(ev_data))
					if ev_data == '': # if keyboard interrupt return blank so we know to break loop
						break
					if ev_data is not None:
						#try:
						new_evs = monitor_new_evs(ev_data, init_evs, new_pick_rules, monitor_idx, valid_sports, driver, test)
						# except KeyboardInterrupt:
						# 	print('Stop Monitor EVs')
						# prev_ev_data = init_ev_data # save last 2 in case glitch causes temp disappearance
						# writer.write_data_to_file(ev_data, ev_data_file) # becomes init next loop
					
						#print('init_evs: ' + str(init_evs))
						all_evs = init_evs
						ev_idx = len(all_evs)

						#print('ev_data: ' + str(ev_data))
						for ev in ev_data:
							if ev in all_evs.values():
								#print('Found saved ev')
								continue
						
							all_evs[ev_idx] = ev
							ev_idx += 1

						# save new evs as json and remove if past
						#print('all_evs: ' + str(all_evs))
						if not test:
							writer.write_json_to_file(all_evs, evs_file)


					monitor_idx += 1 # used only for first loop
					
					
					# see middle cookies
					# cookies = driver.get_cookies()
					# print('cookies: ', cookies)

					# creds = driver.get_credentials()
					# print('creds:', creds)


					# if prematch, keep looping every 5 seconds for change
					# if live, loop every 2 seconds bc fast change
					time.sleep(3) # 4 seems too slow bc can see change long before notice

				except KeyboardInterrupt:
					print('\nKeyboardInterrupt in Infinite Loop')
					print('Exit')
					exit()

			# if keyboard interrupt quit
			# then exit outer loop
			# if arb_data == '' or ev_data == '':
			# 	print('QUIT')
			# 	break



			# see final cookies
			# cookies = driver.get_cookies()
			# print('Final cookies: ', cookies)

			# creds = driver.get_credentials()
			# print('Final creds:', creds)

		except KeyboardInterrupt:
			print('\nKeyboardInterrupt in Monitor Website, outer loop')
			print('Exit')
			exit()
		except ConnectionResetError:
			print('\nKeyboardInterrupt in Monitor Website, outer loop')
			print('Exit')
			exit()

		# COMMENT OUT to see specific errors
		# except Exception as e:
		# 	print('Unknown Error while monitoring website: ', e)
		# 	driver.quit()
		# 	retries += 1




if __name__ == "__main__":
	# === TEST ===
	test = False
	test_ev = {'market':'Moneyline', 
				'bet':'Yoelvis Gomez', 
				'odds':'-2000', 
				'game':'Yoelvis Gomez',
				'sport':'football',
				'source':'betmgm',
				'league':'nfl',
				'value':'5.0',
				'size':'$3.00',
				'game date':'Thu Sep 5 2024',
				'link':'https://sports.ny.betmgm.com/en/sports/events/yoelvis-gomez-cub-diego-allan-ferreira-lablonski-16279417'}
	# test_ev = {'market':'Spread', 
	# 			'bet':'Washington Commanders -4', 
	# 			'odds':'+105', 
	# 			'game':'Washington Commanders vs Tampa Bay Buccaneers',
	# 			'source':'betmgm',
	# 			'sport':'football',
	# 			'league':'nfl',
	# 			'value':'5.0',
	# 			'size':'$3.00',
	# 			'game date':'Sat Sep 8 2024',
	# 			'link':'https://sports.ny.betmgm.com/en/sports/events/washington-commanders-at-tampa-bay-buccaneers-15830750'}
	# https://sports.ny.betmgm.com/en/sports/events/16114424?options=16114424-1161634470--963207266
	# https:...events/<game id>?options=<game id>- ... --<data-test-option-id>
	
	# test:
	# j kelly: https://sports.ny.betmgm.com/en/sports/events/16058791?options=16058791-1139065602--1022063921
	# https://sports.ny.betmgm.com/en/sports/events/16085726?options=16085726-1161494055--963549363
	# cain sandoval: https://sports.ny.betmgm.com/en/sports/events/16249580?options=16249580-1160456875--966257383
	# j canada rebounds: https://sports.ny.betmgm.com/en/sports/events/16085726?options=16085726-1161494055--963549363

	# test_ev = {'market':'Moneyline', 
	# 			'bet':'Paris Saint Germain', 
	# 			'odds':'-300', 
	# 			'game':'Paris Saint Germain',
	# 			'source':'betmgm',
	# 			'sport':'soccer',
	# 			'league':'mlb',
	# 			'value':'5.0',
	# 			'size':'$3.00',
	# 			'game date':'Thu Sep 14 2024',
	# 			'link':'https://sports.ny.betmgm.com/en/sports/events/2:6542108?options=2:6542108-164995050-560588838'}


	
	# if test:
	# 	print('\n===TEST===\n')
	# 	url = 'https://sports.ny.betmgm.com/en/sports/events/baltimore-ravens-at-kansas-city-chiefs-15817162'
	# 	driver = reader.open_react_website(url)
	# 	time.sleep(100)

	# diff from read react website bc we keep site open and loop read data
	# oodsview was free but now charges
	# So instead scrape sites directly
	url = 'https://www.oddsview.com/odds'
	#url = 'https://sportsbook.draftkings.com'
	# cannot do arbs fast enough if absent 
	# bc phone too slow and cannot see both sides at same time
	# so if absent, arbs with fully auto enabled get placed
	# but still notify? not needed 
	# but still log arb missed!!!
	# we can still handle manual ev bc one side is doable on mobile interface
	# best way is to assume manual arbs true
	# but as soon as i miss entering continue within 60s timer
	# then it switches to manual false (auto only)
	manual_arbs = True # Same as half auto arbs enabled = True. If user present, we can handle manual arbs bc of desktop interface
	monitor_website(url, test, test_ev, manual_arbs)