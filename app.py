import streamlit as st
import uuid
import boto3
import botocore
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import requests
from all_funcs import *
from create_table import *
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
st.markdown("""
<style>
#MainMenu{visibility: hidden;} 
td.css-57lzw8:nth-of-type(4){}
footer, label.css-zyb2jl, img.css-1jhkrss, button.css-bl767a {visibility: hidden;}
.copy-button{color:red;}

</style>

""", unsafe_allow_html=True)

if "iden" not in st.session_state:
    st.session_state["iden"] = None
    st.session_state["sesInBucket"] = None
    st.session_state['dataInBucket'] = None
    st.session_state['linksFinal'] = []
    st.session_state['editLinks'] = []
    st.session_state['chosen'] = ""
    st.session_state["refresh"] = ""
    
id_place_con = st.sidebar.container()
    
def from_session():
    already_in_body = st.session_state.dataInBucket
    sessions_here = already_in_body.split(",")
    a = []
    indices = [("Comparison "+ str(num)) for num in range(1, len(sessions_here)+1)]
    comparison_data_con = st.sidebar.container()
    with comparison_data_con:
        chosen = st.selectbox("Choose Session:", indices)
        a = list(set(sessions_here[indices.index(chosen)].split("\n")))
        a.remove("")
        if st.session_state["refresh"] == True:
                st.session_state.linksFinal = []
        if chosen != st.session_state.chosen:
            st.session_state.chosen = chosen
            st.session_state["a"] = a
            st.session_state["linksFinal"] = a
    return sessions_here

def main():
    #if "hey" not in st.session_state:
    count = st_autorefresh(interval=1, limit=2, key="hey")
    #st.write(st.session_state)
    id_place_con.text("Comparison ID:")
    id_place_con.code(st.session_state.iden.replace(".txt", ""))
    id_place_con.download_button("Download ID", st.session_state.iden.replace(".txt", ""), file_name="Session ID.txt")
    id_place_con.warning("Keep Comparison ID to access and save your comparisons.")
    id_place_con.markdown("<hr>", unsafe_allow_html=True)
    if st.session_state.sesInBucket==True:
        sessions_here = from_session()
    else:
        sessions_here = []
    #st.write(st.session_state.linksFinal)
    if len(st.session_state) > 1:
        for k in st.session_state:
            if st.session_state[k] == True and k.isdigit():
                st.session_state["linksFinal"].pop(int(k))
    
    with st.sidebar.form(key='my_form'):
        placeholder = st.empty()
        s = placeholder.text_input(label='Enter URL')
        submit = st.form_submit_button(label='Submit')
        if submit:
            try:
                check_paste = requests.get(s)
                if s in st.session_state["linksFinal"] or s.find("amazon.in") == -1:
                    pass
                else:
                    st.session_state["linksFinal"].append(s)
                
            except:
                st.error('Not a valid URL')
    conf1, refre1 = st.sidebar.columns([1, 1])
    confirm = conf1.button("Compare")
    refresh = refre1.button("Empty List", key="refresh")
    if refresh:
        st.session_state.linksFinal = []

    if len(st.session_state.linksFinal) == 0:
            pass
    else: 
        exp=st.expander("Expand", expanded=True)
        with exp:
            create_vars(st.columns(len(st.session_state.linksFinal)))
    if confirm:
        string = create_table(st.session_state.linksFinal)
        save_data_in_session(string, st.session_state.sesInBucket, sessions_here)
        #count = st_autorefresh(interval=1, limit=2)
if st.session_state.iden != None:
    main()
    
else:
    enter_it = st.sidebar.container()
    lol2 = st.sidebar.container()
    create_it = st.sidebar.container()
    with enter_it:
        textPlace = st.empty()
        produce_error = st.empty()
        enter_uni_id = textPlace.text_input("Enter Comparison ID if you have one:")
        if enter_uni_id == "":
            pass
        else:
            try:
                check_iden = s3.get_object(Bucket="productreviewsdata", Key="sessions/"+enter_uni_id+".txt")
                st.session_state.iden = enter_uni_id + ".txt"
                st.session_state.sesInBucket = True
                st.session_state.dataInBucket = already_in_body = check_iden["Body"].read().decode()
                textPlace.empty()
                produce_error.empty()
            except Exception as e:
                produce_error.error("Comparison ID not found!")
            
    with lol2:
        or_thing = st.empty()
        or_thing.write("OR")
    with create_it:
        create_it_button = st.empty()
        thing = create_it_button.button("Create Comparison ID")
        if thing == True:
            iden = str(uuid.uuid4())
            st.session_state["iden"] = iden + ".txt"
            st.session_state.sesInBucket = False
    if st.session_state.iden != None:
        textPlace.empty()
        or_thing.empty()
        create_it_button.empty()
        produce_error.empty()
        main()
            

    
