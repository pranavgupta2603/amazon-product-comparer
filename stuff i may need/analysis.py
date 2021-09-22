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
with push1:
    copy_button = Button(label="Paste Product URL", sizing_mode="stretch_both",button_type="default", margin=[0, 0, 0, 0], css_classes=["copy-button"])
    copy_button.js_on_event("button_click", CustomJS(code="""
        #navigator.clipboard.readText().then(text => document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: text})))"""))
    st.markdown("<style>.copy-button{font-size: 20px;}</style>", unsafe_allow_html=True)
    print(copy_button)
    result = streamlit_bokeh_events(
        copy_button,
        events="GET_TEXT",
        key="get_text",
        override_height=40,
        refresh_on_update=False,
        debounce_time=0)

if result:
    if "GET_TEXT" in result:
        s = result.get("GET_TEXT")
        try:
            check_paste = requests.get(s)
            if s in st.session_state["final"] or s.find("amazon.in") == -1:
                pass
            else:
                st.session_state["final"].append(s)
        
        except:
            st.error('Not a valid URL')
