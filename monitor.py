# Web Monitor for constantly updating websites

import reader, writer, converter, time, beepy

import re, os

#from slack_sdk import WebClient

# send email
# email vs text: which is faster???
# email has 15 second delay at least
# import smtplib, ssl

# port = 465 # for ssl
# password = input("Password: ")

# # Create a secure SSL context
# context = ssl.create_default_context()


# store as environment variable
#slack_token = os.environ["SLACK_TOKEN"]
test_msg = 'test'

# set up webclient with slack oauth token
#client = WebClient(token=slack_token)




# User Input
# When I am mobile, only send notifications that are valid
# so exclude limited sources
# BUT other ppl are not limited so we need different channels
limited_sources = ['BetMGM']
sources = ['Fanduel','Fliff','Draftkings','Betrivers','Caesars', 'Fanatics', 'BetMGM']
min_value = 1
max_value = 5
player_prop_min_val = 1.2 # take big markets at 1% but need slightly higher val to take player prop???
sports = ['basketball','baseball','hockey'] # big markets to stay subtle

todays_schedule = reader.read_todays_schedule(sports)

# diff from read react website bc we keep site open and loop read data
url = 'https://www.oddsview.com/odds'
driver = reader.open_dynamic_website(url)

idx = 1

prev_prematch_arb_data = [] # first loop init=prev or None?

val_idx = 0
game_idx = 1
market_idx = 2
bet1_idx = 3
bet2_idx = 4
odds1_idx = 5
odds2_idx = 6
link1_idx = 7
link2_idx = 8


# why does vol and freq setting not work???
# beepy.volume = 0.5
# beepy.frequency = 1

# keep looping every 5 seconds for change
while True:

	prematch_arb_data_file = 'data/prematch arb data.csv'
	init_prematch_arb_data = reader.extract_data(prematch_arb_data_file, header=True)
	if idx == 1:
		print('init_prematch_arb_data: ' + str(init_prematch_arb_data))
	prematch_arb_data = reader.read_prematch_arb_data(driver, sources, todays_schedule)
	

	if prematch_arb_data is None:
		continue
	

	# if just check diff then will alert when arb disappears
	# which we do not want
	new_pick = False
	new_picks = []
	test_picks = []
	for arb_row in prematch_arb_data:

		# TEST
		test_picks.append(arb_row)

        # instead of just checking if any diff
		# must be either 
		# 1. existing arb goes from below min val to above = Any Diff bc pick not added if below min val
		# 2. diff game and market
		if arb_row not in init_prematch_arb_data and arb_row not in prev_prematch_arb_data:
			
			


			
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
			if re.search('Home Run', arb_market):
				print('AVOID arb_market: ' + str(arb_market))
				continue


			# if player prop, need higher min val to justify use 
			# bc otherwise short term profit not worth long term loss due to obvious samples with edge
			arb_val = float(arb_row[val_idx])
			if arb_val < min_value or arb_val > max_value:
				print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
				continue
			if not re.search('Moneyline|Spread|Total', arb_market) and arb_val < player_prop_min_val:
				print('AVOID arb_val: ' + str(arb_val) + ', ' + str(arb_market))
				continue


			# AVOID picking same prop twice bc obvious strategy suspicious
			same_arb = False
			for init_arb_row in init_prematch_arb_data:
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
	
	
	# check 2 prev arb tables bc sometimes disappear and reappear so not new
	#if len(prematch_arb_data) > 0 and init_prematch_arb_data != prematch_arb_data and prev_prematch_arb_data != prematch_arb_data:
	if len(new_picks) > 0:
		beepy.beep() # first notify so i can get moving

		print('\n' + str(idx) + ': Found New Picks')

		# format string to post
		writer.write_arbs_to_post(new_picks, client, 'ball')#, True)



	#==============
	# === TEST ===
	#==============
	if len(test_picks) > 0:
		# TEST single pick
		test_picks = [test_picks[0]]
		print('\nTest Pick: ' + str(test_picks))

		# format string to post
		writer.write_arbs_to_post(test_picks, client, 'test')#, True)

		


	# else:
	# 	print(str(idx) + ': No Test Picks')
		#print('prematch_arb_data: ' + str(prematch_arb_data))

	


	# if init_prematch_arb_data != prematch_arb_data:
	# 	print(str(idx) + ': Found New Picks')
	# 	# notify me to confirm picks


	# 	# parse out % value to check >0.5
	# 	# parse out sources allowed
	# 	# SO we must first separate only new pick rows

		
	# 	# How to make system alert with noise on Mac?
	# 	# put % info in notification so i can decide if worth it 
	# 	# although can already see in window next to it so not needed
	# 	# Play a bell sound
	# 	beepy.beep()


		
	# 	# after I confirm
	# 	# deploy bots to make picks
	# 	# need to get around PerimeterX bot blocker
	# 	# even so they can probably tell if bot and ban me quicker
	# 	# BUT if surefire way to hide bot then definitely worth it
	# else:
	# 	print(str(idx) + ': No New Picks')

	idx += 1
	
	prev_prematch_arb_data = init_prematch_arb_data # save last 2 in case glitch causes temp disappearance
	writer.write_data_to_file(prematch_arb_data, prematch_arb_data_file) # becomes init next loop

	# keep looping every 5 seconds for change
	time.sleep(5)