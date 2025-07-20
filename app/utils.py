import datetime
import numpy as np
from app.data_persistence import read_balance

def process_odds(odds):
    odds = odds.replace(' ', '')
    sign = None
    for char in odds:
        if char in ('+', '-'):
            sign = char
            break
    if not sign:
        raise ValueError("Invalid odds format")
    num = float(odds.replace(sign, ''))
    return sign, num

def get_current_balance():
    df = read_balance()
    if df.empty:
        return 0.0
    max_id = df.BalanceId.max()
    balance = df.loc[df.BalanceId == max_id, 'Balance'].item()
    return balance

def get_date(date_str):
    if date_str.lower() == 't':
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    return date

def process_results(s):
    r = s.upper()
    if r not in ['W', 'L', 'P']:
        r = np.nan
    return r

def pct(your_number, num_digits=2):
    s = "{:.num_digits%}"
    s = s.replace('num_digits', str(num_digits))
    return s.format(your_number)
