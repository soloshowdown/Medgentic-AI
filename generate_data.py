# generate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def is_festival(date):
    # very simple: treat fixed dates as festival examples (you can expand)
    month_day = (date.month, date.day)
    festivals = {(10,24), (11,4), (3,8), (8,31)}  # example: placeholder dates (Diwali/Holi/Ganesh/others)
    return 1 if month_day in festivals else 0

def generate_days(n_days=900):
    start = datetime.today() - timedelta(days=n_days)
    rows = []
    for i in range(n_days):
        d = start + timedelta(days=i)
        season = (d.month%12)//3  # rough season
        aqi = max(10, int(np.random.normal(80 + 30*season, 40)))  # higher in some seasons
        temp = int(np.random.normal(25 - 2*season, 6))
        viral_cases = max(0,int(np.random.poisson(5 + 0.01*aqi)))
        festival = is_festival(d)
        # hospital load baseline + noise + festival/pollution effects
        baseline = 50 + 0.3*aqi + 20*festival + 0.5*viral_cases + np.random.normal(0,10)
        hospital_load = int(max(5, baseline))
        rows.append({
            "date": d.strftime("%Y-%m-%d"),
            "aqi": aqi,
            "temp": temp,
            "season": season,
            "viral_cases": viral_cases,
            "festival_flag": festival,
            "hospital_load": hospital_load
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = generate_days(900)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/hospital_history.csv", index=False)
    print("Saved data/hospital_history.csv")
