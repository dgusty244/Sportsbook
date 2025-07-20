from app.data_persistence import read_bets, read_balance
from app.betting_logic import place_bet, save_result, update_balance
from app.utils import pct, get_current_balance
from IPython.display import display

def dashboard():
    df = read_bets()

    wins = len(df[df.Result == 'W'])
    losses = len(df[df.Result == 'L'])
    pushes = len(df[df.Result == 'P'])

    record = f'{wins}-{losses}'
    if pushes > 0:
        record += f'-{pushes}'


    win_pct_denominator = wins + losses + pushes
    if win_pct_denominator > 0:
        win_pct = (wins + (pushes / 2)) / (wins + losses + pushes)
    else:
        win_pct = 0

    pending_bet_count = len(df[df.Result.isnull()])
    pending_bet_amount = df.loc[df.Result.isnull(), 'BetAmount'].sum()

    tot_bet = df.loc[~df.Result.isnull(), 'BetAmount'].sum()
    tot_paid_out = df.RealPayout.sum()

    if tot_bet >0:
        bets_roi = (tot_paid_out - tot_bet) / tot_bet
    else:
        bets_roi = 0

    bal_df = read_balance()
    tot_deposited = bal_df.loc[bal_df.Type == 'Deposit', 'Delta'].sum()

    print(f"""
Balance:             ${round(get_current_balance(), 2)}
Record:              {record}
Win Pct:             {pct(win_pct)}
Total Deposited:     ${tot_deposited}
Total Bet (Settled): ${tot_bet}
Total Paid Out:      ${round(tot_paid_out, 2)}
ROI on bets:         {pct(bets_roi)}
Pending:             {pending_bet_count} bets for ${pending_bet_amount}
""")

def make_deposit():
    amount = float(input('Deposit Amount: '))
    update_balance(delta=amount, _type='Deposit')

def main_menu():
    run = True
    while run:
        dashboard()
        try:
            main_screen_choice = int(input(f'''
Enter a number to make a choice.
1) Place Bet
2) Save Result
3) Make Deposit
4) View Bet History
5) View Balance History
6) Exit
'''))
        except ValueError:
            print("Invalid input, please enter a number 1-6.")
            continue

        if main_screen_choice == 1:
            try:
                place_bet()
            except Exception as e:
                print(f"Error placing bet: {e}")
        elif main_screen_choice == 2:
            try:
                save_result()
            except Exception as e:
                print(f"Error saving result: {e}")
        elif main_screen_choice == 3:
            try:
                make_deposit()
            except Exception as e:
                print(f"Error making deposit: {e}")
        elif main_screen_choice == 4:
            bets = read_bets()
            print(bets)
        elif main_screen_choice == 5:
            balance = read_balance()
            print(balance)
        elif main_screen_choice == 6:
            run = False
        else:
            print("Please choose a valid option between 1 and 6.")
