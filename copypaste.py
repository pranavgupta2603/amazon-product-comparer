"""import pyautogui as pg
import streamlit as st
import pyperclip
import pandas as pd"""
"""
temp = ""
prime = True
l = []
#a = st.sidebar.radio("", ["Paste", "Table"])
con = st.button("Confirm")
if con:
    s = pyperclip.paste()
    if s == temp:
        pass
    else:
        temp= s
        st.write(s)
        
#st.session_state["con"] = False"""

# Importing the necessary libraries
import pandas as pd
from IPython.core.display import display, HTML
import streamlit as st
import streamlit.components.v1 as components

# Create a dataframe using pandas library
df = pd.DataFrame([[2768571, 130655, 1155027, 34713051, 331002277],
[1448753, 60632, 790040, 3070447, 212558178],[654405, 9536, 422931, 19852167, 145934619],[605216, 17848, 359891, 8826585, 1379974505],[288477, 9860, 178245, 1699369, 32969875]], columns = ['Total Cases', 'Total Deaths', 'Total Recovered', 'Total Tests', 'Population'])
# Create a list named country to store all the image paths
country = ['https://www.countries-ofthe-world.com/flags-normal/flag-of-United-States-of-America.png','https://www.countries-ofthe-world.com/flags-normal/flag-of-Brazil.png','https://www.countries-ofthe-world.com/flags-normal/flag-of-Russia.png','https://www.countries-ofthe-world.com/flags-normal/flag-of-India.png','https://www.countries-ofthe-world.com/flags-normal/flag-of-Peru.png']
# Assigning the new list as a new column of the dataframe
df['Country'] = country
#components.html("""<a href="https://www.amazon.in/dp/B086CGNG4T?&linkCode=li1&tag=universalcont-21&linkId=0f9247ce452980ac6c0d0fb8920594d3&language=en_IN&ref_=as_li_ss_il" target="_blank"><img border="0" src="//ws-in.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=B086CGNG4T&Format=_SL110_&ID=AsinImage&MarketPlace=IN&ServiceVersion=20070822&WS=1&tag=universalcont-21&language=en_IN" ></a><img src="https://ir-in.amazon-adsystem.com/e/ir?t=universalcont-21&language=en_IN&l=li1&o=31&a=B086CGNG4T" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />""")
# Converting links to html tags
def path_to_image_html(path):
    return '<a href="https://www.amazon.in/dp/B086CGNG4T?&linkCode=li1&tag=universalcont-21&linkId=0f9247ce452980ac6c0d0fb8920594d3&language=en_IN&ref_=as_li_ss_il" target="_blank"><img src="//ws-in.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=B086CGNG4T&Format=_SL110_&ID=AsinImage&MarketPlace=IN&ServiceVersion=20070822&WS=1&tag=universalcont-21&language=en_IN" /></a>'
# Rendering the dataframe as HTML table
st.write((HTML(df.to_html(escape=False, formatters=dict(Country=path_to_image_html)))))
# Rendering the images in the dataframe using the HTML method.
#df.to_html(escape=False,formatters=dict(Country=path_to_image_html))
# Saving the dataframe as a webpage
#df.to_html('webpage.html',escape=False, formatters=dict(Country=path_to_image_html))
#st.write(df)
