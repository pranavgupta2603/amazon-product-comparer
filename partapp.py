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
from bokeh.models.widgets import Button, Div
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.io import show

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
    count_of_day = 0
    count_of_five_star = 0
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
    for l in range(0, len(st.session_state.final)):
        col1, col2= st.columns([2, 0.5])
        exp = col1.expander(st.session_state.final[l].split("/ref")[0])
        col2.button("X", key=str(l))
        ASIN = find_asin(st.session_state.final[l])
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
                ASIN = find_asin(st.session_state.final[n])
                the_link = """https://ws-in.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=IN&source=ss&ref=as_ss_li_til&ad_type=product_link&tracking_id=universalcont-21&language=en_IN&marketplace=amazon&region=IN&placement="""+ASIN+"""&asins="""+ASIN+"""&show_border=true&link_opens_in_new_window=true"""
                components.iframe(the_link, height=240, width=120)
                st.button("X", key=str(n))
            except:
                 pass
# In[42]:

urls = open('urls5.txt', 'r')
e = Extractor.from_yaml_file('selectors.yml')
price_e = Extractor.from_yaml_file('details.yml')
datalist = pd.read_csv('datalist.csv')
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
prime = True
today = parse(date.today().strftime("%Y-%m-%d"))
st.set_page_config(
     page_title="Product Reviews Comparer",
     layout="wide")
#a = st.sidebar.button("poop")
st.markdown("""
<style>
#MainMenu{visibility: hidden;} 
td.css-57lzw8:nth-of-type(4){}
footer, label.css-zyb2jl, img.css-1jhkrss, button.css-bl767a {visibility: hidden;}
.copy-button{color:red;}

</style>

""", unsafe_allow_html=True)
#button.css-19deh3e, button.css-6163i7, button.css-14n4bfl{visibility: hidden; cursor: none;}
#st.write(st.session_state)

if "w" not in st.session_state:
    st.session_state["w"] = []

if "a" not in st.session_state:
    st.session_state["a"] = []
if "final" not in st.session_state:
    st.session_state["final"] = []
if "chosen" not in st.session_state:
    st.session_state.chosen = ""
#st.markdown("<hr>", unsafe_allow_html=True)

#lay1, lay2 = st.columns(2)

#enter_it, lol2, create_it = st.sidebar.columns(3)
st.sidebar.text("Unique ID:")
enter_it = st.sidebar.container()
lol2 = st.sidebar.container()
create_it = st.sidebar.container()
#st.sidebar.markdown("""<hr>""", unsafe_allow_html=True)
enter_uni_id = lol2.text_input("Enter Unique ID:")
lol2.write("OR")
with enter_it:
    id_place = st.empty()
if "iden" not in st.session_state:
    st.session_state["create_it"] = 0
else:
    id_place.code(st.session_state["iden"].replace(".txt", ""))
if "create_it" in st.session_state:
    enter_it.warning("Keep Session ID to access and save your comparisons.")
with lol2:
    thing = st.button("Create Session ID")
    if thing:
        if st.session_state["create_it"] !=0:
            id_place.code(st.session_state["iden"].replace(".txt", ""))
            #id_place.code(st.session_state["iden"].replace(".txt", ""))
            prime_session=False
        else:
            iden = str(uuid.uuid4())
            st.session_state["iden"] = iden + ".txt"
            id_place.code(iden)
            st.session_state["create_it"] = 1
            prime_session = False

if enter_uni_id == "":
    #st.session_state["iden"] = ""
    prime_session=False
    st.sidebar.markdown("""<hr>""", unsafe_allow_html=True)
else:
    try:
        
        check_iden = s3.get_object(Bucket="productreviewsdata", Key="sessions/"+enter_uni_id+".txt")
        already_in_body = check_iden["Body"].read().decode()
        sessions_here = already_in_body.split(",")
        #print(sessions_here)
        #sessions_here.insert(0, "")
        a = []
        indices = [("Comparison "+ str(num)) for num in range(1, len(sessions_here)+1)]
        #indices.insert(0, "Custom")
        create_it.markdown("""<hr>""", unsafe_allow_html=True)
        with create_it:
            
            chosen = st.selectbox("Choose Session:", indices)
            
            print("___________")
            a = list(set(sessions_here[indices.index(chosen)].split("\n")))
            a.remove("")
            if st.session_state["refresh"] == True:
                st.session_state.final = []
            if chosen != st.session_state.chosen:
                st.session_state.chosen = chosen
                st.session_state["a"] = a
                st.session_state["final"] = a
            else:
                pass
 
        #st.markdown("""<a href="https://www.amazon.in/B00ECWG1NC?ie=UTF8&linkCode=li2&tag=universalcont-21&linkId=d788ae6814662c185b958016f068888b&language=en_IN&ref_=as_li_ss_il" target="_blank"><img border="0" src="//ws-in.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=B00ECWG1NC&Format=_SL160_&ID=AsinImage&MarketPlace=IN&ServiceVersion=20070822&WS=1&tag=universalcont-21&language=en_IN" ></a><img src="https://ir-in.amazon-adsystem.com/e/ir?t=universalcont-21&language=en_IN&l=li2&o=31&a=B07MGQS2M8" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />""", unsafe_allow_html=True)
            #st.text(sessions_here[chosen-1])
        #for j in range(0, len(sessions_here)):
         #   st.text("Session "+ str(j+1)+": ")
          #  st.text(sessions_here[j])
        prime_session=True
        iden = enter_uni_id.replace(".txt", "")
        st.session_state["iden"] = iden+".txt"
        id_place.code(iden)
        st.sidebar.markdown("""<hr>""", unsafe_allow_html=True)

    except:
        lol2.error("Unique ID not found. Create a new table to create one.")
        prime_session=False
        
#st.markdown("<hr>", unsafe_allow_html=True)


#place = st.sidebar.empty()
"""components.html(
<input type="text" id="copy-text-input" placeholder="Enter text to be copied">
    <button id="poop">
        Copy Text
    </button>
<p id="he"></p>
<script>
let copyButton = document.getElementById('poop');
  copyButton.addEventListener('click', function () {
      navigator.clipboard
          .readText()
          .then(
              cliptext =>
              
                  (document.getElementById("he").innerText = cliptext),
                  err => console.log(err)
          );
  });
</script>
)"""
if len(st.session_state) > 1:
    for k in st.session_state:
        if st.session_state[k] == True and k.isdigit():
            st.session_state["final"].pop(int(k))
            
st.session_state["temp_copy"] = ""

#https://www.amazon.in/Bangalore-Refinery-999-9-Yellow-Gold/dp/B01HVB3PSY?ref_=Oct_DLandingS_D_9dee8709_60&smid=A2VFUGD63K4X10
"""con = push1.button("Push to Paste")
if con:
    s = pyperclip.paste()
    if s == st.session_state["temp_copy"]:
        pass
    else:
        st.session_state["temp_copy"]= s
        try:
            check_paste = requests.get(s)
            if s in st.session_state["final"]:
                pass
            else:
                
                st.session_state["final"].append(s)
                
        except:
            st.error('Not a valid URL')"""
#st.sidebar.markdown("<hr>", unsafe_allow_html = True)
#col, col_an = st.columns([1, 0.365])
with st.sidebar.form(key='my_form'):
    placeholder = st.empty()
    s = placeholder.text_input(label='Enter URL')
    submit = st.form_submit_button(label='Submit')
            
            
if submit:
    try:
        check_paste = requests.get(s)
        if s in st.session_state["final"] or s.find("amazon.in") == -1:
            pass
        else:
            st.session_state["final"].append(s)
        
    except:
        st.error('Not a valid URL')
            
conf1, refre1 = st.sidebar.columns([1, 1])
print(st.session_state.final)

confirm = conf1.button("Compare")
refresh = refre1.button("Refresh List", key="refresh")
if refresh:
    st.session_state.final = []
#list_down()
all_the_asin = []
if len(st.session_state.final) == 0:
        pass
else: 
    exp=st.expander("Expand")
    with exp:
        create_vars(st.columns(len(st.session_state.final)))
if confirm and len(st.session_state.final)> 1:
    #print(st.session_state["w"])
    if "iden" not in st.session_state:
        iden = str(uuid.uuid4()) 
        st.session_state["iden"] = iden+ ".txt"
        id_place.code(iden)
        prime_session = False
        
    theurls = st.session_state["final"]
    with st.spinner('Creating Table...'):
        id_place.code(st.session_state["iden"].replace(".txt", ""))
        stat = st.empty()
        
        for i in theurls:
            
            clear_none()
            try:
                asin = find_asin(i)
                if len(asin) != 10:
                    raise ValueError
            except:
                st.write("ASIN NUMBER NOT FOUND IN URL!")
                prime = False
                break
            
            file_name = asin+'.csv'
            print(i)
            try:
                df = s3.get_object(Bucket='productreviewsdata', Key="alldata/"+file_name)
                last = parse(df["LastModified"].strftime("%Y-%m-%d"))
                diff = (today-last).days
                
                if diff > 5:
                    res.Object('productreviewsdata', "alldata/"+file_name).delete()
                    s3.get_object(Bucket='productreviewsdata', Key="alldata/"+file_name) #causes an error
                else:
                    
                    body = df["Body"].read().decode('utf-8')
                    df_data = pd.read_csv(StringIO(body))
                    try:
                        title = list(set(df_data["product"]))[0]
                    except IndexError:
                        print(df_data)
                        break
                    #data = scrape(i, e)
                    #while data["product_title"] == None or data["reviews"] == None:
                    #    data = scrape(i, e)
                    stat.info("Getting " + title + "....")
                    product_names.append(title)
                    #data["product_link"] = "https://www.amazon.in"+data["product_link"]
                    #price, amazon_rating = get_details(data["product_link"])
                    #all_amazon_ratings.append(amazon_rating)
                    try:
                        
                        all_amazon_ratings.append(str(list(set(df_data["amazon_rating"]))[0]))
                    except:
                        all_amazon_ratings.append("-")

                    urls_used.append(list(set(df_data["url"]))[0])
                    string = string+list(set(df_data["url"]))[0]+"\n"
                    #review_len = get_total_reviews(data)
                    #st.write(data["product_title"], price)
                    #print(review_len)
                    #print(df_data)
                    #print(len(df_data))
                    if len(df_data)==0:
                        pass
                    else:
                        df_len, deltaT, rate, ind_time_diff, ind_rating, ind_verified, ind_helped, count_of_day, count_of_five_star, ind_hun_days = getrate(df_data)
                        print(df_len)
                        all_reviews.append(str(df_len))
                        all_time_diff.append(ind_time_diff)
                        print(ind_time_diff)
                        all_rating.append(ind_rating)
                        all_verified.append(ind_verified)
                        all_helped.append(ind_helped)
                        all_count_of_day.append(count_of_day)
                        all_five_star.append(count_of_five_star)
                        all_hun_days.append(ind_hun_days)
                    
            except botocore.exceptions.ClientError:
                st.info("Request sent for " + asin)
                create_df = pd.DataFrame({"title":[], "content": [], 'date':[], "author": [], "rating":[], "product":[], "url":[], "verified":[], "helped": [], "amazon_rating": []})
                bucket = 'productreviewsdata'
                csv_buffer = StringIO()
                create_df.to_csv(csv_buffer, index=False)
                res.Object(bucket, 'alldata/'+asin+'.csv').put(Body=csv_buffer.getvalue())
                string = string + "https://www.amazon.in/product-reviews/"+asin+"\n"
                prime=False
        if prime_session ==True:
            s_check = string.split("\n")
            try:
                while True:
                    s_check.remove("")
            except ValueError:
                pass
                
            print("s_check")
            print(s_check)
            if len(s_check) != len(st.session_state.final):
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
                    string = already_in_body+",\n"+string
                    res.Object('productreviewsdata', 'sessions/'+st.session_state["iden"]).put(Body=string)
        
        else:
            s_check = string.split("\n")
            try:
                while True:
                    s_check.remove("")
            except ValueError:
                pass
            if len(s_check) !=len(st.session_state.final):
                pass
            else:
                res.Object('productreviewsdata', 'sessions/'+st.session_state["iden"]).put(Body=string)
                    
        """       
            if string not in sessions_here:
                string = already_in_body+",\n"+string
                res.Object('productreviewsdata', 'sessions/'+st.session_state["iden"]).put(Body=string)
        else:
            res.Object('productreviewsdata', 'sessions/'+st.session_state["iden"]).put(Body=string)
            """
        dataf = pd.DataFrame({'Product': [], 'Our Rating': [], 'Total Reviews': [], 'No. of Reviews less than 100 days':[], 'No. of Reviews less than 100 days given 5 Stars':[],'Amazon Given Rating': [], 'URL': []})
    
        if prime and len(all_time_diff) == len(st.session_state["final"]):
            
            rates = relative_rates(all_time_diff, all_rating, all_verified, all_helped)
            for record in range(0, len(urls_used)):
                #dataf.append([product_names[record], all_reviews[record], rates[record], all_amazon_ratings[record]])
                
                to_insert = {
                            'Product': product_names[record][:70]+"...",
                            'Our Rating': rates[record],
                            'Total Reviews': all_reviews[record],
                            'No. of Reviews less than 100 days': str(all_count_of_day[record]),
                            'No. of Reviews less than 100 days given 5 Stars': str(all_five_star[record]),
                            'Amazon Given Rating': all_amazon_ratings[record],
                            'URL': urls_used[record]
                            }
                dataf = dataf.append(to_insert, ignore_index=True)
            dataf = dataf.sort_values(by=['Our Rating'], ascending=False)
            dataf.set_index('Product', inplace=True)
            stat.empty()
            #st.table(dataf.style.format({"Total Reviews": "{:.0f}"}))
            st.table(dataf)
            #st.dataframe(dataf)
        else:
            stat.empty()
            st.info("Your request is being processed...")
            
                    
        
