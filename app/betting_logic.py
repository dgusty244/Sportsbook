import numpy as np
import pandas as pd
from app.data_persistence import read_bets, write_bets, update_balance, read_balance, write_balance
from app.utils import process_odds, get_date

def calc_to_win(ml, bet_amount):
    sign, num = process_odds(ml)

    if sign == '-':
        # need to bet variable 'num' to win 100
        winnings_ratio = 100 / num
    elif sign == '+':
        # need to bet 100 to win variable 'num'
        winnings_ratio = num / 100
    else:
        raise ValueError("Invalid odds sign")

    return round(bet_amount * winnings_ratio, 2)

def place_bet():
    # init variables in case not assigned
    spread = None
    o_u = None
    ml = None
    alt_bet_desc = None


    # get user inputs
    game_date = get_date(input('Game Date (Enter "t" if Today): '))
    away_team = input('Away Team: ').title()
    home_team = input('Home Team: ').title()
    bet_type = input('Bet Type (moneyline, point spread, over under, alternative): ').lower()



    if bet_type in ['ml', 'moneyline']:
        bet_type = 'Moneyline'
        selection = input('Team Selection [Home(h) Or Away(a)]: ').lower()
    elif bet_type in ['spread', 'point spread', 'pointspread', 'ps']:
        bet_type = 'Point Spread'
        selection = input('Team Selection [Home(h) Or Away(a)]: ').lower()
        spread_sign, spread_num = process_odds(input('Spread: '))
        spread = spread_sign + " " + str(spread_num)
    elif bet_type in ['ou', 'over under', 'overunder', 'over/under', 'o/u']:
        bet_type = 'Over Under'
        o_u = float(input('Over Under: '))
        selection = input('O/U Selection (enter "o" or "u"): ').lower()
    elif bet_type in ['alt', 'alternative', 'other']:
        alt_bet_desc = input('Alt Bet Description: ')
        selection = input('Alt Bet Selection: ')
    else:
        raise ValueError('Invalid bet type')

    ml = str(input('Moneyline On Bet: '))
    bet_amount = float(input('Bet Amount ($): '))

    # process selection input
    if bet_type.lower() not in ['alt', 'alternative', 'other']:
        if selection == 'h':
            selection = home_team
        elif selection == 'a':
            selection = away_team
        elif selection == 'o':
            selection = 'Over'
        elif selection == 'u':
            selection = 'Under'
        else:
            raise ValueError(f'Invalid selection: {selection}')

    # store historical bets and get next bet id
    hist_bet_df = read_bets()
    if len(hist_bet_df) > 0:
        this_bet_id = int(hist_bet_df.BetId.max() + 1)
    else:
        this_bet_id = 1

    # calculate to_win and potential_payout
    to_win = calc_to_win(ml, bet_amount)
    potential_payout = bet_amount + to_win

    # for now set result and real payout to NaN
    result = np.nan
    real_payout = np.nan

    # create dataframe for this bet's data
    this_bet_df = pd.DataFrame([[this_bet_id, game_date, away_team, home_team, bet_type, selection, ml, spread,
                                 o_u, alt_bet_desc, bet_amount, to_win, potential_payout, result, real_payout]],
                               columns=['BetId', 'GameDate', 'AwayTeam', 'HomeTeam', 'BetType', 'Selection', 'ML',
                                        'Spread', 'OverUnder', 'AltBetDescription', 'BetAmount', 'ToWin',
                                        'PotentialPayout', 'Result', 'RealPayout'])

    # append and write
    all_bet_df = pd.concat([hist_bet_df, this_bet_df], axis=0)
    write_bets(all_bet_df)

    # update balance
    update_balance(delta=-1 * bet_amount, _type='Bet Placed', bet_id=this_bet_id)

    # see if user knows result
    result_known = input('Do you know the result? (y/n) ').lower()
    if result_known not in ['y', 'n']:
        raise ValueError(f'Invalid result: {result_known}')
    if result_known == 'y':
        save_result(this_bet_id)

    # show the bet just placed
    print(read_bets().sort_values('BetId', ascending=False).head(1))

def save_result(bet_id=None):
    bet_df = read_bets()

    if not bet_id:
        print(bet_df[bet_df.Result.isnull()].sort_values('GameDate', ascending=False).head())
        bet_id = int(input('Bet Id: '))

    result = input('Result: (w/l/p): ').upper()
    if result not in ['W', 'L', 'P']:
        raise ValueError(f'Invalid Result: {result}')

    bet_df.loc[bet_df.BetId == bet_id, 'Result'] = result

    if result == 'W':
        real_payout = bet_df.loc[bet_df.BetId == bet_id, 'PotentialPayout'].item()
        bet_df.loc[bet_df.BetId == bet_id, 'RealPayout'] = real_payout
        update_balance(real_payout, 'Bet Won', bet_id=bet_id)
    elif result == 'P':
        real_payout = bet_df.loc[bet_df.BetId == bet_id, 'BetAmount']
        bet_df.loc[bet_df.BetId == bet_id, 'RealPayout'] = real_payout
        update_balance(real_payout, 'Bet Pushed', bet_id=bet_id)
    else:
        bet_df.loc[bet_df.BetId == bet_id, 'RealPayout'] = 0

    write_bets(bet_df)
