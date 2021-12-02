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
from all_funcs import *


def create_table(theurls):
    e = Extractor.from_yaml_file('selectors.yml')
    all_five_star = []
    all_time_diff = []
    all_hun_days = []
    all_rating = []
    all_verified = []
    all_helped = []
    urls_used = []
    product_names = []
    all_reviews = []
    all_amazon_ratings = []
    all_count_of_day = []
    string = ""
    fig = go.Figure()
    prime = False
    today = parse(date.today().strftime("%Y-%m-%d"))
    url_dataframe = pd.DataFrame()
    
    spin = st.empty()
    stat = st.empty()
    print(theurls)
    for i in theurls:
        try:
            asin = find_asin(i)
            print(asin)
            if len(asin) != 10:
                raise ValueError
        except:
            st.error("ASIN NUMBER NOT FOUND IN URL! PLEASE CHECK FORMAT OF URL")
            prime = False
            break
        file_name = asin+'.csv'
        print(file_name)
        try:
            df = s3.get_object(Bucket='productreviewsdata', Key="alldata/"+file_name) 
            body = df["Body"].read().decode('utf-8')
            df_data = pd.read_csv(StringIO(body))
            try:
                title = list(set(df_data["product"]))[0]
                print(list(set(df_data["title"])))
                if list(set(df_data["title"]))[0] == "-":
                    st.error(title + " has 0 reviews. Please remove it from your list and try again!")
                    break
                    
            except IndexError:
                string = string + "https://www.amazon.in/product-reviews/"+asin+"\n"
                break
            stat.info("Getting " + title + "....")
            product_names.append(title)
            try:
                all_amazon_ratings.append(str(list(set(df_data["amazon_rating"]))[0]))
            except:
                all_amazon_ratings.append("-")
            urls_used.append(list(set(df_data["url"]))[0])
            string = string+list(set(df_data["url"]))[0]+"\n"
            #st.write(df_data)
            if len(df_data)==0:
                pass
                    #string = string + "https://www.amazon.in/product-reviews/"+asin+"\n"
                    #st.write(string)
            else:
                fig = create_graph(fig, df_data)
                df_len, deltaT, rate, ind_time_diff, ind_rating, ind_verified, ind_helped, count_of_day, count_of_five_star, ind_hun_days = getrate(df_data)
                #print(df_len)
                all_reviews.append(str(df_len))
                all_time_diff.append(ind_time_diff)
                all_rating.append(ind_rating)
                all_verified.append(ind_verified)
                all_helped.append(ind_helped)
                all_count_of_day.append(count_of_day)
                all_five_star.append(count_of_five_star)
                all_hun_days.append(ind_hun_days)
                prime=True
                
        except botocore.exceptions.ClientError:
            st.info("Request sent for " + asin)
            create_df = pd.DataFrame({"title":[], "content": [], 'date':[], "author": [], "rating":[], "product":[], "url":[], "verified":[], "helped": [], "amazon_rating": []})
            bucket = 'productreviewsdata'
            csv_buffer = StringIO()
            create_df.to_csv(csv_buffer, index=False)
            res.Object(bucket, 'alldata/'+asin+'.csv').put(Body=csv_buffer.getvalue())
            string = string + "https://www.amazon.in/product-reviews/"+asin+"\n"
            prime=False
    dataf = pd.DataFrame({'Product': [],
                          'Our Rating': [],
                          'Total Verified Purchases': [],
                          'No. of Verified Purchases in last 100 days':[],
                          'No. of Verified Purchases that have 5 stars in the last 100 days':[],
                          'Amazon Rating': [],
                          'URL': []})
        
    if prime and len(all_time_diff) == len(st.session_state["linksFinal"]):
        fig.update_layout(
            title="Graph of reviews",
            xaxis_title="Date",
            yaxis_title="No. of Reviews",
            legend_title="Products",
            font=dict(
                family="Courier New, monospace",
                color="black"))
        rates = relative_rates(all_time_diff, all_rating, all_verified, all_helped)
        for record in range(0, len(urls_used)):
            #dataf.append([product_names[record], all_reviews[record], rates[record], all_amazon_ratings[record]])
            
            to_insert = {
                        'Product': product_names[record][:70]+"...",
                        'Our Rating': rates[record],
                        'Total Verified Purchases': all_reviews[record],
                        'No. of Verified Purchases in last 100 days': str(all_count_of_day[record]),
                        'No. of Verified Purchases that have 5 stars in the last 100 days': str(all_five_star[record]),
                        'Amazon Rating': all_amazon_ratings[record],
                        'URL': urls_used[record]
                        }
            dataf = dataf.append(to_insert, ignore_index=True)
        dataf = dataf.sort_values(by=['Our Rating'], ascending=False)
        dataf.set_index('Product', inplace=True)
        stat.empty()
        #st.table(dataf.style.format({"Total Reviews": "{:.0f}"}))
        
        st.table(dataf)
        st.plotly_chart(fig)
        #st.dataframe(dataf)
    else:
        stat.empty()
        #reqs_spin.empty()
        spin.info("Your request is being processed...")
        
        time.sleep(10)
    #st.write(string)
    return string

def save_data_in_session(string, prime_session, sessions_here):
    if prime_session ==True:
        s_check = string.split("\n")
        try:
            while True:
                s_check.remove("")
        except ValueError:
            pass
        print("THIS")
        print(s_check)
        if len(s_check) != len(st.session_state.linksFinal):
            pass
        else:
            for ses in sessions_here:
                ses_check = ses.split("\n")
                try:
                    while True:
                        ses_check.remove("")
                except ValueError:
                    pass
                print("ses_check")
                print(ses_check)
                if set(s_check) == set(ses_check):
                    break
            else:
                print("HIIIIIIIIIIIIII")
                string = st.session_state.dataInBucket+",\n"+string
                st.success("Session Saved")
                res.Object('productreviewsdata', 'sessions/'+st.session_state["iden"]).put(Body=string)
    
    else:
        s_check = string.split("\n")
        try:
            while True:
                s_check.remove("")
        except ValueError:
            pass
        if len(s_check) !=len(st.session_state.linksFinal):
            pass
        else:
            st.success("Session Saved")
            res.Object('productreviewsdata', 'sessions/'+st.session_state["iden"]).put(Body=string)
    
    
    
