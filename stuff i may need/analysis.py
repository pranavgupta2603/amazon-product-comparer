import pandas as pd
from dateutil.parser import parse
from datetime import date, datetime
import csv


def getrate():
    
    df = pd.read_csv('data.csv')
    df_len = len(df)
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
    df.sort_values(by = 'date', inplace = False, ascending = True)
    df.to_csv('data.csv', index=False)

    d0 = parse(min(df['date']))
    d1 = parse(date.today().strftime('%Y-%m-%d'))


    deltaT = abs((d1-d0).days)
    
    print(df['date'])
    print(d0, d1, deltaT)
    print(df_len)
    return df_len, deltaT, (df_len/deltaT)


df_len, deltaT, rate = getrate()

def recordlinks(name, df_len, deltaT, rate, url):
    df = pd.read_csv('datalist.csv')
    to_insert = {
        'product': name,
        'num_reviews': df_len,
        'deltaT': deltaT,
        'rate': rate,
        'url': url
        }
    with open('datalist.csv', 'a') as savefile:
        writer = csv.DictWriter(savefile, fieldnames=["product", 'num_reviews', "deltaT", "rate", "url"])
        writer.writerow(to_insert)
    print("Saved Data!")
