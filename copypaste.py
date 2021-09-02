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


components.html("""


<table class="css-1vbb94r edw49t11"><thead><tr><th class="blank css-8tih0y edw49t13">&nbsp;</th><th scope="col" class="col_heading level0 col0 css-8tih0y edw49t13">Our Rating</th><th scope="col" class="col_heading level0 col1 css-8tih0y edw49t13">Total Reviews</th><th scope="col" class="col_heading level0 col2 css-8tih0y edw49t13">No. of Reviews less than 100 days</th><th scope="col" class="col_heading level0 col3 css-8tih0y edw49t13">No. of Reviews less than 100 days given 5 Stars</th><th scope="col" class="col_heading level0 col4 css-8tih0y edw49t13">Amazon Given Rating</th><th scope="col" class="col_heading level0 col5 css-8tih0y edw49t13">URL</th></tr></thead><tbody><tr><th scope="row" class="row_heading level0 row0 css-8tih0y edw49t13">OnePlus Buds Z (White)</th><td class="css-57lzw8 edw49t12">0.0851</td><td class="css-57lzw8 edw49t12">5000</td><td class="css-57lzw8 edw49t12">1968</td><td class="css-57lzw8 edw49t12">697</td><td class="css-57lzw8 edw49t12">4.2</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B07XY541GH</td></tr><tr><th scope="row" class="row_heading level0 row1 css-8tih0y edw49t13">Noise Air Buds Truly Wireless Earbuds with Mic for Crystal Clear Calls, HD Sound, Smart Touch and 20 Hour Playtime - ICY White</th><td class="css-57lzw8 edw49t12">0.0752</td><td class="css-57lzw8 edw49t12">5000</td><td class="css-57lzw8 edw49t12">2699</td><td class="css-57lzw8 edw49t12">913</td><td class="css-57lzw8 edw49t12">3.7</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B08H8Q5KLK</td></tr><tr><th scope="row" class="row_heading level0 row2 css-8tih0y edw49t13">Mivi DuoPods A25 True Wireless Earbuds Made in India. Bluetooth Wireless Ear Buds with 30Hours Battery, Immersive Sound Quality, Powerful Bass, Touch Control - Black</th><td class="css-57lzw8 edw49t12">0.0595</td><td class="css-57lzw8 edw49t12">2790</td><td class="css-57lzw8 edw49t12">2595</td><td class="css-57lzw8 edw49t12">1212</td><td class="css-57lzw8 edw49t12">3.6</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B08ZYPBSSH</td></tr><tr><th scope="row" class="row_heading level0 row3 css-8tih0y edw49t13">Boult Audio AirBass TrueBuds True Wireless Earbuds with 30 Hours Total Playtime &amp; Deep Bass, Type-C Fast Charging, Touch Controls, IPX7 Fully Waterproof, Noise Isolation and Voice Assistant (Grey)</th><td class="css-57lzw8 edw49t12">0.0270</td><td class="css-57lzw8 edw49t12">3026</td><td class="css-57lzw8 edw49t12">456</td><td class="css-57lzw8 edw49t12">186</td><td class="css-57lzw8 edw49t12">3.8</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B08CFCK6CW</td></tr><tr><th scope="row" class="row_heading level0 row4 css-8tih0y edw49t13">Jabra Elite 65t Alexa Enabled True Wireless Earbuds with Charging Case, 15 Hours Battery,Titanium Black, Designed in Denmark</th><td class="css-57lzw8 edw49t12">0.0237</td><td class="css-57lzw8 edw49t12">3536</td><td class="css-57lzw8 edw49t12">693</td><td class="css-57lzw8 edw49t12">209</td><td class="css-57lzw8 edw49t12">3.9</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B079L9WYP7</td></tr><tr><th scope="row" class="row_heading level0 row5 css-8tih0y edw49t13">Apple AirPods Pro</th><td class="css-57lzw8 edw49t12">0.0212</td><td class="css-57lzw8 edw49t12">1374</td><td class="css-57lzw8 edw49t12">264</td><td class="css-57lzw8 edw49t12">153</td><td class="css-57lzw8 edw49t12">4.4</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B07ZRXF7M8</td></tr><tr><th scope="row" class="row_heading level0 row6 css-8tih0y edw49t13">Sony WF-XB700 Extra Bass True Wireless (TWS) Bluetooth Earbuds with 18hrs Battery Life, Splash Proof, BT Ver 5.0, Quick Charge, mic for Phone Calls, Suitable for Workout, Online Classes, WFH (Blue)</th><td class="css-57lzw8 edw49t12">0.0187</td><td class="css-57lzw8 edw49t12">3152</td><td class="css-57lzw8 edw49t12">609</td><td class="css-57lzw8 edw49t12">141</td><td class="css-57lzw8 edw49t12">3.9</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B085VQFZ91</td></tr><tr><th scope="row" class="row_heading level0 row7 css-8tih0y edw49t13">Ambrane Dots 38 True Wireless Earbuds TWS with Pure HD Bass, 16H Playtime, IPX4 Waterproof, Responsive Touch Sensors for Multifunctions, Compact Type-C Charging Case (Green), Normal</th><td class="css-57lzw8 edw49t12">0.0084</td><td class="css-57lzw8 edw49t12">414</td><td class="css-57lzw8 edw49t12">192</td><td class="css-57lzw8 edw49t12">57</td><td class="css-57lzw8 edw49t12">3.6</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B0995RZPQV</td></tr><tr><th scope="row" class="row_heading level0 row8 css-8tih0y edw49t13">boAt Airdopes 201 Bluetooth Truly Wireless Earbuds with Mic(Viper Green)</th><td class="css-57lzw8 edw49t12">0.0036</td><td class="css-57lzw8 edw49t12">618</td><td class="css-57lzw8 edw49t12">85</td><td class="css-57lzw8 edw49t12">25</td><td class="css-57lzw8 edw49t12">3.7</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B0856GK57Z</td></tr><tr><th scope="row" class="row_heading level0 row9 css-8tih0y edw49t13">Skullcandy Dime True Wireless Earbuds with 12 Hours Total Battery, IPX4 Sweat and Water Resistant, Secure Noise Isolating Fit (True Black)</th><td class="css-57lzw8 edw49t12">0.0026</td><td class="css-57lzw8 edw49t12">1219</td><td class="css-57lzw8 edw49t12">1061</td><td class="css-57lzw8 edw49t12">15</td><td class="css-57lzw8 edw49t12">3.7</td><td class="css-57lzw8 edw49t12">https://www.amazon.in/product-reviews/B08X1QWB9W</td></tr></tbody></table>""", height=800, scrolling=True)
