# Web Monitor for constantly updating websites

import reader, writer, converter, time, beepy

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
min_value = 0.4
ideal_min_value = 0.7 # when only few sports/games today, accept down to 0.8 for unlimited player props
player_prop_min_val = min_value #1.2 # take big markets at 1% but need slightly higher val to take player prop???
# if value too high then likely too temp to hit or read error so avoid
# sources differ so provide list
normal_max_val = 5
max_value = 7 # 5-10?
alt_max_val = 8
betrivers_min_val = 1.5
limited_min_val = 2.5
new_arb_rules = {'normal max': normal_max_val, 
				 'max': max_value, 
				 'min': min_value,
				 'player min': player_prop_min_val, 
				 'betrivers min': betrivers_min_val,
				 'limited min': limited_min_val}


sports = ['baseball']#,'hockey'] # big markets to stay subtle
arb_type = 'pre' # all/both/options, live, OR prematch/pre
monitor_ev = True



# input all arbs read this scan
# output only valid arbs into proper channels
# so diff users only see arbs that apply to them
def monitor_new_evs(ev_data, init_ev_data, prev_ev_data, todays_schedule, new_ev_rules, monitor_idx):
	# print('\n===Monitor New EVs===\n')
	# print('Input: arb_data = [[...],...]')# + str(arb_data))
	# print('\nOutput: new_arbs = [[%, $, ...], ...]\n')

	val_idx = 0
	game_idx = 1
	market_idx = 2
	bet1_idx = 3
	bet2_idx = 4
	odds1_idx = 5
	odds2_idx = 6
	link1_idx = 7
	link2_idx = 8

	# if just check diff then will alert when arb disappears
	# which we do not want
	new_pick = False
	new_picks = []
	test_picks = []
	for ev_row in ev_data:

		# TEST
		test_picks.append(ev_row)

        # instead of just checking if any diff
		# must be either 
		# 1. existing arb goes from below min val to above = Any Diff bc pick not added if below min val
		# 2. diff game and market
		if ev_row not in init_ev_data and ev_row not in prev_ev_data:
			
			


			
			# complex version:
			# check if existing game and market
			arb_game = converter.convert_game_teams_to_abbrevs(ev_row[game_idx])
			#print('arb_game: ' + str(arb_game))

			arb_bet1 = ev_row[bet1_idx]
			arb_bet2 = ev_row[bet2_idx]


			# check if game today
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
			game_date = ev_row[game_date_idx]
			#print('game_date: ' + game_date)
			if not re.search('Today', game_date):
				# if either side is unlimited source, 
				# avoid game not today bc suspicious
				# but if both sides already limited 
				# then need to take all available, even diff days
				if arb_bet1 not in limited_sources or arb_bet2 not in limited_sources:
					print('AVOID Game Not Today: ' + str(arb_game) + ', ' + game_date)
					continue

			if arb_game not in todays_schedule:
				# check reverse away home teams bc sometimes labeled backwards
				arb_game = (arb_game[1], arb_game[0])
				if arb_game not in todays_schedule:
					# if either side still not limited, avoid future games
					# bc obvious red flag
					if arb_bet1 not in limited_sources or arb_bet2 not in limited_sources:
						print('AVOID arb_game: ' + str(arb_game))
						continue

			# AVOID baseball player Home Run props 
			# bc most common market inefficiency so obvious honeypot
			arb_market = ev_row[market_idx]
			# if re.search('Home Run', arb_market):
			# 	print('AVOID arb_market: ' + str(arb_market))
			# 	continue

			# AVOID small markets
			# AVOID non-star role player props
			# especially low rebound numbers
			# How to tell if main player
			# for basketball, based on minutes or specific stat level
			# bc players may have large minutes but low rebounds or assists 
			# so still small market
			# So use specific stat level



			
			# bc otherwise short term profit not worth long term loss due to obvious samples with edge
			arb_val = float(ev_row[val_idx])
			if arb_val < new_arb_rules['min'] or arb_val > new_arb_rules['max']:
				print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
				continue

			# if player prop, need higher min val to justify use 
			# but still allow home runs if already limited on other markets
			if not re.search('Moneyline|Spread|Total|Home', arb_market) and arb_val < new_arb_rules['player min']:
				print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
				continue


			# Betrivers is usually off by 5 odds so need higher limit to avoid false alarm
			# if limited by betrivers only take >3%
			# EXCEPT big markets, moneyline, spread, total bc higher limits
			
			if arb_bet1 == 'Betrivers' or arb_bet2 == 'Betrivers':
				# less limited markets such as home runs bc very extreme odds
				# so accept lower min bc invest more
				
				if arb_val < new_arb_rules['betrivers min'] and not re.search('Moneyline|Spread|Total|Home', arb_market):
					print('AVOID Betrivers arb_val: ' + str(arb_val) + ', ' + str(arb_market))
					continue


			# limited sites need higher val to be worth it
			if arb_bet1 in limited_sources or arb_bet2 in limited_sources:
				if arb_val < new_arb_rules['limited min'] and not re.search('Moneyline|Spread|Total|Home', arb_market):
					print('AVOID limited arb_val: ' + str(arb_val) + ', ' + str(arb_market))
					continue

			# AVOID picking same prop twice bc obvious strategy suspicious
			same_arb = False
			for init_arb_row in init_ev_data:
				init_arb_game = converter.convert_game_teams_to_abbrevs(init_arb_row[game_idx])
				init_arb_market = init_arb_row[market_idx]
				# print('\narb_game: ' + str(arb_game))
				# print('arb_market: ' + str(arb_market))
				# print('init_arb_game: ' + str(init_arb_game))
				# print('init_arb_market: ' + str(init_arb_market))
				if arb_game == init_arb_game and arb_market == init_arb_market:
					init_arb_val = init_arb_row[val_idx]
					#print('init_arb_val: ' + str(init_arb_val))
					# if prev arb val already greater than min val we already took prop so do not double take
					if float(init_arb_val) > 2:
						#print('Found Same Arb')
						same_arb = True
						break
						
			if same_arb:	
				print('AVOID same arb: ' + str(arb_val) + ', ' + str(arb_game) + ', ' + str(arb_market))
				continue

			# simple version: if any diff, notify
			new_picks.append(ev_row)

	# notify immediately after reading new live arbs
	# before checking prematch

	# check 2 prev arb tables bc sometimes disappear and reappear so not new
	#if len(prematch_arb_data) > 0 and init_prematch_arb_data != prematch_arb_data and prev_prematch_arb_data != prematch_arb_data:
	if len(new_picks) > 0:
		#beepy.beep() # first notify so i can get moving
		#say_str = 'say "Go Fuck Yourself."'
		# list each arb details
		ev_type = 'pre-match'
		say_str = 'say "' + ev_type + ' EV pick"'
		os.system(say_str)

		print('\n' + str(idx) + ': Found New +EV Picks')


		# post_arbs = []
		# for pick in new_picks:
		# 	arb_market = pick[market_idx]
		# 	if not re.search('Home Run', arb_market):
		# 		post_arbs.append(pick)



		# format string to post
		writer.write_evs_to_post(new_picks, client, True)

	


	return new_picks


# input all arbs read this scan
# output only valid arbs into proper channels
# so diff users only see arbs that apply to them
def monitor_new_arbs(arb_data, init_arb_data, prev_arb_data, todays_schedule, new_arb_rules, monitor_idx):
	# print('\n===Monitor New Arbs===\n')
	# print('Input: arb_data = [[...],...]')# + str(arb_data))
	# print('\nOutput: new_arbs = [[%, $, ...], ...]\n')

	val_idx = 0
	game_idx = 1
	market_idx = 2
	bet1_idx = 3
	bet2_idx = 4
	game_date_idx = 11

	# if just check diff then will alert when arb disappears
	# which we do not want
	new_pick = False
	new_picks = []
	test_picks = []
	for arb_row in arb_data:

		# TEST
		test_picks.append(arb_row)

        # instead of just checking if any diff
		# must be either 
		# 1. existing arb goes from below min val to above = Any Diff bc pick not added if below min val
		# 2. diff game and market
		if arb_row not in init_arb_data and arb_row not in prev_arb_data:
			
			


			
			# complex version:
			# check if existing game and market
			arb_game = converter.convert_game_teams_to_abbrevs(arb_row[game_idx])
			#print('arb_game: ' + str(arb_game))

			arb_bet1 = arb_row[bet1_idx]
			arb_bet2 = arb_row[bet2_idx]


			# check if game today
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
			game_date = arb_row[game_date_idx]
			#print('game_date: ' + game_date)
			if not re.search('Today', game_date):
				# if either side is unlimited source, 
				# avoid game not today bc suspicious
				# but if both sides already limited 
				# then need to take all available, even diff days
				if arb_bet1 not in limited_sources or arb_bet2 not in limited_sources:
					print('AVOID Game Not Today: ' + str(arb_game) + ', ' + game_date)
					continue

			if arb_game not in todays_schedule:
				# check reverse away home teams bc sometimes labeled backwards
				arb_game = (arb_game[1], arb_game[0])
				if arb_game not in todays_schedule:
					# if either side still not limited, avoid future games
					# bc obvious red flag
					if arb_bet1 not in limited_sources or arb_bet2 not in limited_sources:
						print('AVOID arb_game: ' + str(arb_game))
						continue

			# AVOID baseball player Home Run props 
			# bc most common market inefficiency so obvious honeypot
			arb_market = arb_row[market_idx]
			# if re.search('Home Run', arb_market):
			# 	print('AVOID arb_market: ' + str(arb_market))
			# 	continue

			# AVOID small markets
			# AVOID non-star role player props
			# especially low rebound numbers
			# How to tell if main player
			# for basketball, based on minutes or specific stat level
			# bc players may have large minutes but low rebounds or assists 
			# so still small market
			# So use specific stat level



			
			# bc otherwise short term profit not worth long term loss due to obvious samples with edge
			arb_val = float(arb_row[val_idx])
			if arb_val < new_arb_rules['min'] or arb_val > new_arb_rules['max']:
				print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
				continue

			# if player prop, need higher min val to justify use 
			# but still allow home runs if already limited on other markets
			if not re.search('Moneyline|Spread|Total|Home', arb_market) and arb_val < new_arb_rules['player min']:
				print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
				continue


			# Betrivers is usually off by 5 odds so need higher limit to avoid false alarm
			# if limited by betrivers only take >3%
			# EXCEPT big markets, moneyline, spread, total bc higher limits
			
			if arb_bet1 == 'Betrivers' or arb_bet2 == 'Betrivers':
				# less limited markets such as home runs bc very extreme odds
				# so accept lower min bc invest more
				
				if arb_val < new_arb_rules['betrivers min'] and not re.search('Moneyline|Spread|Total|Home', arb_market):
					print('AVOID Betrivers arb_val: ' + str(arb_val) + ', ' + str(arb_market))
					continue


			# limited sites need higher val to be worth it
			if arb_bet1 in limited_sources or arb_bet2 in limited_sources:
				if arb_val < new_arb_rules['limited min'] and not re.search('Moneyline|Spread|Total|Home', arb_market):
					print('AVOID limited arb_val: ' + str(arb_val) + ', ' + str(arb_market))
					continue

			# AVOID picking same prop twice bc obvious strategy suspicious
			same_arb = False
			for init_arb_row in init_arb_data:
				init_arb_game = converter.convert_game_teams_to_abbrevs(init_arb_row[game_idx])
				init_arb_market = init_arb_row[market_idx]
				# print('\narb_game: ' + str(arb_game))
				# print('arb_market: ' + str(arb_market))
				# print('init_arb_game: ' + str(init_arb_game))
				# print('init_arb_market: ' + str(init_arb_market))
				if arb_game == init_arb_game and arb_market == init_arb_market:
					init_arb_val = init_arb_row[val_idx]
					#print('init_arb_val: ' + str(init_arb_val))
					# if prev arb val already greater than min val we already took prop so do not double take
					if float(init_arb_val) > 2:
						#print('Found Same Arb')
						same_arb = True
						break
						
			if same_arb:	
				print('AVOID same arb: ' + str(arb_val) + ', ' + str(arb_game) + ', ' + str(arb_market))
				continue

			# simple version: if any diff, notify
			new_picks.append(arb_row)

	# notify immediately after reading new live arbs
	# before checking prematch

	# check 2 prev arb tables bc sometimes disappear and reappear so not new
	#if len(prematch_arb_data) > 0 and init_prematch_arb_data != prematch_arb_data and prev_prematch_arb_data != prematch_arb_data:
	if len(new_picks) > 0:
		#beepy.beep() # first notify so i can get moving
		#say_str = 'say "Go Fuck Yourself."'
		# list each arb details
		arb_type = 'pre-match'
		say_str = 'say "' + arb_type + ' pick"'
		os.system(say_str)

		print('\n' + str(monitor_idx) + ': Found New Picks')


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



# open website once 
# and then loop over it 
# simulate human behavior to avoid getting blocked
def monitor_website(url):

	driver = reader.open_react_website(url)


	while True:
		# track prev web data each loop to see diff bt loops
		prev_new_web_data = {}

		# get all updated web data
		all_web_data = reader.read_dynamic_web_data(driver)

		# extract desired data
		# what has changed bt loops
		new_web_data = isolator.isolate_new_web_data(all_web_data, prev_new_web_data)

		# make it equal to new only
		# bc then we can check if it passed in last loop
		# before going thru logic to see if it is valid category
		prev_new_web_data = new_web_data

# diff from read react website bc we keep site open and loop read data
# oodsview was free but now charges
# So instead scrape sites directly
url = 'https://www.oddsview.com/odds'
#url = 'https://sportsbook.draftkings.com'
monitor_website(url)