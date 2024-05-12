# Web Monitor for constantly updating websites

import reader, writer, time, beepy


# User Input
sources = ['Draftkings','Fanduel','Betrivers','BetMGM','Caesars']
min_value = 0.5


# diff from read react website bc we keep site open and loop read data
url = 'https://www.oddsview.com/odds'
driver = reader.open_dynamic_website(url)

idx = 1

# keep looping every 5 seconds for change
while True:

	prematch_arb_data_file = 'data/prematch arb data.csv'
	init_prematch_arb_data = reader.extract_data(prematch_arb_data_file, header=True)

	prematch_arb_data = reader.read_prematch_arb_data(driver, min_value, sources)

	print('init_prematch_arb_data: ' + str(init_prematch_arb_data))
	print('prematch_arb_data: ' + str(prematch_arb_data))

	# new_pick = False
	# for arb_row in prematch_arb_data:

	# 	if arb_row not in init_prematch_arb_data:
	# 		new_pick = True
	# 		break
	
	if init_prematch_arb_data != prematch_arb_data:
		print(str(idx) + ': Found New Picks')
		beepy.beep()
	else:
		print(str(idx) + ': No New Picks')


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
	
	writer.write_data_to_file(prematch_arb_data, prematch_arb_data_file)

	# keep looping every 5 seconds for change
	time.sleep(5)