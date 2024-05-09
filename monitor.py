# Web Monitor for constantly updating websites

import reader

init_prematch_arb_data = reader.read_init_prematch_arb_data()

prematch_arb_data = reader.read_prematch_arb_data()

if init_prematch_arb_data != prematch_arb_data:
	# notify me to confirm picks
	
	# after I confirm
	# deploy bots to make picks
	# need to get around PerimeterX bot blocker
	# even so they can probably tell if bot and ban me quicker
	# BUT if surefire way to hide bot then definitely worth it