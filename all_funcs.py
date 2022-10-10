import validators
from selectorlib import Extractor
import requests 
import json 
import time
import csv
from dateutil.parser import parse
import sys, os
import re
from datetime import date, datetime
import numpy as np
import math
import concurrent.futures
import boto3
import botocore 
from io import StringIO
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import base64
import uuid
#import pyperclip
#from IPython.core.display import HTML
from bokeh.plotting import figure
import plotly.express as px
import plotly.graph_objects as go


# In[2]:


AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

s3 = boto3.client("s3", 
                  region_name='ap-south-1', 
                  aws_access_key_id=AWS_ACCESS_KEY_ID, 
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

res = boto3.resource("s3",
                     region_name='ap-south-1',
                     aws_access_key_id=AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
def getrate(df):
    ind_time_diff = []
    ind_rating = []
    ind_helped = []
    count_of_day = 0
    count_of_five_star = 0
    
    #print(min(df['date']))
    
    df['date'] = pd.to_datetime(df.date, infer_datetime_format = True)
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
    df.sort_values(by = 'date', inplace = True, ascending=True)
    #df.to_csv('data.csv', index=False)
    df = df.query('verified == 1')
    df_len = len(df)
    d0 = parse(min(df['date']))
    d1 = parse(max(df['date']))
    today = parse(date.today().strftime("%Y-%m-%d"))
    for i in df["date"].values:
        ind_time_diff.append((today-parse(i)).days)
    for i in ind_time_diff:
        if i <=100:
            count_of_day+=1
    #print(count_of_day)
    ind_hun_days = ind_time_diff[len(ind_time_diff)-count_of_day:]
    for i in range(0, len(df['rating'].values)):
        if df['rating'].values[i] == None or df['rating'].values[i] == "" or df['rating'].values[i] == "None":
            ind_rating.append(0)
        else:  
            ind_rating.append(float(df['rating'].values[i])/5)
    ind_rating_count_of_day = [i*5 for i in ind_rating[len(ind_time_diff)-count_of_day:]]
    for i in ind_rating_count_of_day:
        if i == 5:
            count_of_five_star += 1
    ind_verified = df['verified'].values
    for i in range(0, len(df['helped'].values)):
        if df['helped'].values[i] == None:
            ind_helped.append(1)
        else:
            if str(df['helped'].values[i]).isdigit() == True:
                ind_helped.append(int(df['helped'].values[i]) + 1)
            else:
                df['helped'].values[i] = df['helped'].values[i].split(",")
                df['helped'].values[i] = "".join(df['helped'].values[i])
                ind_helped.append(int(df['helped'].values[i]) + 1)
        
    deltaT = abs((d1-d0).days)
    if deltaT == 0:
        deltaT = 1
    #print(deltaT)
    rate = (df_len/deltaT)
    #revenue = rate * int(p[1])
    #print(df_len)
    """print(df['date'])
    print(d0, d1, deltaT)
    print(int(p[1]))
    print(revenue)"""

    return df_len, deltaT, rate, ind_time_diff, ind_rating, ind_verified, ind_helped, count_of_day, count_of_five_star, ind_hun_days
#p = ["", "1"]
#df_len, deltaT, rate, revenue = getrate(p)


# In[4]:


def recordlinks(name, df_len, deltaT, rate, url):
    to_insert = {
        'product': name,
        'num_reviews': df_len,
        'deltaT': deltaT,
        'rate': rate,
        'url': url,
        }
    df = pd.read_csv('datalist.csv')
    with open('datalist.csv', 'a', newline="") as savefile:
        writer = csv.DictWriter(savefile, fieldnames=["product", 'num_reviews', "deltaT", "rate", "url"])
        writer.writerow(to_insert)
    print("Saved Data!")


# In[5]:


def scrape(url, e):    
    headers = {
        'authority': 'www.amazon.in',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US,en-IN;q=0.9,en;q=0.8',
    }

    r = requests.get(url, headers=headers)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies %d\n"%(url, r.status_code))
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    #print(e.extract(r.text)["product_title"])
    return e.extract(r.text)


# In[6]:


def finding_data(data, url):
    
    if data:
        for r in data['reviews']:
            if r["title"] == None:
                r["title"] = "None"
            r["product"] = data["product_title"]
            r['url'] = url
            try:
                r['rating'] = r['rating'].split(' out of')[0]
            except:
                r['rating'] = "None"
            
            date_posted = r['date'].split('on ')[-1]
            r['date'] = parse(date_posted).strftime('%m-%d-%Y')
            if r['helped'] != None:
                r['helped'] = r['helped'].split(" ")[0]
                if r['helped'] == "One":
                    r['helped'] = "1"
            else:
                r['helped'] = 0
            if r['verified'] != None:
                r['verified'] = r['verified'].split(" ")[0]
                if r['verified'] == "Verified":
                    r['verified'] = "1"
            else:
                r['verified'] = "0"
            
                
        
    #print(data)
    return data
            
# In[7]:

# In[8]:


def get_nextpage(data):
    return "https://www.amazon.in"+data["next_page"]


# In[9]:


def clear_none():
    #df = pd.read_csv('datalist.csv')
    #df.dropna(axis="rows", how="any", inplace = True)
    #df.to_csv('datalist.csv', index=False)
    with open('data.csv', 'w+', encoding="utf-8", errors="ignore") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["title","content","date", "author","rating","product","url", "verified", "helped"])
        writer.writeheader()
    outfile.close()
#clear_none()


# In[27]:


def get_details(link):
    weight = 0
    count = 0
    details = scrape(link, price_e)
    while details['amazon_given_rating'] == None and count < 15:
        details = scrape(link, price_e)
        print("count: " + str(count))
        count += 1

    if details["price"] == None:
        details["price"] = ["", "1"]
    else:
        if "x" in details["price"]:
            details["price"] = details["price"].split("\xa0")
            details["price"][1] = details["price"][1].split(",")
            details["price"][1] = ["".join(details["price"][1])]
            details["price"][1] = details["price"][1][0].split(".")[0]
        else:
            details["price"] = list(details["price"])
            details["price"].pop(0)
            details["price"] = "".join(details["price"])
            #print(details["price"])
    
    if details["amazon_given_rating"] == None:
        amazon_rating = "-"
    else:
        amazon_rating = details["amazon_given_rating"].split(" out")[0]
        
    if (details['info'] == None) and (details['info2'] != None):
        details['info'] = details['info2']
        details['info2'] = None
        
    if details['info'] != None:
        info = details['info']
        #weight = info.split("Weight ")[1][0]
    print(amazon_rating)
    print(details)

    
    
        
    
    return details["price"], amazon_rating


# In[28]:


def relative_rates(timediff, allrating, allverified, all_helped):
    sum_list = []
    temp_arr = []
    for i in range(0, len(all_helped)):
        temp_arr.append(max(all_helped[i]))
    norm_fact = max(temp_arr)
    #print(temp_arr)
    
    for i in range(0, len(timediff)):
        for j in range(0, len(timediff[i])):
            if int(allverified[i][j]) != 1:
                timediff[i][j] = round((np.exp(-(timediff[i][j]**(1/4))) * allrating[i][j] * (all_helped[i][j]/norm_fact) * 0.1), 5)
            else:
                timediff[i][j] = round((np.exp(-(timediff[i][j]**(1/4))) * allrating[i][j] * (all_helped[i][j]/norm_fact)), 5)
    for i in range(0, len(timediff)):
        sum_list.append(round(sum(timediff[i]), 5))
    return sum_list


# In[29]:

# In[30]:


def find_all_links(link, num):
    link = link.split("?")
    all_links = []
    num_pages = math.ceil(int(num)/10)
    for page in range(0, num_pages):
        link[1] = "pageNumber=" + str(page+1)
        temp_data = {"next_page": "?".join(link)}
        finallink = get_nextpage(temp_data)
        all_links.append(finallink)
    return all_links
        


# In[31]:


def upload(res, asin, file_name):
    file_name = asin + ".csv"
    bucket = "productreviewsdata"
    res.Bucket(bucket).upload_file("data.csv", "alldata/"+file_name)


# In[32]:


def find_asin(link):
    link = link.split("/")
    for i in range(0, len(link)):
        if link[i] == "product-reviews":
            asin = link[i+1]
        if link[i] == "dp":
            asin=link[i+1][0:10]
        if link[i] == "product":
            asin=link[i+1][0:10]
    return asin


# In[33]:


def get_total_reviews(data):
    data['total_reviews'] = data['total_reviews'].split("| ")
    data['total_reviews'] = data['total_reviews'][1].split(" ")[0].split(",")
    data["total_reviews"] = int(''.join(data["total_reviews"]))
    return data["total_reviews"]

def myFunc(e):
    return e["Our Rating"]
def list_down():
    all_the_asin = []
    for l in range(0, len(st.session_state.linksFinal)):
        col1, col2= st.columns([2, 0.5])
        exp = col1.expander(st.session_state.linksFinal[l].split("/ref")[0])
        col2.button("X", key=str(l))
        ASIN = find_asin(st.session_state.linksFinal[l])
        all_the_asin.append(ASIN)
        the_link = """https://ws-in.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=IN&source=ss&ref=as_ss_li_til&ad_type=product_link&tracking_id=universalcont-21&language=en_IN&marketplace=amazon&region=IN&placement="""+ASIN+"""&asins="""+ASIN+"""&show_border=true&link_opens_in_new_window=true"""
        with exp:
            components.iframe(the_link, height=240, width=120)
    
    
          
    #print(globals()["col"])
    #print(globals()["col_an"])
    #for n, val in enumerate(st.session_state["final"]):
     #   globals()["var%d"%n] = val

def create_vars(func_col):
    for n, val in enumerate(func_col):
        globals()["var%d"%n] = val
    for n in range(0, len(func_col)):
        with globals()["var"+str(n)]:
            try:
                ASIN = find_asin(st.session_state.linksFinal[n])
                the_link = """https://ws-in.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=IN&source=ss&ref=as_ss_li_til&ad_type=product_link&tracking_id=universalcont-21&language=en_IN&marketplace=amazon&region=IN&placement="""+ASIN+"""&asins="""+ASIN+"""&show_border=true&link_opens_in_new_window=true"""
                components.iframe(the_link, height=240, width=120)
                st.button("X", key=str(n))
            except Exception as e:
                 st.write(e)
def create_graph(fig, df):
    df['date'] = pd.to_datetime(df.date, infer_datetime_format = True)
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
    df.sort_values(by = 'date', inplace = True, ascending=True)
    y_data = [i+1 for i in range(0, len(df))]
    fig.add_trace(go.Scatter(x=df["date"], y=y_data, name=list(set(df["product"]))[0][0:20]+"..."))
    return fig
