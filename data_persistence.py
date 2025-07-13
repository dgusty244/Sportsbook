import pandas as pd
import numpy as np
import datetime
import os

base_path = "./"  # Adjust if needed
default_bets_csv = "bets.csv"
default_balance_csv = "balance.csv"

def read_bets(additional_path=default_bets_csv):
    full_path = base_path + additional_path
    if not os.path.exists(full_path):
        # Create empty bets dataframe with correct columns
        columns = ['BetId', 'GameDate', 'AwayTeam', 'HomeTeam', 'BetType', 'Selection', 'ML',
                   'Spread', 'OverUnder', 'AltBetDescription', 'BetAmount', 'ToWin', 'PotentialPayout',
                   'Result', 'RealPayout']
        df = pd.DataFrame(columns=columns)
        df.to_csv(full_path, index=False)
        return df
    return pd.read_csv(full_path).sort_values(['GameDate', 'BetId'], ascending=False)

def read_balance(additional_path=default_balance_csv):
    full_path = base_path + additional_path
    if not os.path.exists(full_path):
        # Create balance file with initial row
        columns = ['BalanceId', 'Type', 'Delta', 'Balance', 'BetId', 'Timestamp']
        df = pd.DataFrame(columns=columns)
        df.loc[0] = [0, 'Init', 0.0, 0.0, np.nan, pd.Timestamp.now()]
        df.to_csv(full_path, index=False)
        return df
    return pd.read_csv(full_path).sort_values('Timestamp', ascending=False)

def write_bets(df, additional_path=default_bets_csv):
    full_path = base_path + additional_path
    df.to_csv(full_path, index=False)

def write_balance(df, additional_path=default_balance_csv):
    full_path = base_path + additional_path
    df.to_csv(full_path, index=False)

def update_balance(delta, _type, bet_id=np.nan):
    _type = _type.title()
    valid_types = ['Bet Placed', 'Deposit', 'Bet Won', 'Bet Pushed', 'Init']

    if _type not in valid_types:
        raise ValueError(f"type: {_type} must be in {valid_types}")

    balance_df = read_balance()

    if balance_df.empty:
        max_balance_id = 0
        old_balance = 0.0
    else:
        max_balance_id = balance_df.BalanceId.max()
        old_balance = balance_df.loc[balance_df.BalanceId == max_balance_id, 'Balance'].item()

    new_balance = old_balance + delta

    this_row_df = pd.DataFrame([[max_balance_id + 1, _type, delta, new_balance, bet_id, datetime.datetime.now()]],
                               columns=['BalanceId', 'Type', 'Delta', 'Balance', 'BetId', 'Timestamp'])

    new_df = pd.concat([balance_df, this_row_df], axis=0)
    write_balance(new_df)

def get_current_balance():
    df = read_balance()
    if df.empty:
        return 0.0
    max_id = df.BalanceId.max()
    balance = df.loc[df.BalanceId == max_id, 'Balance'].item()
    return balance

def delete_records(bet_id_list):
    df = read_bets()
    df = df[~df.BetId.isin(bet_id_list)]
    write_bets(df)

    balance_df = read_balance()
    balance_df = balance_df[~balance_df.BetId.isin(bet_id_list)]
    write_balance(balance_df)
