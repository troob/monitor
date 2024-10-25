# isolate things

def isolate_future_games(init_games, todays_date):
    print('\n===Isolate Future Games===\n')

    future_games = []

    for game in init_games:
        # Tue Jul 30
        game_date = game['game date']

        if game_date < todays_date:
            continue

        future_games.append(game)


    return future_games