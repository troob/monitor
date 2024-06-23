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



# === SETTINGS === 
# User Input
# When I am mobile, only send notifications that are valid
# so exclude limited sources
# BUT other ppl are not limited so we need different channels
# for limited sources, require higher profit to be worth it
limited_sources = ['BetMGM', 'Fanatics', 'Betrivers']
sources = ['Fanduel','Fliff','Draftkings','Betrivers','Caesars', 'Fanatics', 'BetMGM']
big_market_min = 0.5 # sharper big market but can put more down
min_value = 0.9
# if value too high then likely too temp to hit or read error so avoid
# sources differ so provide list
normal_max_val = 5
max_value = 7 # 5-10?
alt_max_val = 8
player_prop_min_val = 1 #1.2 # take big markets at 1% but need slightly higher val to take player prop???
betrivers_min_val = 1.5
limited_min_val = 2.5
new_arb_rules = {'normal max': normal_max_val, 
				 'max': max_value, 
				 'min': min_value,
				 'player min': player_prop_min_val, 
				 'betrivers min': betrivers_min_val,
				 'limited min': limited_min_val}


sports = ['baseball','hockey'] # big markets to stay subtle
arb_type = 'pre' # all/both/options, live, OR prematch/pre

# include game times so we can find first and last
# only need to read once per day, not every run
# save team list and times separately
# bc diff formats and we only need to get times once per day
todays_schedule_file = 'data/todays schedule.csv'
game_time_file = 'data/game times.txt' # first, last
init_todays_schedule = reader.extract_data(todays_schedule_file, header=True)
todays_schedule = reader.read_todays_schedule(sports)
game_teams = todays_schedule[0]
first_live_time = todays_schedule[1] # first game start
last_pre_time = todays_schedule[2] # last game start

# diff from read react website bc we keep site open and loop read data
url = 'https://www.oddsview.com/odds'
website = reader.open_dynamic_website(url)
# need to switch bt live and prematch on same page
driver = website[0]
live_btn = website[1]
pre_btn = website[2]

idx = 1

prev_arb_data = [] # first loop init=prev or None?

val_idx = 0
game_idx = 1
market_idx = 2
bet1_idx = 3
bet2_idx = 4
odds1_idx = 5
odds2_idx = 6
link1_idx = 7
link2_idx = 8


# input all arbs read this scan
# output only valid arbs into proper channels
# so diff users only see arbs that apply to them
def monitor_new_arbs(arb_data, init_arb_data, prev_arb_data, todays_schedule, new_arb_rules):
	# print('\n===Monitor New Arbs===\n')
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


			# check if game today
			if arb_game not in todays_schedule:
				# check reverse away home teams bc sometimes labeled backwards
				arb_game = (arb_game[1], arb_game[0])
				if arb_game not in todays_schedule:
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



			# if player prop, need higher min val to justify use 
			# bc otherwise short term profit not worth long term loss due to obvious samples with edge
			arb_val = float(arb_row[val_idx])
			if arb_val < new_arb_rules['min'] or arb_val > new_arb_rules['max']:
				print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
				continue
			#allow home runs if already limited on other markets
			if not re.search('Moneyline|Spread|Total|Home', arb_market) and arb_val < new_arb_rules['player min']:
				print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
				continue


			# Betrivers is usually off by 5 odds so need higher limit to avoid false alarm
			# if limited by betrivers only take >3%
			# EXCEPT big markets, moneyline, spread, total bc higher limits
			arb_bet1 = arb_row[bet1_idx]
			arb_bet2 = arb_row[bet2_idx]
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
		os.system('say "Go Fuck Yourself."')

		print('\n' + str(idx) + ': Found New Picks')


		post_arbs = []
		for pick in new_picks:
			arb_market = pick[market_idx]
			if not re.search('Home Run', arb_market):
				post_arbs.append(pick)



		# format string to post
		writer.write_arbs_to_post(post_arbs, client, 'ball', True)

	


	#return new_picks

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

# already init on live page
if arb_type == 'pre':
	pre_btn.click()

# need sleep to load dynamic data otherwise blank
time.sleep(1)

# keep looping every 5 seconds for change
while True:

	# DO we need to separate live and prematch in 2 files???
	# no bc just checking if any change overall
	# BUT we need to make diff notice for live vs prematch 
	# so we know which page to go to for link
	arb_data_file = 'data/arb data.csv'
	init_arb_data = reader.extract_data(arb_data_file, header=True)

	# only 1 file for efficiency but in file it separates live and prematch arbs
	# init_live_arb_data = init_arb_data[0]
	# init_prematch_arb_data = init_arb_data[1]

	if idx == 1:
		print('init_arb_data: ' + str(init_arb_data))


	# use time of day to tell arb type
	# if before first game, only pre
	# if after last game started, only live
	# else both
	#arb_type = monitor_arb_type(first_live_time, last_pre_time)
	# read live first bc changes faster
	# if arb_type == 'live':
	# 	arb_data = reader.read_live_arb_data(driver, sources)
	# elif arb_type == 'pre':
	# 	arb_data = reader.read_prematch_arb_data(driver, sources)
	# else:
	# 	arb_data = reader.read_prematch_arb_data(driver, sources)
	

	# first check Live and then Prematch
	# notify bt each so no delay for live arbs
	# read either live or pre, not both
	arb_data = []
	if arb_type == 'live':
		# if on pre-page, click live btn
		# init on live page so not extra btn to press
		arb_data = reader.read_live_arb_data(driver, sources)
	elif arb_type == 'pre':
		# if on live-page, click pre btn
		arb_data = reader.read_prematch_arb_data(driver, sources)
	# live_arb_data = arb_data[0]
	# prematch_arb_data = arb_data[1]
	

	# if keyboard interrupt return blank so we know to break loop
	if arb_data == '':
		break
	if arb_data is None:
		continue
	
	# monitor either live or pre, not both
	new_arbs = monitor_new_arbs(arb_data, init_arb_data, prev_arb_data, game_teams, new_arb_rules)
	
	
	
	# new_live_arbs = new_arbs[0]
	# new_prematch_arbs = new_arbs[1]
	


	idx += 1
	
	prev_arb_data = init_arb_data # save last 2 in case glitch causes temp disappearance
	writer.write_data_to_file(arb_data, arb_data_file) # becomes init next loop

	# if prematch, keep looping every 5 seconds for change
	# if live, loop every 2 seconds bc fast change
	time.sleep(5)




