# Web Monitor for constantly updating websites

import reader, writer, converter, time, beepy


# User Input
sources = ['Fanduel','Fliff','Fanatics', 'BetMGM','Draftkings','Betrivers','Caesars']
min_value = 0.5
sports = ['basketball','baseball','hockey'] # big markets to stay subtle

todays_schedule = reader.read_todays_schedule(sports)

# diff from read react website bc we keep site open and loop read data
url = 'https://www.oddsview.com/odds'
driver = reader.open_dynamic_website(url)

idx = 1

prev_prematch_arb_data = [] # first loop init=prev or None?

# why does vol and freq setting not work???
# beepy.volume = 0.5
# beepy.frequency = 1

# keep looping every 5 seconds for change
while True:

	prematch_arb_data_file = 'data/prematch arb data.csv'
	init_prematch_arb_data = reader.extract_data(prematch_arb_data_file, header=True)
	if idx == 1:
		print('init_prematch_arb_data: ' + str(init_prematch_arb_data))
	prematch_arb_data = reader.read_prematch_arb_data(driver, min_value, sources, todays_schedule)
	

	if prematch_arb_data is None:
		continue
	

	# if just check diff then will alert when arb disappears
	# which we do not want
	new_pick = False
	new_picks = []
	for arb_row in prematch_arb_data:

        # instead of just checking if any diff
		# must be either 
		# 1. existing arb goes from below min val to above = Any Diff bc pick not added if below min val
		# 2. diff game and market
		if arb_row not in init_prematch_arb_data and arb_row not in prev_prematch_arb_data:
			
			# complex version:
			# check if existing game and market
			arb_game = converter.convert_game_teams_to_abbrevs(arb_row[2])
			print('arb_game: ' + str(arb_game))
			# arb_market = arb_row[3]
			# same_arb = False
			# init_same_arb = []
			# for init_arb_row in init_prematch_arb_data:
			# 	init_arb_game = arb_row[2]
			# 	init_arb_market = arb_row[3]
			# 	if arb_game == init_arb_game and arb_market == init_arb_market:
			# 		same_arb = True
			# 		init_same_arb = init_arb_row

			# 		# print('Same Arb')
			# 		# print('arb_row: ' + str(arb_row))
			# 		break


			# if same_arb:	
			# 	# if same arb with changed val but prev val was already above min val
			# 	# so already taken so ignore
			# 	#arb_val = arb_row[0]
			# 	init_arb_val = float(init_same_arb[0])
			# 	# arb val went from below to above min
			# 	if init_arb_val < min_value:
			# 		new_picks.append(arb_row)

			# else:
			# 	new_picks.append(arb_row)

			# if new_pick:
			# 	new_picks.append(arb_row)
				#break


			# check if game today
			if arb_game in todays_schedule:

				# simple version: if any diff, notify
				new_picks.append(arb_row)
	
	
	# check 2 prev arb tables bc sometimes disappear and reappear so not new
	#if len(prematch_arb_data) > 0 and init_prematch_arb_data != prematch_arb_data and prev_prematch_arb_data != prematch_arb_data:
	if len(new_picks) > 0:
		print('\n' + str(idx) + ': Found New Picks')

		# print('init_prematch_arb_data: ' + str(init_prematch_arb_data))
		# print('prematch_arb_data: ' + str(prematch_arb_data))

		print('new_picks: ' + str(new_picks))

		beepy.beep()
	else:
		print(str(idx) + ': No New Picks')
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