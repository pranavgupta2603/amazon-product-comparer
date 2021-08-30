import pyautogui as pg
import streamlit as st
import pyperclip


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
        
#st.session_state["con"] = False
