#!/usr/bin/env python
# coding: utf-8

# In[1]:

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



# In[2]:


AWS_ACCESS_KEY_ID = 'AKIA4QZRAFHSF3EZPL73'
AWS_SECRET_ACCESS_KEY = '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'

s3 = boto3.client("s3", 
                  region_name='ap-south-1', 
                  aws_access_key_id=AWS_ACCESS_KEY_ID, 
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

res = boto3.resource("s3",
                     region_name='ap-south-1',
                     aws_access_key_id=AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


# In[3]:


def getrate(df):
    ind_time_diff = []
    ind_rating = []
    ind_helped = []
    
    df_len = len(df)
    #print(min(df['date']))
    
    df['date'] = pd.to_datetime(df.date, infer_datetime_format = True)
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
    df.sort_values(by = 'date', inplace = True, ascending=True)
    df.to_csv('data.csv', index=False)

    d0 = parse(min(df['date']))
    d1 = parse(max(df['date']))
    today = parse(date.today().strftime("%Y-%m-%d"))
    for i in df["date"].values:
        ind_time_diff.append((today-parse(i)).days)
    #print(ind_time_diff) 
    for i in range(0, len(df['rating'].values)):
        if df['rating'].values[i] == None or df['rating'].values[i] == "" or df['rating'].values[i] == "None":
            ind_rating.append(0)
        else:  
            ind_rating.append(int(float(df['rating'].values[i])/5))
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
    rate = (df_len/deltaT)
    #revenue = rate * int(p[1])
    #print(df_len)
    """print(df['date'])
    print(d0, d1, deltaT)
    print(int(p[1]))
    print(revenue)"""
    return df_len, deltaT, rate, ind_time_diff, ind_rating, ind_verified, ind_helped
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
    df = pd.read_csv('datalist.csv')
    df.dropna(axis="rows", how="any", inplace = True)
    df.to_csv('datalist.csv', index=False)
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
    while details['amazon_given_rating'] == None and count < 100:
        details = scrape(link, price_e)
        #print("count: " + str(count))
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
    print(temp_arr)
    
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
    
    return asin


# In[33]:


def get_total_reviews(data):
    data['total_reviews'] = data['total_reviews'].split("| ")
    data['total_reviews'] = data['total_reviews'][1].split(" ")[0].split(",")
    data["total_reviews"] = int(''.join(data["total_reviews"]))
    return data["total_reviews"]

def myFunc(e):
    return e["Our Rating"]


# In[42]:


urls = open('urls5.txt', 'r')
e = Extractor.from_yaml_file('selectors.yml')
price_e = Extractor.from_yaml_file('details.yml')
datalist = pd.read_csv('datalist.csv')
all_time_diff = []
all_rating = []
all_verified = []
all_helped = []
urls_used = []
product_names = []
all_reviews = []
all_amazon_ratings = []
string = ""
prime = True
today = parse(date.today().strftime("%Y-%m-%d"))

refresh = st.button("Refresh")

if refresh:
    st.session_state["w"] = []
place = st.empty()

if "w" not in st.session_state:
    st.session_state["w"] = []
    
if len(st.session_state) > 1:
    for k in st.session_state:
        if st.session_state[k] == True:
            st.session_state.w.pop(int(k))
            
ask= place.text_input("Enter", value="")
if ask == "" or ask in st.session_state["w"]:
    pass
else:
    try:
        check = requests.get(ask)
        st.session_state["w"].append(ask)

    except:
        st.error('Not a valid URL')

for l in range(0, len(st.session_state.w)):
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.text(st.session_state.w[l])
        col2.button("X", key=str(l))
#st.write(st.session_state)


confirm = st.button("Create Table?")
if confirm and len(st.session_state.w)> 1:
    theurls = st.session_state["w"]
    with st.spinner('Creating Table...'):
        stat = st.empty()
        for i in theurls:
            string = string+i+"\n"
            clear_none()
            try:
                asin = find_asin(i)
            except:
                st.write("ASIN NUMBER NOT FOUND!")
                prime = False
                break
            
            file_name = asin+'.csv'
            print(i)
            try:
                df = s3.get_object(Bucket='productreviewsdata', Key="alldata/"+file_name)
                last = parse(df["LastModified"].strftime("%Y-%m-%d"))
                diff = (today-last).days
                print(diff)
                
                if diff > 3:
                    res.Object('productreviewsdata', "alldata/"+file_name).delete()
                    s3.get_object(Bucket='productreviewsdata', Key="alldata/"+file_name) #causes an error
                else:
                    
                    
                    body = df["Body"].read().decode('utf-8')
                    df_data = pd.read_csv(StringIO(body))
                    data = scrape(i, e)
                    while data["product_title"] == None or data["reviews"] == None:
                        data = scrape(i, e)
                    stat.info("Getting " + data["product_title"] + "....")
                    product_names.append(data["product_title"])
                    data["product_link"] = "https://www.amazon.in"+data["product_link"]
                    price, amazon_rating = get_details(data["product_link"])
                    all_amazon_ratings.append(amazon_rating)
                    urls_used.append(i)
                    review_len = get_total_reviews(data)
                    #st.write(data["product_title"], price)
                    
                    
                    #print(df_data)
                    df_len, deltaT, rate, ind_time_diff, ind_rating, ind_verified, ind_helped = getrate(df_data)
                    print(df_len)
                    all_reviews.append(df_len)
                    all_time_diff.append(ind_time_diff)
                    print(ind_time_diff)
                    all_rating.append(ind_rating)
                    all_verified.append(ind_verified)
                    all_helped.append(ind_helped)
                
            except botocore.exceptions.ClientError as err:
                if err.response['Error']['Code'] == "NoSuchKey":
                    data = scrape(i, e)
                    while data["product_title"] == None or data["reviews"] == None:
                        data = scrape(i, e)
                    stat.info("Scraping "+ data["product_title"]+"....")
                    product_names.append(data["product_title"])
                    data["product_link"] = "https://www.amazon.in"+data["product_link"]
                    price, amazon_rating = get_details(data["product_link"])
                    all_amazon_ratings.append(amazon_rating)
                    urls_used.append(i)
                    review_len = get_total_reviews(data)
                    
                    #st.write(data["product_title"], price)
                    if data["next_page"] == None:
                        all_links = []
                        all_links.append(i)
                    else:
                        all_links = find_all_links(data["next_page"], review_len)

                    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                        results = {executor.submit(scrape, link, e): link for link in all_links}
                        for result in concurrent.futures.as_completed(results):
                            link = results[result]
                            print(link)
                            data = result.result()
                            
                            this_prime=True
                            while this_prime:
                                if data["product_title"] == None:
                                    data = scrape(link, e)
                                else:
                                    this_prime=False
 
                            if data["reviews"] == None:
                                pass
                            else:
                                data = finding_data(data, i)
                                df_data = pd.read_csv('data.csv')
                                for r in data["reviews"]:
                                    df_data = df_data.append(r, ignore_index = True)
                                df_data.to_csv('data.csv', index = False)
                    upload(res, asin, file_name)
                    df_data = pd.read_csv('data.csv')
                    df_len, deltaT, rate, ind_time_diff, ind_rating, ind_verified, ind_helped = getrate(df_data)
                    print(df_len)
                    all_reviews.append(df_len)
                    all_time_diff.append(ind_time_diff)
                    all_rating.append(ind_rating)
                    all_verified.append(ind_verified)
                    all_helped.append(ind_helped)
                    prime=True
        #prime=True
        iden = str(uuid.uuid4()) + ".txt"
        res.Object('productreviewsdata', 'sessions/'+iden).put(Body=string)
        dataf = pd.DataFrame({'Product': [], 'Our Rating': [], 'Total Reviews': [], 'Amazon Given Rating': [], 'URL': []})
        if prime:
            rates = relative_rates(all_time_diff, all_rating, all_verified, all_helped)
            for record in range(0, len(urls_used)):
                #dataf.append([product_names[record], all_reviews[record], rates[record], all_amazon_ratings[record]])
                
                to_insert = {
                            'Product': product_names[record],
                            'Our Rating': rates[record],
                            'Total Reviews': all_reviews[record],
                            'Amazon Given Rating': all_amazon_ratings[record],
                            'URL': urls_used[record]
                            }
                print(to_insert)
                dataf = dataf.append(to_insert, ignore_index=True)
            dataf = dataf.sort_values(by=['Our Rating'], ascending=False)
            dataf.set_index('Product', inplace=True)
            stat.empty()
            st.table(dataf.style.format({"Total Reviews": "{:.0f}"}))
            st.dataframe(dataf)
        else:
            print("Thanks for stopping by!!")
        
            

                #print(data)



