# converter.py

import re # need to see if negative sign in odds string

import reader # read player abbrevs

import math

# milwaukee bucks -> mil bucks
def convert_team_name_to_abbrev(team_name):
    print('\n===Convert Team Name to Abbrev===\n')

    # split loc and name
    loc, name = convert_team_to_loc_and_name(team_name)

    loc_abbrev = convert_team_loc_to_abbrev(loc)

    return loc_abbrev + ' ' + name

# COPY TO CLIENT
def round_to_base(x, base=5):
    return base * round_half_up(x/base)

# COPY TO CLIENT
# specifically for arb bets???
# what is different than ev bets???
# ev bets always round to whole num bc smaller scale on limited sources
# just depends on source and scale
def round_bet_size(init_bet_size, source):
    print('\n===Round Bet Size===\n')
    print('init_bet_size: ' + str(init_bet_size))
    print('source: ' + str(source) + '\n')

    # size_key = 'size' + side_num
    # init_size_str = arb[size_key]
    # print('init_size_str: ' + init_size_str)
    #init_size_float = float(re.sub('\$','',init_size_str))

    # fully limited sources round to nearest 0.10
    # partly limited sources round to whole number
    # unlimited sources round to nearest 5, 10, 50, 100
    #limited_sources = reader.read_json('sources/limited-sources.json')
    fully_limited_sources = ['betmgm', 'betrivers', 'fanatics']
    partly_limited_sources = ['draftkings', 'fanduel']
    unlimited_sources = ['caesars', 'espn', 'fliff']

    # scale is used to tell whether to round to 50 if <1000 or 100 if >1000
    # scale = 1 #-99
    # use base to round to nearest 5 or 50
    
    if source in fully_limited_sources:

        rounded_bet_size = round_half_up(init_bet_size, decimals=1)

    elif source in partly_limited_sources:

        rounded_bet_size = round_half_up(init_bet_size)
    
    #elif source in unlimited_sources:
    else:

        # cant have base 0 bc divide by 0
        # if init num < 5, round up to 5
        if init_bet_size <= 5:
            rounded_bet_size = 5

        else:
            base = 5
            # round to nearest 50
            if init_bet_size >= 1000:
                # scale = 1000 #-9999'
                base = 50
            print('base: ' + str(base))

            rounded_bet_size = round_to_base(init_bet_size, base)

    print('rounded_bet_size: ' + str(rounded_bet_size) + '\n')
    return rounded_bet_size



# based on scale and source
# round to nearest 5
# if unlimited source, round more to remain unlimited
# if limited source, all 2 decimals if 
def round_ev_bet_size(ev):
    #print('\n===Round EV Bet Size===\n')

    init_size_str = ev['size']
    #print('init_size_str: ' + init_size_str)

    init_size_float = float(re.sub('\$','',init_size_str))

    # always round to nearest whole number for ev, no matter the scale
    rounded_bet_size = '$' + str(round_half_up(init_size_float))

    #print('rounded_bet_size: ' + rounded_bet_size)
    return rounded_bet_size

# COPY TO CLIENT
def convert_name_to_standard_format(name):
    #print('\n===Convert Name to Standard Format: ' + name + '===\n')

    # cannot simply remove . bc sometimes needed if decimal in title
    if not re.search('[0-9]', name):
        name = re.sub('\.', '', name)

    name = re.sub(' jr\.?| ii+| \(.+\)|amp;', '', name)
    name = re.sub('á|ã|ä', 'a', name) # ä sometimes included?
    name = re.sub('č|ć', 'c', name)
    name = re.sub('é|ê|è', 'e', name)
    name = re.sub('ó', 'o', name)
    name = re.sub('ş', 's', name) # Beşiktaş A.Ş.
    name = re.sub('ú', 'u', name)
    
    # if market contains 'University' and ' - ' 
    # then remove ' - ' to differentiate player props
    # only player props should have ' - ' in market
    if re.search('University', name):
        name = re.sub(' - ', ' ', name)

    # remove university of and _ university
    # remove club
    name = re.sub('club |university of | university', '', name)

    #print('name: ' + name)
    return name

# remove extra letters from name, such as the 'u' in 'pittsburgh u'
def convert_bet_line_to_standard_format(listed_line):

    # universal rule for university sports
    # either university of x or x university
    bet_line = re.sub(' u$', '', listed_line)
    bet_line = re.sub(' u ', ' ', bet_line)

    # remove ole from ole miss
    bet_line = re.sub('^ole ', '', bet_line)

    bet_line = convert_name_to_standard_format(bet_line)

    return bet_line

# init bet line unless need to change
# spreads are usually same except soccer handicaps on betmgm
def convert_bet_line_to_source_format(bet_line, market, sport, website_name):
    print('\n===Convert Bet Line to Source Format===\n')
    print('Input: bet_line = ' + bet_line)
    print('Input: market = ' + market + '\n')
    #print('Output: source bet_line = string\n')

    # universal rule for university sports
    bet_line = re.sub('university of | university', '', bet_line)

    # abbrev player name
    # solo sports do not have spreads?
    # no bc tennis set and game spread
    solo_sports = ['boxing', 'mma', 'tennis']
    if website_name == 'betmgm':
        
        # special case player props not o/u but yes only
        # so player name is bet line
        # football anytime td scorer has player name as line
        # hockey anytime goalscorer
        if re.search('- touchdowns|- goals', market):
            player_name = market.split(' - ')[0]
            bet_line = player_name

        elif market == 'total sets':
            # u 2.5 -> 2 sets
            # o 2.5 -> 3 sets
            bet_data = bet_line.split()
            direction = bet_data[0]
            line_val = bet_data[1]
            if direction == 'o':
                bet_line = '3 sets'
            else:
                bet_line = '2 sets'

        # to win at least 1 set
        # elif bet_line == 'yes' or bet_line == 'no':
        #     print('Same Bet Line')

        # totals and player props are over/unders
        elif re.search('total| - ', market):
            bet_data = bet_line.split()
            direction = bet_data[0]
            line_val = bet_data[1]
            if re.search('first inning', market):
                if direction == 'o':
                    bet_line = 'yes'
                else:
                    bet_line = 'no'
            else:
                if direction == 'o':
                    bet_line = 'over ' + line_val
                else:
                    bet_line = 'under ' + line_val

        elif sport == 'soccer' and market == 'spread':
            # +0.5 -> (0.5)
            # remove + sign?
            # no bc need +/- to indicate cutoff
            #bet_line = re.sub('\+', '', bet_line)
            bet_line = re.sub(r' \+(.+)', ' \((1)\)', bet_line)
            bet_line = re.sub(r' (-.+)', ' \((1)\)', bet_line)

        elif sport in solo_sports and not re.search('spread', market):
            # ensure player name
            #if bet_line != 'yes' and bet_line != 'no':
            #if not re.search('^yes$|^no$', bet_line):
            # josh kelly -> j kelly
            names = bet_line.split(' ', 1)
            if len(names) > 1:
                bet_line = names[0][0] + ' ' + names[1]

    elif website_name == 'draftkings':

        if re.search('moneyline', market):

            # milwaukee bucks -> mil bucks
            bet_line = convert_team_name_to_abbrev(bet_line)

        # special case player props not o/u but yes only
        # so player name is bet line
        # football anytime td scorer has player name as line
        elif re.search('- touchdowns|- goals', market):
            player_name = market.split(' - ')[0]
            bet_line = player_name

        elif market == 'total sets':
            # u 2.5 -> 2 sets
            # o 2.5 -> 3 sets
            bet_data = bet_line.split()
            direction = bet_data[0]
            line_val = bet_data[1]
            if direction == 'o':
                bet_line = '3 sets'
            else:
                bet_line = '2 sets'

        # totals and player props are over/unders
        elif re.search('total| - ', market):
            bet_data = bet_line.split()
            direction = bet_data[0]
            line_val = bet_data[1]
            if re.search('first inning', market):
                if direction == 'o':
                    bet_line = 'yes'
                else:
                    bet_line = 'no'
            else:
                if direction == 'o':
                    bet_line = 'over ' + line_val
                else:
                    bet_line = 'under ' + line_val

        elif sport == 'soccer' and market == 'spread':
            # +0.5 -> (0.5)
            # remove + sign?
            # no bc need +/- to indicate cutoff
            #bet_line = re.sub('\+', '', bet_line)
            bet_line = re.sub(r' \+(.+)', ' \((1)\)', bet_line)
            bet_line = re.sub(r' (-.+)', ' \((1)\)', bet_line)

        elif sport in solo_sports and not re.search('spread', market):
            # josh kelly -> j kelly
            names = bet_line.split(' ', 1)
            if len(names) > 1:
                bet_line = names[0][0] + ' ' + names[1]


        

    print('source bet_line: ' + bet_line + '\n')
    return bet_line

def convert_market_to_source_format(market, sport, game, league, website_name):
    print('\n===Convert Market to Source Format===\n')
    print('market: ' + market)
    print('sport: ' + sport)
    print('game: ' + game)
    print('league: ' + league)
    print('website_name: ' + website_name + '\n')
    #print('\nOutput: market_title = string\n')

    market_title = market

    if website_name == 'betmgm':

        if sport == 'baseball':

            # Same
            # first x innings spread
            # pitcher outs
            # home runs
            # runs
            # singles/doubles/triples
            # bases/stolen bases
            # batter walks

            # NA
            # hits allowed

            if market == 'moneyline':

                market_title = 'money line'
            
            elif market == 'spread':

                market_title = 'run line spread'

            elif market == 'total':

                market_title = 'totals'

            elif re.search('innings? moneyline', market):

                market_title = re.sub('moneyline', 'money line', market)

            elif market == 'first inning total':

                market_title = '1st inning run'

            elif re.search('innings? total', market):

                market_title = market + ' runs'

            elif re.search('innings? .+ total', market):
                # first inning milwaukee brewers total
                # milwaukee brewers 1st inning runs
                #parts = re.split('innings? ',market)
                team_part = re.split('innings? ',market)[1] # 'milwaukee brewers total'
                inning_part = market.split(team_part)[0] #parts[0] # 'first inning '
                if re.search('first', inning_part): # # '1st inning '
                    inning_part = re.sub('first', '1st', inning_part)
                #team_part = parts[1] # 'milwaukee brewers total'
                team_name = team_part.split('total')[0] # 'milwaukee brewers '
                market_title = team_name + inning_part + 'runs'

            # team total
            elif re.search('total', market):

                market_title = market + ' runs'

            # Player Props
            elif market == 'pitcher strikeouts':

                market_title = 'strikeouts'

            elif market == 'earned runs allowed':

                market_title = 'pitcher earned runs'

            elif market == 'rbi':

                market_title = 'runs batted in'

            elif market == 'hits runs rbis':

                market_title = 'total hits, runs and rbis'


        elif sport == 'basketball':

            # Same
            # spread
            # assists
            # points
            # rebounds

            if market == 'moneyline':

                market_title = 'money line'
            
            elif market == 'total':

                market_title = 'totals'


            # Halfs
            # first half spread
            # 1st half totals
            # first half money line
            elif market == '1st half spread':
                market_title = 'first half spread'
            elif market == '1st half total':
                market_title = '1st half totals'
            elif market == '1st half moneyline':
                market_title = 'first half money line'


            # Quarters
            # first quarter spread
            # first quarter totals
            # first quarter money line
            elif market == '1st quarter spread':
                market_title = 'first quarter spread'
            elif market == '1st quarter total':
                market_title = 'first quarter totals'
            elif market == '1st quarter moneyline':
                market_title = 'first quarter money line'


            # Player Props
            elif market == 'threes':

                market_title = 'three-pointers made'


        elif sport == 'boxing' or sport == 'mma':
            
            if market == 'moneyline':

                market_title = 'fight result'

        elif sport == 'football':

            # Same
            # Spread
            
            if market == 'moneyline':

                market_title = 'money line'

            elif market == 'total':

                market_title = 'totals'

            elif market == 'touchdowns':

                market_title = 'anytime td scorer'

            elif market == 'defensive tackles and assists':

                market_title = 'total tackles and assists'

            elif market == 'first to score':

                market_title = 'team to score first'

            # 1st half totals is only market with abbrev
            # others spell out first

            # 1st Quarter Total -> first quarter totals
            # 1st Half Total -> 1st half totals

            # 1st Quarter Spread -> first quarter spread
            # 1st Half Spread -> first half spread

            elif market == '1st half spread':
                market_title = 'first half spread'
            elif market == '1st half total':
                market_title = '1st half totals'
            elif market == '1st half moneyline':
                market_title = 'first half money line'

            elif market == '1st quarter spread':
                market_title = 'first quarter spread'
            elif market == '1st quarter total':
                market_title = 'first quarter totals'
            elif market == '1st quarter moneyline':
                market_title = 'first quarter money line'

            
            # 1st Half Philadelphia Eagles Total -> Philadelphia Eagles 1st half points
            elif re.search('half .+ total|quarter .+ total', market):
                #parts = market.split('half ')
                team_part = re.split('half |quarter ', market)[1] # 'Philadelphia Eagles Total
                
                period_part = market.split(team_part)[0] # '1st half '
                
                team_name = team_part.split(' total')[0] # 'Philadelphia Eagles'
                team_name = convert_name_to_standard_format(team_name)

                market_title = team_name + ' ' + period_part + 'points'

            # eagles total -> eagles total points
            elif re.search('total', market):
                
                market_title += ' points'


        elif sport == 'hockey':

            if market == 'moneyline':

                market_title = 'money line'

            elif market == 'total':

                market_title = 'totals'

            # team total
            elif re.search('\stotal', market):

                market_title = re.sub('total', 'goals', market)

            elif market == 'goals':

                market_title = 'anytime goalscorer'

            


        elif sport == 'soccer':
            
            if market == 'moneyline':

                market_title = 'match result'

            # first half moneyline -> first half result
            elif re.search('moneyline', market):

                market_title = re.sub('moneyline', 'result', market)

            elif market == 'total':

                market_title = 'total goals'

            elif market == 'spread':

                market_title = 'handicap'

            # 1st Half Huracán Total -> Huracán - 1st half - total goals
            # 1st half real madrid total -> real madrid - total goals - 1st half
            elif re.search('half .+ total', market):
                print('Half Team Total')
                team_part = market.split('half ')[1] # 'Huracán Total'
                # use team part to split off period part
                period_part = market.split(team_part)[0].strip() # '1st half'
                
                team_name = team_part.split('total')[0] # 'huracan '

                #market_title = team_name + period_part + '- total goals'

                market_title = team_name + '- total goals - ' + period_part

            # 1st half total -> 1st half - total goals
            # elif re.search('half total', market):

            #     market_title = re.sub('total', '- total goals', market)

            # Huracán Total -> Huracán - total goals
            elif re.search('total', market):
                
                market_title = re.sub('total', '- total goals', market)


        elif sport == 'tennis':

            # Same
            # Set 1 winner
            
            if market == 'moneyline':

                market_title = 'match winner'

            elif re.search('least', market):

                player_name = market.split(' to ')[0]

                # flavio cobolli to win at least 1 set
                # player 1 to win at least 1 set
                players = game.split(' vs ')
                player_num = '1'
                # betmgm does opposite to oddsview player order
                if player_name == players[0]:
                    player_num = '2'

                market_title = 'player ' + player_num + ' to win at least 1 set'


            elif market == 'total sets':

                market_title = 'how many sets will be played in the match?'

            elif market == 'game spread':

                market_title = 'who will win the most games in the match? (player spread)'
                

    elif website_name == 'draftkings':
        #print('Source 3 DK')

        # convert ' and ' to ' + ' for all
        market_title = re.sub(' and ', ' \+ ', market)

        if sport == 'baseball':

            if market == 'spread':
                market_title = 'run line'

            elif market == 'bases':
                market_title = 'total bases'

            # first 3 innings moneyline -> 1st 3 innings
            elif re.search('innings? moneyline', market):

                market_title = re.sub('first', '1st', market)
                market_title = re.sub(' moneyline', '', market_title)

            elif re.search('innings? total', market):

                market_title = market + ' runs'

            elif re.search('innings? .+ total', market):
                # first inning milwaukee brewers total
                # mil brewers: team total runs - 1st inning
                #parts = re.split('innings? ',market)
                team_part = re.split('innings? ',market)[1] # 'milwaukee brewers total'
                inning_part = market.split(team_part)[0].strip() #parts[0] # 'first inning'
                if re.search('first', inning_part): # # '1st inning'
                    inning_part = re.sub('first', '1st', inning_part)
                #team_part = parts[1] # 'milwaukee brewers total'
                team_name = team_part.split(' total')[0] # 'milwaukee brewers'
                team_abbrev = team_name #convert_team_name_to_abbrev(team_name) # 'mil brewers'
                market_title = team_abbrev + ' team total runs - ' + inning_part

        elif sport == 'basketball':

            # 3rd quarter moneyline -> moneyline 3rd quarter
            # moneyline always last word
            if re.search('quarter moneyline|half moneyline', market):
                market_data = market.rsplit(' ', 1)
                period_part = market_data[0]
                market_part = market_data[1]
                market_title = market_part + ' ' + period_part


        elif sport == 'football':
            #print('Football')

            if market == 'first to score':

                market_title = '1st to score'

            elif market == 'touchdowns':

                market_title = 'anytime td scorer'
            
            # 1st Half Philadelphia Eagles Total -> phi Eagles team total points - 1st half
            elif re.search('half .+ total|quarter .+ total', market):
                print('Part Team Total')

                # 'Philadelphia Eagles Total'
                # 'Northwestern University Total'
                # 'University of Maryland Total'
                team_part = re.split('half |quarter ', market)[1] 
                print('team_part: ' + team_part)
                
                # '1st half'
                period_part = market.split(team_part)[0].strip() 
                print('period_part: ' + period_part)
                
                # 'Philadelphia Eagles'
                # 'Northwestern'
                # 'Maryland'
                team = team_part.split(' total')[0] 
                team = convert_name_to_standard_format(team)
                print('team: ' + team)

                if league == 'nfl':
                    # 'philadelphia', 'eagles'
                    location, name = convert_team_to_loc_and_name(team)

                    # 'phi'
                    loc_abbrev = convert_team_loc_to_abbrev(location) 

                    # phi Eagles
                    team = loc_abbrev + ' ' + name

                # phi Eagles team total points - 1st half
                # northwestern team total points - 1st half
                market_title = team + ' team total points - ' + period_part

            # 1st half spread/moneyline/total -> spread/moneyline/total 1st half
            elif re.search('half|quarter', market):
                print('Part Total/Spread/Moneyline')

                # last word
                market_data = market.rsplit(' ', 1)
                overall_market = market_data[1] # 'spread' 
                period = market_data[0] # '1st half'

                market_title = overall_market + ' ' + period #re.sub(' spread', '', market)


            # Team Total
            # philadelphia eagles total -> phi eagles team total points
            # auburn university total -> auburn team total points
            elif re.search('\stotal', market):
                print('Team Total')
                
                # 'Philadelphia Eagles'
                team = market.split(' total')[0]
                #team_name = re.sub(' university|university of ', '', team_name)
                team = convert_name_to_standard_format(team)

                # 'philadelphia', 'eagles'
                location, name = convert_team_to_loc_and_name(team)

                # 'phi'
                loc_abbrev = convert_team_loc_to_abbrev(location) 
                
                market_title = ''
                if loc_abbrev != '':
                    market_title = loc_abbrev + ' ' 
                market_title += name + ' team total points'

            


    print('market_title: ' + market_title + '\n')
    return market_title

# extract team loc from bet
# by separating team name
def convert_full_team_name(bet_outcome, market):
    print('\n===Convert Bet to Team Loc===\n')
    print('Input: bet_outcome = team name = ' + bet_outcome)

    # convert_team_to_loc_and_name
    # only sox has 2 names in team
    # 2 word teams:
    # white sox
    # blue bombers
    # trail blazers
    # hockey club
    multi_names = ['sox', 'blue', 'blazer', 'club']
    split_num = 1
    for multi_name in multi_names:
        if multi_name in bet_outcome:
            split_num = 2
            break
    print('split_num: ' + str(split_num))

    # moneyline outcome is just team name
    # but other bets like spread have +1.5 to split off
    if re.search('spread', market):
        split_num += 1

    team_loc = bet_outcome.rsplit(' ', split_num)[0]
    #team_loc = bet_outcome.split()[0]

    print('team_loc: ' + team_loc)
    return team_loc

# extract team loc from bet
# by separating team name
def convert_bet_to_team_loc(bet_outcome, market):
    print('\n===Convert Bet to Team Loc===\n')
    print('Input: bet_outcome = team name = ' + bet_outcome)

    # only sox has 2 names in team
    # white sox and blue bombers is 2 words
    multi_names = ['sox', 'blue', 'blazer', 'club']
    split_num = 1
    for multi_name in multi_names:
        if multi_name in bet_outcome:
            split_num = 2
            break
    print('split_num: ' + str(split_num))

    # moneyline outcome is just team name
    # but other bets like spread have +1.5 to split off
    if re.search('spread', market):
        split_num += 1

    team_loc = bet_outcome.rsplit(' ', split_num)[0]
    #team_loc = bet_outcome.split()[0]

    print('team_loc: ' + team_loc)
    return team_loc


def convert_name_format(name, name_format=None):
    print('\n===Convert Name Format===\n')
    print('Input: name = ' + name + '\n')

    # if not sure which format input but only want comma out
    if name_format == ',' and not re.search(',', name):
        names = name.split() 
        name = names[1] + ', ' + names[0]
        
    else:
        # Swiatek, Iga -> Iga Swiatek
        # Bouzas Maneiro, Jessica -> Jessica Bouzas Maneiro
        if re.search(',', name):
            names = name.split(', ') 
            name = names[1] + ' ' + names[0]

        # Iga Swiatek -> Swiatek, Iga
        # Jessica Bouzas Maneiro -> Bouzas Maneiro, Jessica
        else:
            names = name.split(' ', 1) 
            name = names[1] + ', ' + names[0]

            # remove dots after 1 initial
            # dodig, i. -> dodig, i
            # do not change abbrevs like c.j.
            #name = re.sub(r'([a-z])\.', '{1}', name)
            if name.count('.') == 1:
                name = re.sub('\.', '', name)

    print('name: ' + name)
    return name

# if university or state then loc is team name
# but problem is university names can have any name
# so need to know league
# milwaukee bucks -> milwaukee, bucks
def convert_team_to_loc_and_name(team):
    print('\n===Convert Team to Loc and Name===\n')
    print('Input: team = kansas city royals or chicago white sox = ' + team)
    print('\nOutput: kansas city or chicago\n')

    # only sox has 2 names in team
    # white sox is 2 words
    #multi_name = 'sox'
    multi_names = ['sox', 'blue', 'blazer', 'club']
    split_num = 1
    for multi_name in multi_names:
        if multi_name in team:
            split_num = 2
            break
    print('split_num: ' + str(split_num))

    team_data = team.rsplit(' ', split_num)
    team_loc = team_data[0]
    #team_loc = bet_outcome.split()[0]
    team_name = team_data[1]
    if split_num == 2:
        team_name += ' ' + team_data[2]

    print('team_loc: ' + team_loc)
    print('team_name: ' + team_name)
    return team_loc, team_name


# seattle seahawks total -> sea seahawks
def convert_market_to_team_name(market, league, sport):
    print('\n===Convert Market to Team Name===\n')
    print('Input: market = ' + market)

    # 1st half atlas total
    # 1st half university of north carolina at charlotte total
    if re.search('innings?|halfs?|quarters?', market):
        market = re.split('innings? |halfs? |quarters? ', market)[1]

    # university of north carolina at charlotte total
    # -> charlotte total
    if re.search(' at ', market):
        market = market.split(' at ')[1]

    # only convert team name format if usa league
    # atlas total
    source_team_name = re.sub(' total', '', market)
    source_team_name = convert_name_to_standard_format(source_team_name)

    usa_leagues = ['mlb', 'nba', 'nfl', 'wnba', 'nhl']

    if league not in usa_leagues:
        return source_team_name

    # first x innings kansas city royals total -> kansas city royals
    # first inning kansas city royals total -> kansas city royals
    # if re.search('innings?|halfs?|quarters?', market):
    #     #market = market.split('innings ')[1]
    #     market = re.split('innings? |halfs? |quarters? ', market)[1]
    # elif re.search('inning|half|quarter', market):
    #     #market = market.split('inning ')[1]
    #     market = re.split('inning |half |quarter ', market)[1]
    # kansas city royals total
    print('market: ' + market)

    # remove last word to get team full name
    # kansas city royals
    team_full_name = market.rsplit(' ', 1)[0]

    team_loc, team_name = convert_team_to_loc_and_name(team_full_name)

    loc_abbrev = convert_team_loc_to_abbrev(team_loc, sport)

    # final format depends on source
    # betrivers uses loc abbrev + team name
    # oakland athletics -> oak athletics
    # kansas city royals -> kc royals
    source_team_name = loc_abbrev + ' ' + team_name

    print('source_team_name: ' + source_team_name)
    return source_team_name


# we must iteratively try to round stake and see if other side stake is round enough
# until both stakes are round enough
def round_stakes(stake1, stake2):
    print('\n===Round Stakes: ' + str(stake) + '===\n')

    round_stake = str(stake)

    # if <100, round up to nearest 10
    if stake < 100:
        round_stake = round(stake, 10)

    print('round_stake: ' + round_stake)
    return str(round_stake)


# if very likely odds 80/20 then lean more towards likely outcome
# but if 70/30 or less then round down if less than 5
def round_stake(stake):
    print('\n===Round Stake: ' + str(stake) + '===\n')

    round_stake = round(stake, 10)

    print('round_stake: ' + round_stake)
    return str(round_stake)



# (+100, +105) -> (max limit, x)
# Arbitrage % = ((1 / decimal odds for outcome A) x 100) + ((1 / decimal odds for outcome B) x 100)
# Individual Bet = (Total Investment x Individual Odds Percentage) / Total Arbitrage Percentage
def convert_odds_to_bet_size(odds1, odds2, max_limit):
    # print('\n===Convert Odds to Bet Size===\n')
    # print('Input: odds1 = +x = ' + odds1)
    # print('odds2: ' + odds2)
    # print('max_limit: ' + str(max_limit))
    # print('\nOutput: stake = x\n')

    # calc individual odds percent
    # if positive
    # decimal_odds1 = 0
    # if odds1[0] == '+':
    #     decimal_odds1 = (int(odds1) / 100) + 1
    # # if negative
    # else:
    #     decimal_odds1 = (100 / int(odds1)) + 1

    # percent_odds1 = (1 / decimal_odds1) * 100

    # decimal_odds2 = 0
    # if odds1[0] == '+':
    #     decimal_odds2 = (int(odds2) / 100) + 1
    # # if negative
    # else:
    #     decimal_odds2 = (100 / int(odds2)) + 1

    # percent_odds2 = (1 / decimal_odds2) * 100

    # percent_odds1 = 0
    # if odds1[0] == '+':
    #     print('Positive')
    #     percent_odds1 = 100 / (int(odds1) + 100) * 100
    #     percent_odds2 = int(odds2) / (int(odds2) + 100) * 100
    # # if negative
    # else:
    #     percent_odds1 = int(odds1) / (int(odds1) + 100) * 100
    #     percent_odds2 = 100 / (int(odds2) + 100) * 100


    # odds1 always negative odds
    # EXCEPT +100
    # -210 / 
    percent_odds1 = 0 #int(odds1) / (int(odds1) - 100) * 100
    if odds1[0] == '+':
        percent_odds1 = round_half_up(100 / (int(odds1) + 100) * 100, 1)
    else:
        percent_odds1 = round_half_up(int(odds1) / (int(odds1) - 100) * 100, 1)
    percent_odds2 = round_half_up(100 / (int(odds2) + 100) * 100, 1)

    # print('decimal_odds1: ' + str(decimal_odds1))
    # print('decimal_odds2: ' + str(decimal_odds2))
    # print('percent_odds1: ' + str(percent_odds1))
    # print('percent_odds2: ' + str(percent_odds2))


    # arb_percent = percent_odds1 + percent_odds2

    # # total_stake = max_limit + likely_stake
    # stake1 = (total_stake * percent_odds1) / arb_percent

    # stake2 = (total_stake * percent_odds2) / arb_percent
    # # stake2 * arb_percent = total_stake * percent_odds2
    # total_stake = stake2 * arb_percent / percent_odds2

    # loop thru from max limit to min limit
    # every 100
    # limits = []
    # for limit in limits:


    # bigger bet on more likely outcome
    # rounder bet on less likely outcome bc less suspicious
    likely_stake = round(math.ceil(max_limit * percent_odds1 / percent_odds2), -1)
    # simply round based on scale
    # more advanced will iteratively round both stakes until both are ideally round
    #likely_stake = round_stakes(likely_stake, max_limit)

    #print('likely_stake: ' + likely_stake)
    return likely_stake





def convert_game_teams_to_abbrevs(game_teams):
    # print('\n===Convert Game Teams to Abbrevs===\n')
    # print('game_teams: ' + str(game_teams))
    # print('Input: game_teams = \'Away Team vs Home Team\'')

    #team_abbrevs = ()
    teams = game_teams.split(' vs ')
    away_team = teams[0].lower()
    home_team = teams[1].lower()

    away_team_abbrev = convert_team_name_to_abbrev(away_team)
    home_team_abbrev = convert_team_name_to_abbrev(home_team)

    return (away_team_abbrev, home_team_abbrev)



# from fri 1/12 to 1/12/2024
def convert_game_date_to_full_date(init_game_date, season_year):
    # print('\n===Convert Game Date to Full Date===\n')
    # print('init_game_date: ' + str(init_game_date))
    # print('season_year: ' + str(season_year))

    game_date = init_game_date.split()[1]
    game_mth = game_date.split('/')[0]
    final_season_year = str(season_year)
    if int(game_mth) in range(10,13):
        final_season_year = str(int(season_year) - 1)
    full_date = game_date + "/" + final_season_year

    #print('full_date: ' + str(full_date))
    return full_date



def convert_dict_to_list(dict, desired_order=[]):

    dict_list = []

    for key in desired_order:
        if key in dict.keys():
            val = dict[key]
            dict_list.append(val)
        else:
            print('Warning: Desired key ' + key + ' not in dict!')

    # add remaining in the order they come
    for key, val in dict.items():
        # if not already added
        if key not in desired_order:
            dict_list.append(val)

    return dict_list


def convert_dicts_to_lists(all_consistent_stat_dicts, desired_order=[]):
    #print('\n===Convert Dicts to Lists===\n')
    dict_lists = []

    for dict in all_consistent_stat_dicts:
        #print('dict: ' + str(dict))

        dict_list = convert_dict_to_list(dict, desired_order)

        dict_lists.append(dict_list)
        
    return dict_lists

# from 2023-24 to 2024
def convert_span_to_season(span):

    #print('span: ' + span)
    season_years = span.split('-')
    # for now assume 2000s
    season = '20' + season_years[1]

    #print('season: ' + season)
    return season

def convert_team_abbrev_to_espn_abbrev(team_abbrev):

    espn_irregular_abbrevs = {'uta':'utah',
						   	'nyk':'ny',
							'gsw':'gs',
							'nop':'no',
							'sas':'sa'}
    
    if team_abbrev in espn_irregular_abbrevs.keys():
        team_abbrev = espn_irregular_abbrevs[team_abbrev]

    return team_abbrev

def convert_irregular_team_abbrev(init_team_abbrev):
    #print('\n===Convert Irregular Team Abbrev: ' + init_team_abbrev + '===\n')

    init_team_abbrev = init_team_abbrev.lower()

    final_team_abbrev = init_team_abbrev

    irregular_abbrevs = {'bro':'bkn', 
					  	'gs':'gsw',
						'okl':'okc', 
						'no':'nop',
						'nor':'nop', 
						'pho':'phx', 
						'was':'wsh', 
						'uth': 'uta', 
						'utah': 'uta', 
						'sa':'sas',
						'ny':'nyk'  } # for these match the first 3 letters of team name instead

    if init_team_abbrev in irregular_abbrevs.keys():
        final_team_abbrev = irregular_abbrevs[init_team_abbrev]

    #print('final_team_abbrev: ' + final_team_abbrev)
    return final_team_abbrev

# SEE generate_player_abbrev for more
# jaylen brown -> j brown sg
# trey murphy iii -> t murphy iii sg
# Jayson Tatum -> J Tatum SF
# use to see if started or bench
# bc box score shows player abbrev
# lineups online have mix of full and abbrev names
# def convert_player_name_to_abbrev(player, player_position):
#     player_abbrev = ''
#     return player_abbrev

# given team and player abbrev without position
# we can tell player full name
# we get team from all lineups page online
# but if we only get abbrev then we cannot say position for sure
# if 2 players have same abbrevs on same team, lineups will differentiate for us
# so take full name first and abbrev as remaining option
def convert_player_abbrev_to_name(player_abbrev, player_team):
    player_name = ''

    # check if 2 players on same team with same abbrev
    # bc if so then would take first player name without knowing position



    return player_name

# american odds given as string from internet
def convert_american_to_decimal_odds(american_odds):
    #print('\n===Convert American to Decimal Odds===\n')
    #print('american_odds: ' + str(american_odds))
    decimal_odds = 0.0

    #determine if input str or int
    #if re.search('-|\+',str(american_odds)):
        
    #if re.search('-',american_odds):
    if int(american_odds) < 0:
        decimal_odds = "%.2f" % ((100 / -int(american_odds)) + 1)
    else:
        decimal_odds = "%.2f" % ((int(american_odds) / 100) + 1)
    
    #print('decimal_odds: ' + str(decimal_odds))
    return float(decimal_odds)




























def convert_time_zone_to_time(timezone):
    # print('Input: timezone = ' + timezone)
    # print('\nOutput: time = 0\n')

    # nba uses ET as standard time
    time = 0

    # each timezone needs a ref relative time
    timezone_times = {'ET':0,
                      'CT':-1,
                      'MT':-2,
                      'PT':-3,
                      'HAT':-5,
                      'GMT':5,
                      'CET':6,
                      'IT':7,
                      'GT':9,
                      'JT':14,}
    
    if timezone != '':
        time = timezone_times[timezone]

    return time

# convert 12/29/2023 to Dec 29 2023
# so convert month num to name
def convert_month_num_to_abbrev(date):

    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

    date_data = date.split('/')
    mth_num = date_data[0]
    day_num = date_data[1]
    year = date_data[2]

    abbrev = months[int(mth_num)-1] + ' ' + day_num + ' ' + year

    return abbrev

def convert_month_abbrev_to_num(game_mth_abbrev):
    #print('\n===Convert Month Abbrev to Num: ' + game_mth_abbrev + '===\n')

    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    
    game_mth_num = 1

    game_mth_abbrev = game_mth_abbrev.lower()

    for mth_idx in range(len(months)):
        mth = months[mth_idx]
        if mth == game_mth_abbrev:
            game_mth_num = mth_idx + 1
            break

    #print('game_mth_num: ' + str(game_mth_num))
    return game_mth_num

# default whole number
def round_half_up(n, decimals=0):
    multiplier = 10**decimals
    nr = math.floor(n * multiplier + 0.5) / multiplier
    if decimals == 0:
        return int(nr)
    else:
        return nr

def convert_year_to_span(year):

    # year is season end
    year_start = str(int(year) - 1)
    abbrev_yr_end = year[2:]

    span = year_start + '-' + abbrev_yr_end

    return span

# all_box_scores = {game:{away:{starters:{},bench:{}},home:{starters:[],bench:[]}}
# we will convert away home to teammates opponents given current player of interest
# game_box_scores_dict = {away:df, home:df}
# get the game box score page using the game id
# get the box score from the page in a df
# game_box_scores_dict = {away:df, home:df}
# currently returns empty dict if results already saved
def convert_box_score_to_dict(box_score_df):
    # print('\n===Convert Box Score to Dict===\n')
    # print('Input: box_score_df = dataframe')
    # print('\nOutput: box_score_dict = {team part: {player abbrev:play time, ...= {\'starters\': {\'A Gordon PF\': \'32\', ...\n')

    box_score_dict = {'starters':{},'bench':{}}

    players = box_score_df[0].drop(0).to_list()
    #print('players:' + str(players))
    play_times = box_score_df[1].drop(0).to_list()
    
    final_players = []
    for player in players:
        player = re.sub('\.','',player)#.lower() # easier to read if titled but ust match comparisons with all teammates. all teammates comes from all players in games so they auto match format
        player = re.sub('-',' ',player)
        final_players.append(player)

    bench_idx = 5 # bc always 5 starters
    # starters = final_players[:bench_idx]
	# bench = final_players[bench_idx+1:]
    #for team_part, team_part_box_score_dict in box_score_dict.items():

    # ignore players played <10min
    # arbitrary portion of game deemed consequential
    for player_idx in range(len(players)):
        # ignore mid header row repeated for bench
        if player_idx == bench_idx:
            continue

        team_part = 'bench'
        if player_idx < bench_idx:
            team_part = 'starters'

        player = final_players[player_idx]
        play_time = play_times[player_idx]

        # better to keep all players in box score, even dnp and out
        # bc easier to match with current conditions than leaving unknowns
        #if int(play_time) > 10:
        box_score_dict[team_part][player] = play_time

    #print('box_score_dict: ' + str(box_score_dict))
    return box_score_dict

def convert_team_to_loc_abbrev(team_loc, sport=''):
    #print('\n===Convert Team to Location Abbrev: ' + team_name + '===\n')
    
    abbrev = ''

    
    # for baseball, need logo info bc multiple teams same city
    if sport == 'baseball':
        team_locs = {'chicago white sox':'chw',
                    'cleveland guardians':'cle',
                    'detroit tigers':'det',
                    'kansas city royals':'kc', #KC
                    'minnesota twins':'min',
                    'baltimore orioles':'bal',
                    'boston red sox':'bos',
                    'new york yankees':'ny',
                    'tampa bay rays':'tb',
                    'toronto blue jays':'tor',
                    'houston astros':'hou',
                    'los angeles angels':'la',
                    'oakland athletics':'oak',
                    'seattle mariners':'sea',
                    'texas rangers':'tex',
                    'chicago cubs':'chi',
                    'cincinnati reds':'cin',
                    'milwaukee brewers':'mil',
                    'pittsburgh pirates':'pit',
                    'st louis cardinals':'stl',
                    'atlanta braves':'atl',
                    'miami marlins':'mia',
                    'new york mets':'ny',
                    'philadelphia phillies':'phi',
                    'washington nationals':'wsh',
                    'arizona diamondbacks':'ari',
                    'colorado rockies':'col',
                    'los angeles dodgers':'la',
                    'san diego padres':'sd',
                    'san francisco giants':'sf'}
        
    elif sport == 'hockey':
        team_locs = {'boston':'bos',
                        'buffalo':'buf',
                        'detroit':'det',
                        'florida':'fla',
                        'montreal':'mtl',
                        'ottawa':'ott',
                        'tampa bay':'tbl',
                        'toronto':'tor',
                        'arizona':'ari',
                        'chicago':'chi',
                        'colorado':'col',
                        'dallas':'dal',
                        'minnesota':'min',
                        'nashville':'nsh',
                        'st louis':'stl',
                        'winnipeg':'wpg',
                        'carolina':'car',
                        'columbus':'cbj',
                        'new jersey':'njd',
                        'new york islanders':'nyi',
                        'new york rangers':'nyr',
                        'philadelphia':'phi',
                        'pittsburgh':'pit',
                        'washington':'wsh',
                        'anaheim':'ana',
                        'calgary':'cgy',
                        'edmonton':'edm',
                        'los angeles':'lak',
                        'san jose':'sjs',
                        'seattle':'sea',
                        'vancouver':'van',
                        'vegas':'vgk'}
    elif sport == 'football':
        team_locs = {'buffalo':'buf',
                        'miami':'mia',
                        'new england':'nep',
                        'new york jets':'nyj',
                        'baltimore':'bal',
                        'cincinnati':'cin',
                        'cleveland':'cle',
                        'pittsburgh':'pit',
                        'houston':'hou',
                        'indianapolis':'ind',
                        'jacksonville':'jax',
                        'tennessee':'ten',
                        'denver':'den',
                        'kansas city':'kcc',
                        'las vegas':'lvr',
                        'los angeles colts':'lac',
                        'dallas':'dal',
                        'new york giants':'nyg',
                        'philadelphia':'phi',
                        'washington':'wsh',
                        'chicago':'chi',
                        'detroit':'det',
                        'green bay':'gbp',
                        'minnesota':'min',
                        'atlanta':'atl',
                        'carolina':'car',
                        'new orleans':'nos',
                        'tampa bay':'tbb',
                        'arizona':'ari',
                        'los angeles rams':'lar',
                        'san francisco':'sff',
                        'seattle':'sea'}
        
    else: # basketball
        # even tho 2 teams in LA 1 labeled LA and other Los Angeles
        team_locs = {'atlanta':'atl', 
                    'boston':'bos', 
                    'brooklyn':'bk', 
                    'charlotte':'cha', 
                    'chicago':'chi',
                    'cleveland':'cle',
                    'dallas':'dal',
                    'denver':'den',
                    'detroit':'det',
                    'golden state':'gs',
                    'houston':'hou',
                    'indiana':'ind',
                    'las vegas':'lv',
                    'la':'la',
                    'los angeles':'la',
                    'memphis':'mem',
                    'miami':'mia',
                    'milwaukee':'mil',
                    'minnesota':'min',
                    'new orleans':'no',
                    'new york':'ny',
                    'oklahoma city':'okc',
                    'orlando':'orl',
                    'philadelphia':'phi',
                    'phoenix':'pho',
                    'portland':'por',
                    'sacramento':'sac',
                    'san antonio':'sa',
                    'toronto':'tor',
                    'utah':'uta',
                    'washington':'wsh'} # could get from fantasy pros table but simpler to make once bc only 30 immutable vals
    



    # hard fail so we can correct name
    #if team_name in team_abbrevs.keys():
    abbrev = team_locs[team_loc]
    # else:
    #     print('Warning: Unknown team name! ' + team_name)

    #print('abbrev: ' + abbrev)
    return abbrev

def convert_team_loc_to_abbrev(team_loc, sport=''):
    #print('\n===Convert Team Location to Abbrev: ' + team_name + '===\n')
    
    abbrev = ''

    
    # for baseball, need logo info bc multiple teams same city
    if sport == 'baseball':
        team_locs = {'chicago':'chi',
                        'cleveland':'cle',
                        'detroit':'det',
                        'kansas city':'kc', #KC
                        'kansas':'kc', #KC
                        'minnesota':'min',
                        'baltimore':'bal',
                        'boston':'bos',
                        'new york':'ny',
                        'new':'ny',
                        'tampa bay':'tb',
                        'tampa':'tb',
                        'toronto':'tor',
                        'houston':'hou',
                        'los angeles':'la',
                        'oakland':'oak',
                        'seattle':'sea',
                        'texas':'tex',
                        'cincinnati':'cin',
                        'milwaukee':'mil',
                        'pittsburgh':'pit',
                        'st louis':'stl',
                        'st':'stl',
                        'atlanta':'atl',
                        'miami':'mia',
                        'philadelphia':'phi',
                        'washington':'was',
                        'arizona':'ari',
                        'colorado':'col',
                        'san diego':'sd',
                        'san francisco':'sf'}
        
    elif sport == 'hockey':
        team_locs = {'boston':'bos',
                        'buffalo':'buf',
                        'detroit':'det',
                        'florida':'fla',
                        'montreal':'mtl',
                        'ottawa':'ott',
                        'tampa bay':'tb',
                        'toronto':'tor',
                        'arizona':'ari',
                        'chicago':'chi',
                        'colorado':'col',
                        'dallas':'dal',
                        'minnesota':'min',
                        'nashville':'nsh',
                        'st louis':'stl',
                        'winnipeg':'wpg',
                        'carolina':'car',
                        'columbus':'cb',
                        'new jersey':'nj',
                        'new york islanders':'ny',
                        'new york rangers':'ny',
                        'new york':'ny',
                        'philadelphia':'phi',
                        'pittsburgh':'pit',
                        'washington':'wsh',
                        'anaheim':'ana',
                        'calgary':'cgy',
                        'edmonton':'edm',
                        'los angeles':'la',
                        'san jose':'sj',
                        'seattle':'sea',
                        'vancouver':'van',
                        'vegas':'vg',
                        'las vegas':'lv'}
    elif sport == 'football':
        team_locs = {'buffalo':'buf',
                        'miami':'mia',
                        'new england':'ne',
                        'new york jets':'ny',
                        'new york':'ny',
                        'baltimore':'bal',
                        'cincinnati':'cin',
                        'cleveland':'cle',
                        'pittsburgh':'pit',
                        'houston':'hou',
                        'indianapolis':'ind',
                        'jacksonville':'jax',
                        'tennessee':'ten',
                        'denver':'den',
                        'kansas city':'kc',
                        'las vegas':'lv',
                        'los angeles colts':'la',
                        'los angeles':'la',
                        'dallas':'dal',
                        'new york giants':'ny',
                        'philadelphia':'phi',
                        'washington':'wsh',
                        'chicago':'chi',
                        'detroit':'det',
                        'green bay':'gb',
                        'minnesota':'min',
                        'atlanta':'atl',
                        'carolina':'car',
                        'new orleans':'no',
                        'tampa bay':'tb',
                        'arizona':'ari',
                        'los angeles rams':'la',
                        'san francisco':'sf',
                        'seattle':'sea'}
        
    else: # basketball
        # even tho 2 teams in LA 1 labeled LA and other Los Angeles
        team_locs = {'atlanta':'atl', 
                    'boston':'bos', 
                    'brooklyn':'bkn', 
                    'charlotte':'cha', 
                    'chicago':'chi',
                    'cleveland':'cle',
                    'connecticut':'con',
                    'dallas':'dal',
                    'denver':'den',
                    'detroit':'det',
                    'golden state':'gs',
                    'houston':'hou',
                    'indiana':'ind',
                    'las vegas':'lv',
                    'la':'lac',
                    'los angeles':'la',
                    'memphis':'mem',
                    'miami':'mia',
                    'milwaukee':'mil',
                    'minnesota':'min',
                    'new orleans':'no',
                    'new york':'ny',
                    'oklahoma city':'okc',
                    'orlando':'orl',
                    'philadelphia':'phi',
                    'phoenix':'phx',
                    'portland':'por',
                    'sacramento':'sac',
                    'san antonio':'sa',
                    'toronto':'tor',
                    'utah':'uta',
                    'washington':'wsh'} # could get from fantasy pros table but simpler to make once bc only 30 immutable vals
    



    # hard fail so we can correct name
    #if team_name in team_abbrevs.keys():
    abbrev = team_locs[team_loc]
    # else:
    #     print('Warning: Unknown team name! ' + team_name)

    #print('abbrev: ' + abbrev)
    return abbrev

def convert_team_loc_to_source_abbrev(team_loc, sport='', source=''):
    print('\n===Convert Team Location to Source Abbrev: ' + team_loc + '===\n')
    
    abbrev = ''

    # remove dots
    team_loc = re.sub('\.', '', team_loc)

    if source == 'betrivers':
        # for baseball, need logo info bc multiple teams same city
        if sport == 'baseball':
            team_locs = {'chicago':'chi',
                            'cleveland':'cle',
                            'detroit':'det',
                            'kansas city':'kc', #KC
                            'kansas':'kc', #KC
                            'minnesota':'min',
                            'baltimore':'bal',
                            'boston':'bos',
                            'new york':'ny',
                            'new':'ny',
                            'tampa bay':'tb',
                            'tampa':'tb',
                            'toronto':'tor',
                            'houston':'hou',
                            'los angeles':'la',
                            'oakland':'oak',
                            'seattle':'sea',
                            'texas':'tex',
                            'cincinnati':'cin',
                            'milwaukee':'mil',
                            'pittsburgh':'pit',
                            'st louis':'stl',
                            'st':'stl',
                            'atlanta':'atl',
                            'miami':'mia',
                            'philadelphia':'phi',
                            'washington':'was',
                            'arizona':'ari',
                            'colorado':'col',
                            'san diego':'sd',
                            'san francisco':'sf'}
            
        elif sport == 'hockey':
            team_locs = {'boston':'bos',
                            'buffalo':'buf',
                            'detroit':'det',
                            'florida':'fla',
                            'montreal':'mtl',
                            'ottawa':'ott',
                            'tampa bay':'tbl',
                            'toronto':'tor',
                            'arizona':'ari',
                            'chicago':'chi',
                            'colorado':'col',
                            'dallas':'dal',
                            'minnesota':'min',
                            'nashville':'nsh',
                            'st louis':'stl',
                            'winnipeg':'wpg',
                            'carolina':'car',
                            'columbus':'cbj',
                            'new jersey':'njd',
                            'new york islanders':'nyi',
                            'new york rangers':'nyr',
                            'philadelphia':'phi',
                            'pittsburgh':'pit',
                            'washington':'wsh',
                            'anaheim':'ana',
                            'calgary':'cgy',
                            'edmonton':'edm',
                            'los angeles':'lak',
                            'san jose':'sjs',
                            'seattle':'sea',
                            'vancouver':'van',
                            'vegas':'vgk'}
        elif sport == 'football':
            team_locs = {'buffalo':'buf',
                            'miami':'mia',
                            'new england':'ne',
                            'new york':'ny',
                            'new york jets':'ny',
                            'baltimore':'bal',
                            'cincinnati':'cin',
                            'cleveland':'cle',
                            'pittsburgh':'pit',
                            'houston':'hou',
                            'indianapolis':'ind',
                            'jacksonville':'jax',
                            'tennessee':'ten',
                            'denver':'den',
                            'kansas city':'kc',
                            'las vegas':'lv',
                            'los angeles':'la',
                            'los angeles colts':'la',
                            'dallas':'dal',
                            'new york giants':'ny',
                            'philadelphia':'phi',
                            'washington':'was',
                            'chicago':'chi',
                            'detroit':'det',
                            'green bay':'gb',
                            'minnesota':'min',
                            'atlanta':'atl',
                            'carolina':'car',
                            'new orleans':'no',
                            'tampa bay':'tb',
                            'arizona':'ari',
                            'los angeles rams':'la',
                            'san francisco':'sf',
                            'seattle':'sea',
                            # CFL
                            'hamilton':'ham',
                            'montreal':'mtl',
                            'toronto':'tor',
                            'winnipeg':'wpg',
                            'british columbia':'bc',
                            'calgary':'cal',
                            'edmonton':'edm',
                            'sasketchewan':'ssk',
                            'ottawa':'ott'}
            
        else: # basketball
            # even tho 2 teams in LA 1 labeled LA and other Los Angeles
            team_locs = {'atlanta':'atl', 
                        'boston':'bos', 
                        'brooklyn':'bk', 
                        'charlotte':'cha', 
                        'chicago':'chi',
                        'cleveland':'cle',
                        'connecticut':'con',
                        'dallas':'dal',
                        'denver':'den',
                        'detroit':'det',
                        'golden state':'gs',
                        'houston':'hou',
                        'indiana':'ind',
                        'las vegas':'lv',
                        'la':'la',
                        'los angeles':'la',
                        'memphis':'mem',
                        'miami':'mia',
                        'milwaukee':'mil',
                        'minnesota':'min',
                        'new orleans':'no',
                        'new york':'ny',
                        'oklahoma city':'okc',
                        'orlando':'orl',
                        'philadelphia':'phi',
                        'phoenix':'pho',
                        'portland':'por',
                        'sacramento':'sac',
                        'san antonio':'sa',
                        'toronto':'tor',
                        'utah':'uta',
                        'washington':'was'} # could get from fantasy pros table but simpler to make once bc only 30 immutable vals
    
    else:

            # for baseball, need logo info bc multiple teams same city
        if sport == 'baseball':
            team_locs = {'chicago':'chi',
                            'cleveland':'cle',
                            'detroit':'det',
                            'kansas city':'kc', #KC
                            'kansas':'kc', #KC
                            'minnesota':'min',
                            'baltimore':'bal',
                            'boston':'bos',
                            'new york':'ny',
                            'new':'ny',
                            'tampa bay':'tb',
                            'tampa':'tb',
                            'toronto':'tor',
                            'houston':'hou',
                            'los angeles':'la',
                            'oakland':'oak',
                            'seattle':'sea',
                            'texas':'tex',
                            'cincinnati':'cin',
                            'milwaukee':'mil',
                            'pittsburgh':'pit',
                            'st louis':'stl',
                            'st':'stl',
                            'atlanta':'atl',
                            'miami':'mia',
                            'philadelphia':'phi',
                            'washington':'was',
                            'arizona':'ari',
                            'colorado':'col',
                            'san diego':'sd',
                            'san francisco':'sf'}
            
        elif sport == 'hockey':
            team_locs = {'boston':'bos',
                            'buffalo':'buf',
                            'detroit':'det',
                            'florida':'fla',
                            'montreal':'mtl',
                            'ottawa':'ott',
                            'tampa bay':'tbl',
                            'toronto':'tor',
                            'arizona':'ari',
                            'chicago':'chi',
                            'colorado':'col',
                            'dallas':'dal',
                            'minnesota':'min',
                            'nashville':'nsh',
                            'st louis':'stl',
                            'winnipeg':'wpg',
                            'carolina':'car',
                            'columbus':'cbj',
                            'new jersey':'njd',
                            'new york islanders':'nyi',
                            'new york rangers':'nyr',
                            'philadelphia':'phi',
                            'pittsburgh':'pit',
                            'washington':'wsh',
                            'anaheim':'ana',
                            'calgary':'cgy',
                            'edmonton':'edm',
                            'los angeles':'lak',
                            'san jose':'sjs',
                            'seattle':'sea',
                            'vancouver':'van',
                            'vegas':'vgk'}
        elif sport == 'football':
            team_locs = {'buffalo':'buf',
                            'miami':'mia',
                            'new england':'ne',
                            'new york jets':'ny',
                            'baltimore':'bal',
                            'cincinnati':'cin',
                            'cleveland':'cle',
                            'pittsburgh':'pit',
                            'houston':'hou',
                            'indianapolis':'ind',
                            'jacksonville':'jax',
                            'tennessee':'ten',
                            'denver':'den',
                            'kansas city':'kc',
                            'las vegas':'lv',
                            'los angeles colts':'la',
                            'dallas':'dal',
                            'new york giants':'ny',
                            'philadelphia':'phi',
                            'washington':'was',
                            'chicago':'chi',
                            'detroit':'det',
                            'green bay':'gb',
                            'minnesota':'min',
                            'atlanta':'atl',
                            'carolina':'car',
                            'new orleans':'no',
                            'tampa bay':'tb',
                            'arizona':'ari',
                            'los angeles rams':'la',
                            'san francisco':'sf',
                            'seattle':'sea',
                            # CFL
                            'hamilton':'ham',
                            'montreal':'mtl',
                            'toronto':'tor',
                            'winnipeg':'wpg',
                            'british columbia':'bc',
                            'calgary':'cal',
                            'edmonton':'edm',
                            'sasketchewan':'ssk',
                            'ottawa':'ott'}
            
        else: # basketball
            # even tho 2 teams in LA 1 labeled LA and other Los Angeles
            team_locs = {'atlanta':'atl', 
                        'boston':'bos', 
                        'brooklyn':'bk', 
                        'charlotte':'cha', 
                        'chicago':'chi',
                        'cleveland':'cle',
                        'connecticut':'con',
                        'dallas':'dal',
                        'denver':'den',
                        'detroit':'det',
                        'golden state':'gs',
                        'houston':'hou',
                        'indiana':'ind',
                        'las vegas':'lv',
                        'la':'lac',
                        'los angeles':'lal',
                        'memphis':'mem',
                        'miami':'mia',
                        'milwaukee':'mil',
                        'minnesota':'min',
                        'new orleans':'no',
                        'new york':'ny',
                        'oklahoma city':'okc',
                        'orlando':'orl',
                        'philadelphia':'phi',
                        'phoenix':'pho',
                        'portland':'por',
                        'sacramento':'sac',
                        'san antonio':'sa',
                        'toronto':'tor',
                        'utah':'uta',
                        'washington':'was'}


    # hard fail so we can correct name
    #if team_name in team_abbrevs.keys():
    abbrev = team_locs[team_loc]
    # else:
    #     print('Warning: Unknown team name! ' + team_name)

    #print('abbrev: ' + abbrev)
    return abbrev

def convert_team_name_to_loc_abbrev(team_name):
    #print('\n===Convert Team Name to Loc Abbrev: ' + team_name + '===\n')
    
    abbrev = ''

    # ensure lowercase and no dots
    team_name = re.sub('\.','',team_name).lower()

    team_abbrevs = {'atlanta hawks':'atl', 
                    'boston celtics':'bos', 
                    'brooklyn nets':'bkn', 
                    'charlotte hornets':'cha', 
                    'chicago bulls':'chi',
                    'cleveland cavaliers':'cle',
                    'dallas mavericks':'dal',
                    'denver nuggets':'den',
                    'detroit pistons':'det',
                    'golden state warriors':'gsw',
                    'houston rockets':'hou',
                    'indiana pacers':'ind',
                    'la clippers':'lac',
                    'los angeles lakers':'lal',
                    'memphis grizzlies':'mem',
                    'miami heat':'mia',
                    'milwaukee bucks':'mil',
                    'minnesota timberwolves':'min',
                    'new orleans pelicans':'nop',
                    'new york knicks':'nyk',
                    'oklahoma city thunder':'okc',
                    'orlando magic':'orl',
                    'philadelphia 76ers':'phi',
                    'phoenix suns':'phx',
                    'portland trail blazers':'por',
                    'sacramento kings':'sac',
                    'san antonio spurs':'sas',
                    'toronto raptors':'tor',
                    'utah jazz':'uta',
                    'washington wizards':'wsh',
                    # WNBA
                    'las vegas aces':'lv',
                    # Baseball
                    'chicago white sox':'chw',
                    'cleveland guardians':'cle',
                    'detroit tigers':'det',
                    'kansas city royals':'kcr', #KC
                    'minnesota twins':'min',
                    'baltimore orioles':'bal',
                    'boston red sox':'bos',
                    'new york yankees':'nyy',
                    'tampa bay rays':'tbr',
                    'toronto blue jays':'tor',
                    'houston astros':'hou',
                    'los angeles angels':'laa',
                    'oakland athletics':'oak',
                    'seattle mariners':'sea',
                    'texas rangers':'tex',
                    'chicago cubs':'chc',
                    'cincinnati reds':'cin',
                    'milwaukee brewers':'mil',
                    'pittsburgh pirates':'pit',
                    'st louis cardinals':'stl',
                    'atlanta braves':'atl',
                    'miami marlins':'mia',
                    'new york mets':'nym',
                    'philadelphia phillies':'phi',
                    'washington nationals':'wsh',
                    'arizona diamondbacks':'ari',
                    'colorado rockies':'col',
                    'los angeles dodgers':'lad',
                    'san diego padres':'sdp',
                    'san francisco giants':'sfg',
                    # Hockey
                    'boston bruins':'bos',
                    'buffalo sabres':'buf',
                    'detroit red wings':'det',
                    'florida panthers':'fla',
                    'montreal canadiens':'mtl',
                    'ottawa senators':'ott',
                    'tampa bay lightning':'tbl',
                    'toronto maple leafs':'tor',
                    'arizona coyotes':'ari',
                    'chicago blackhawks':'chi',
                    'colorado avalanche':'col',
                    'dallas stars':'dal',
                    'minnesota wild':'min',
                    'nashville predators':'nsh',
                    'st louis blues':'stl',
                    'winnipeg jets':'wpg',
                    'carolina hurricanes':'car',
                    'columbus blue jackets':'cbj',
                    'new jersey devils':'njd',
                    'new york islanders':'nyi',
                    'new york rangers':'nyr',
                    'philadelphia flyers':'phi',
                    'pittsburgh penguins':'pit',
                    'washington capitals':'wsh',
                    'anaheim ducks':'ana',
                    'calgary flames':'cgy',
                    'edmonton oilers':'edm',
                    'los angeles kings':'lak',
                    'san jose sharks':'sjs',
                    'seattle kraken':'sea',
                    'vancouver canucks':'van',
                    'vegas golden knights':'vgk',
                    # Football
                    'buffalo bills':'buf',
                    'miami dolphins':'mia',
                    'new england patriots':'nep',
                    'new york jets':'nyj',
                    'baltimore ravens':'bal',
                    'cincinnati bengals':'cin',
                    'cleveland browns':'cle',
                    'pittsburgh steelers':'pit',
                    'houston texans':'hou',
                    'indianapolis colts':'ind',
                    'jacksonville jaguars':'jax',
                    'tennessee titans':'ten',
                    'denver broncos':'den',
                    'kansas city chiefs':'kcc',
                    'las vegas raiders':'lvr',
                    'los angeles chargers':'lac',
                    'dallas cowboys':'dal',
                    'new york giants':'nyg',
                    'philadelphia eagles':'phi',
                    'washington commanders':'wsh',
                    'chicago bears':'chi',
                    'detroit lions':'det',
                    'green bay packers':'gbp',
                    'minnesota vikings':'min',
                    'atlanta falcons':'atl',
                    'carolina panthers':'car',
                    'new orleans saints':'nos',
                    'tampa bay buccaneers':'tbb',
                    'arizona cardinals':'ari',
                    'los angeles rams':'lar',
                    'san francisco 49ers':'sff',
                    'seattle seahawks':'sea'} # could get from fantasy pros table but simpler to make once bc only 30 immutable vals

    # hard fail so we can correct name?
    # Problem is we need to filter by sport
    # so if name not here then consider not needed
    if team_name in team_abbrevs.keys():
        abbrev = team_abbrevs[team_name]
    # else:
    #     print('Warning: Unknown team name! ' + team_name)

    #print('abbrev: ' + abbrev)
    return abbrev

def convert_team_abbrev_to_name(team_abbrev):
    #print('\n===Convert Team Abbrev to Name: ' + team_abbrev + '===\n')
    
    name = ''

    team_names = {'atl':'atlanta hawks', 
                    'bos':'boston celtics', 
                    'bkn':'brooklyn nets', 
                    'cha':'charlotte hornets', 
                    'chi':'chicago bulls',
                    'cle':'cleveland cavaliers',
                    'dal':'dallas mavericks',
                    'den':'denver nuggets',
                    'det':'detroit pistons',
                    'gsw':'golden state warriors',
                    'hou':'houston rockets',
                    'ind':'indiana pacers',
                    'lac':'la clippers',
                    'lal':'los angeles lakers',
                    'mem':'memphis grizzlies',
                    'mia':'miami heat',
                    'mil':'milwaukee bucks',
                    'min':'minnesota timberwolves',
                    'nop':'new orleans pelicans',
                    'nyk':'new york knicks',
                    'okc':'oklahoma city thunder',
                    'orl':'orlando magic',
                    'phi':'philadelphia 76ers',
                    'phx':'phoenix suns',
                    'por':'portland trail blazers',
                    'sac':'sacramento kings',
                    'sas':'san antonio spurs',
                    'tor':'toronto raptors',
                    'uta':'utah jazz',
                    'wsh':'washington wizards'} # could get from fantasy pros table but simpler to make once bc only 30 immutable vals

    if team_abbrev in team_names.keys():
        name = team_names[team_abbrev]

    #print('name: ' + name)
    return name

# Convert Player Name to Abbrev: damion lee
# what is the diff bt this and determine player abbrev?
# determine player abbrev take first inital and last names simply
# where this fcn gets list of saved player abbrevs
# how to tell if different players have same name so are actually meant to have separate abbrevs?
# will they be on team different teams?
# what if players have same name on same team? then it would incorrectly take both players abbrevs as 1 players abbrevs
# i think odds are low enough to treat main case and flag when 2 players on same team have same name
def convert_player_name_to_abbrevs(game_player, all_players_abbrevs, game_player_team='', player_teams={}, all_players_teams={}, all_box_scores={}, season_years=[], cur_yr='', prints_on=True):
    # if prints_on:
    #     print('\n===Convert Player Name to Abbrevs: ' + game_player.title() + '===\n')
    #     print('Input: game_player_team = ' + game_player_team)
    #     print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-mem\': \'jaren jackson jr\',...')# + str(all_players_abbrevs))

    game_player_abbrevs = []


    # we need dict of player teams to get team at time of game
    # we need all matching player abbrevs but in this case we are comparing to teammates 
    # so should it be restricted to only current team?

    # go thru all abbrevs to find given players abbrevs by matching name and team
    for year, year_players_abbrev in all_players_abbrevs.items():
        #print('\nyear: ' + year)
        for abbrev_key, name in year_players_abbrev.items():
            
            abbrev_data = abbrev_key.split('-')
            abbrev = abbrev_data[0]
            
            team = abbrev_data[1]

            # if prints_on:
            #     print('\nabbrev_key: ' + abbrev_key)
            #     print('abbrev: ' + str(abbrev))
            #     print('name: ' + str(name))
            #     print('game_player: ' + str(game_player))
            #     print('team: ' + str(team))
            #     print('game_player_team: ' + str(game_player_team))
            # loop thru teams played this yr to ensure correct abbrev or else might find same abbrev for diff player
            if game_player_team != '' :
                if name == game_player and team == game_player_team:
                    #print('found abbrev')
                    game_player_abbrevs.append(abbrev)
                    #print('game_player_abbrevs: ' + str(game_player_abbrevs))
            
            elif len(player_teams.keys()) > 0:
                #print('Not given game player team of interest so check all teams.')
                # should always have year in teams bc abbrev from box score which also gets player teams
                #if year in player_teams.keys():
                year_teams_dict = player_teams[year]
                year_teams = list(year_teams_dict.keys())#convert_player_teams_dict_to_list(year_teams_dict)
                for gp_team in year_teams:
                    if name == game_player and team == gp_team:
                        
                        game_player_abbrevs.append(abbrev_key)
                        # print('found abbrev')
                        # print('game_player_abbrevs: ' + str(game_player_abbrevs))
            

        # we only add abbrevs from year of interest?
        # keep yrs separate
        # but if abbrev not available in cur yr then maybe in prev yr bc player played last yr but not this yr
        if len(game_player_abbrevs) > 0:
            #print('found abbrev for ' + game_player)
            break

        # look for all abbrevs in all yrs so we can find current player in past yrs with different abbrevs

    # if prints_on:
    #     print('game_player_abbrevs: ' + str(game_player_abbrevs))
    return game_player_abbrevs

def convert_irregular_player_name(player_name):

    player_name = re.sub('−|-',' ',player_name).lower()
    # do we need to remove ' bc seems to work with it???
    player_name = re.sub('\.','',player_name)

    if player_name == 'nicolas claxton':
        player_name = 'nic claxton'
    elif player_name == 'cameron thomas':
        player_name = 'cam thomas'
    elif player_name == 'gregory jackson':
        player_name = 'gg jackson'
    elif player_name == 'kelly oubre':
        player_name = 'kelly oubre jr'

    return player_name

# CHANGED to get list of all abbrevs
# Convert Player Name to Abbrev: damion lee
# what is the diff bt this and determine player abbrevs?
# determine abbrev simply truncates name
# def convert_player_name_to_abbrevs(game_player, all_players_abbrevs):
#     # print('\n===Convert Player Name to Abbrevs: ' + game_player.title() + '===\n')
#     # print('all_players_abbrevs: ' + str(all_players_abbrevs))

#     game_player_abbrevs = []

#     # some players w/ jr/sr have 2 entries
#     for year_players_abbrev in all_players_abbrevs.values():
#         for abbrev_key, name in year_players_abbrev.items():
#             abbrev_data = abbrev_key.split('-')
#             abbrev = abbrev_data[0]

#             # CAUTION: does this cause mismatch
#             # we want kelly oubre to match kelly oubre jr
#             # but are there any irregular cases where 1 players name fits in another players name???
#             #if name == game_player:
#             if re.search(game_player, name) and abbrev not in game_player_abbrevs:
#                 game_player_abbrevs.append(abbrev)



#     #print('game_player_abbrevs: ' + str(game_player_abbrevs))
#     return game_player_abbrevs

# CHANGE to get list of all abbrevs
# Convert Player Name to Abbrev: damion lee
# what is the diff bt this and determine player abbrev?
# determine abbrev simply truncates name
def convert_player_name_to_abbrev(game_player, all_players_abbrevs, gp_team):
    # print('\n===Convert Player Name to Abbrev: ' + game_player.title() + '===\n')
    # print('Input: gp_team = ' + gp_team.upper())
    # print('all_players_abbrevs: ' + str(all_players_abbrevs))

    game_player_abbrev = ''

    # some players w/ jr/sr have 2 entries
    for year_players_abbrev in all_players_abbrevs.values():
        for abbrev_key, name in year_players_abbrev.items():
            abbrev_data = abbrev_key.split('-')
            abbrev = abbrev_data[0]
            team = abbrev_data[1]

            # CAUTION: does this cause mismatch
            # we want kelly oubre to match kelly oubre jr
            # but are there any irregular cases where 1 players name fits in another players name???
            #if name == game_player:
            if re.search(game_player, name) and team == gp_team:
                game_player_abbrev = abbrev#all_players_abbrevs[game_player]#convert_player_name_to_abbrev(game_player, all_players_abbrevs, all_players_teams, all_box_scores, season_years, cur_yr)
                break

        if game_player_abbrev != '':
            break






    # it is looking for cur yr so how does it handle players who played last yr but are still on team but not playing this yr?
    # player does not register on teams list if not played this yr so need to check roster
    # if player of interest has not played with player this yr 
    # but did play with them previous seasons and they are listed as out, then this is a case of player still on team but stopped playing time for any reason
    # should we loop thru all yrs until we find abbrev? 
    # really only need 1 yr bc player still on team but not played so unlikely to be on team without playing for more than a yr but possible
    # if len(season_years) == 0 and cur_yr != '':
    #     if cur_yr in all_players_abbrevs.keys() and game_player in all_players_abbrevs[cur_yr].keys():
    #         game_player_abbrev = all_players_abbrevs[cur_yr][game_player] #converter.convert_player_name_to_abbrev(out_player)
    #     else:
    #         if cur_yr in all_players_teams.keys() and game_player in all_players_teams[cur_yr].keys():
    #             # out_player_teams = all_players_teams[cur_yr][out_player]
    #             # out_player_team = determiner.determine_player_current_team(out_player, out_player_teams, cur_yr, rosters)
    #             game_player_abbrev = reader.read_player_abbrev(game_player, all_players_teams, cur_yr, all_box_scores)
    #         else:
    #             print('Warning: Game player not in all players current teams! ' + game_player)
    # else:
    #     for year in season_years:
    #         #print('\nyear: ' + str(year))
    #         if year in all_players_abbrevs.keys() and game_player in all_players_abbrevs[year].keys():
    #             year_players_abbrevs = all_players_abbrevs[year]
    #             #print('year_players_abbrevs: ' + str(year_players_abbrevs))
    #             game_player_abbrev = year_players_abbrevs[game_player] #converter.convert_player_name_to_abbrev(out_player)
    #         else:
    #             if year in all_players_teams.keys() and game_player in all_players_teams[year].keys():
    #                 game_player_abbrev = reader.read_player_abbrev(game_player, all_players_teams, year, all_box_scores)
    #             else:
    #                 print('Warning: Game player not in all players teams! ' + game_player + ', ' + str(year))

    #         if game_player_abbrev != '':
    #             break

    #print('game_player_abbrev: ' + str(game_player_abbrev))
    return game_player_abbrev

# CHANGE to get list of all abbrevs bc each player may have multiple
# we know all players on same team bc called from in team part loop
def convert_all_players_names_to_abbrevs(players, all_players_abbrevs, gp_team):
    # print('\n===Convert All Players Names to Abbrevs===\n')
    # print('Input: players = ' + str(players))
    # print('Input: gp_team = ' + gp_team.upper())
    # print('\nOutput: abbrevs = [abbrev1,...]\n')
    
    abbrevs = []
    
    for player in players:
        # check both forms of name
        abbrev = convert_player_name_to_abbrev(player, all_players_abbrevs, gp_team)
        if abbrev == '' and re.search('\'', player):
            player = re.sub('\'','',player).strip()
            abbrev = convert_player_name_to_abbrev(player, all_players_abbrevs, gp_team)
        
        if abbrev != '': # blank if not played on team yet bc abbrev got from box score
            abbrevs.append(abbrev)

    #print('abbrevs: ' + str(abbrevs))
    return abbrevs

# combine all names into single string condition, alphabet order
# generic function, convert list to string (alphabetized)
def convert_list_to_str(list, order='alphabet'):
    print('\n===Convert List to String===\n')
    print('Input: game_players = [player abbrev, ...] = [A Gordon PF, ...]')
    print('\nOutput: game_players_str = \'player abbrev, ...\' = \'A Gordon PF, ...\'\n')

    string = ''
    if order == 'alphabet':
        list = sorted(list)

    for idx in range(len(list)):
        item = list[idx]
        # add condition for all game players in combo
        if idx == 0:
            string = item
        else:
            string += ', ' + item

    return string

# combine all names into single string condition, alphabet order
# generic function, convert list to string (alphabetized)
def convert_to_game_players_str(game_players):
    # print('\n===Convert to Game Players String===\n')
    # print('Input: game_players = [player abbrev, ...] = [A Gordon PF, ...] = ' + str(game_players))
    # print('\nOutput: game_players_str = \'player abbrev, ...\' = \'A Gordon PF, ...\'\n')

    game_players_str = ''
    game_players = sorted(game_players)
    for game_player_idx in range(len(game_players)):
        game_player_abbrev = game_players[game_player_idx]
        # add condition for all game players in combo
        if game_player_idx == 0:
            game_players_str = game_player_abbrev
        else:
            game_players_str += ', ' + game_player_abbrev

    #print('game_players_str: ' + str(game_players_str))
    return game_players_str

# convert cond dict to list
#all_current_conditions: {'cole anthony': {'loc': 'away', 'out': ['wendell carter jr', 'markelle fultz'], 'start...
# all_current_conditions = {p1:{out:[m fultz pg], loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
# list = away, 'p1 out', 'p2 out', ...
# need to expand list values
# OLD: conditions_list = ['m fultz pg out', 'w carter c out', 'm fultz pg, w carter c out', 'away', ...]
# conditions_list = ['m fultz pg, w carter c out', 'away', ...]
# for player conditions only show list of players together but later will account for sub weights of single player conditions
def convert_conditions_to_dict(conditions, all_players_abbrevs, all_players_teams, all_box_scores, player='', season_years=[], cur_yr=''):
    # print('\n===Convert Conditions Dict to List: ' + player.title() + '===\n')
    # print('Input: Player of Interest')
    # print('Input: conditions = {starters:[s1,...], loc:l1, city:c1, dow:d1, tod:t1,...}, ... = {\'loc\': \'away\', \'out\': [\'vlatko cancar\',...], ...')
    # print('Input: all_players_abbrevs = {year:{abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF\': \'jaren jackson jr\',...')
    # print('\nOutput: conditions_dict = {loc:away, start:start, prev:5, ... = ')
    # print('Output: gp_conds_dict = {teammates: {starters:[],...}, opp: {...}}, ... = \n')

    #print('all_players_abbrevs: ' + str(all_players_abbrevs))

    conditions_dict = {}

    teammates_key = 'teammates'
    opp_key = 'opp'
    gp_conds_dict = {teammates_key:{}, opp_key:{}}

    game_players_cond_keys = ['out', 'starters', 'bench']

    game_players = []
    in_key = 'in'
    
    for cond_key, cond_val in conditions.items():
        # print('cond_key: ' + str(cond_key))
        # print('cond_val: ' + str(cond_val))
        
        if cond_key in game_players_cond_keys:#== 'out':
            #print('game player condition')
            
            gp_conds_dict[teammates_key][cond_key] = cond_val
        
        elif re.search(opp_key, cond_key) and cond_key != 'opp team':
            cond_key = re.sub('opp ','',cond_key) # opp shown in top level so dont repeat?
            gp_conds_dict[opp_key][cond_key] = cond_val

            # game_part_players = []
            
            # for game_player_idx in range(len(cond_val)):
            #     game_player = cond_val[game_player_idx]
            #     print('\ngame_player: ' + str(game_player))
            #     # need to convert player full name to abbrev with position to compare to condition titles
            #     # at this point we have determined full names from abbrevs so we can refer to that list
            #     # done: save player abbrevs for everyone played with
            #     # NEXT: enable multiple irregular abbrevs like X Tillman and Tillman Sr for xavier tillman
            #     # pass in list of players with multiple abbrevs so we dont have to check every player
            #     game_player_abbrev = convert_player_name_to_abbrev(game_player, all_players_abbrevs)
            #     # if blank abbrev, then practice player bc we got all abbrevs of players in games
            #     if game_player_abbrev != '':
        
            #         # if condition is multiplayer then we need to sort alphabetically
            #         #if re.search(',',conditions):
            #         game_part_players.append(game_player_abbrev)
            #         if cond_key != 'out': # player in game
            #             game_players.append(game_player_abbrev)
                        
                        # final_cond_val = game_player_abbrev + ' ' + in_key 
                        # #print('final_cond_val: ' + str(final_cond_val))
                        
                        # conditions_dict[final_cond_val] = in_key

            # cond val is list of players in part
            # if len(cond_val) > 0:
            #     game_part_players_str = convert_to_game_players_str(game_part_players)
                
            #     # game part players, where part = starters or bench or out
            #     #game_players_str += ' ' + cond_key
            #     game_part_players_cond_val = game_part_players_str + ' ' + cond_key 
            #     #print('game_part_players_cond_val: ' + str(game_part_players_cond_val))
            #     conditions_dict[game_part_players_cond_val] = cond_key


        else:
            conditions_dict[cond_key] = cond_val

    # add all players probs here bc we dont need in condition until now since we already have starters and bench which makes up in
    # we do not want to show in condition due to clutter but still account for it
    # if len(game_players) > 0: # all players in game
    #     game_players_str = convert_to_game_players_str(game_players)
            
    #     game_players_cond_val = game_players_str + ' ' + in_key
    #     #print('game_players_cond_val: ' + str(game_players_cond_val))
    #     conditions_dict[game_players_cond_val] = in_key

    # conditions_list: ['home', 'L Nance Jr PF out', 'M Ryan F out', 'L Nance Jr PF, M Ryan F out', 'C McCollum SG starters', 'B Ingram SF starters', 'H Jones SF starters', 'Z Williamson PF starters', 'J Valanciunas C starters', 'C McCollum SG, B Ingram SF, H Jones SF, Z Williamson PF, J Valanciunas C starters', 'bench']
    #print('conditions_dict: ' + str(conditions_dict))
    return (conditions_dict, gp_conds_dict)

# all_conditions_dicts = {p1:{out:[m fultz pg], loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
# all_conditions_lists = {p1:[m fultz pg out, away, ...],...
# seaprate groups of conditions with diff structs, eg game player conds
def convert_all_conditions_to_dicts(all_conditions, all_players_abbrevs, all_players_teams, all_box_scores, season_years=[], cur_yr=''):
    print('\n===Convert All Conditions Dicts to Lists===\n')
    print('Input: all_conditions = {p1:{starters:[s1,...], opp starters:[s1,...], loc:l1, city:c1, dow:d1, tod:t1,...}, ... = {\'nikola jokic\': {\'loc\': \'away\', \'out\': [\'vlatko cancar\',...], ...')# = ' + str(all_conditions))
    #print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-MEM\': \'jaren jackson jr\',...')
    # print('Input: all_players_teams = {player:{year:{team:gp,... = {\'bam adebayo\': {\'2018\': {\'mia\': 69}, ...\n')
    # print('Input: all_box_scores = {year:{game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
    # print('Input: Season Years of Interest')
    print('\nOutput: all_conditions_dicts = {p1:{loc:away, start:start, prev:5, ...} = {\'nikola jokic\': {loc:\'away\', ...')
    print('Output: all_game_player_cur_conds = {p1: {teammates: {starters:[],...}, opp: {...}}, ... = \n')

    all_conditions_dicts = {}
    all_game_player_cur_conds = {}

    for player, cond in all_conditions.items():
        cond_data = convert_conditions_to_dict(cond, all_players_abbrevs, all_players_teams, all_box_scores, player, season_years, cur_yr)
        
        cond_dict = cond_data[0]
        gp_cond_dict = cond_data[1]

        all_conditions_dicts[player] = cond_dict
        all_game_player_cur_conds[player] = gp_cond_dict

    # print('all_conditions_dicts: ' + str(all_conditions_dicts))
    # print('all_game_player_cur_conds: ' + str(all_game_player_cur_conds))
    return (all_conditions_dicts, all_game_player_cur_conds)