from xml.dom import NamespaceErr
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import numpy as np
import random


SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID="1cH3TrGx0VShMbVDlswhSqRshBdRgTq9ary-ISD-Ibzk"
SHEET_NAME = "Database2"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"


@st.experimental_singleton()
def connect_to_gsheet():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[SCOPE],
    )

    service = build("sheets", "v4", credentials=credentials)
    gsheet_connector = service.spreadsheets()
    return gsheet_connector


def get_data(gsheet_connector) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:H",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def add_row_to_gsheet(gsheet_connector, row) -> None:
    values = (
        gsheet_connector.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:G",
            body=dict(values=row),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )


st.set_page_config(page_title="Badminton Kakis", page_icon="🏸", layout="centered")

st.title("🏸 Badminton Kakis")

gsheet_connector = connect_to_gsheet()

form = st.form(key="annotation")

with form:

    cols = st.columns((1, 1))
    player_name = cols[0].selectbox("I am:",[" ","Mike","Hugo Boss", "Kah Wing","Super the Man","Soon","Adrian Chuah","Alvin","Dennis","Jianwei","Kayes","Ken","Prince","Seb","Tom","WL","Francis","Guest"])
#    date = cols[1].date_input("Date of session played or court booked:")
    session_name = cols[0].selectbox(
        "Session:", [
        "3 Mar 2022, Chinese Swimming Club, 1 hour",    
        "23 Mar 2022, Clementi Sports Hall, 1 hour",
        "17 Feb 2022, Chinese Swimming Club, 1 hour", 
        "7 Feb 2022, Clementi Sports Hall, 1 hour"]
    ) #, index=2
    
#    bug_severity = cols[1].slider("Bug severity:", 1, 5, 2)
#    courts = cols[1].selectbox("Paid for Court Booking?",["No.","Yes and attended session.", "Yes but did not attend session."])
    shuttles_contributed = cols[0].selectbox("Shuttlecocks Contributed:",[0,1,2,3,4,5])
    attendance= cols[1].selectbox("Attended session:",["Yes","No"])
    court_payment = cols[1].selectbox("Paid for court booking:",["No","Yes"])
    
#    hours = cols[1].selectbox("Length of Session (in hours):",[1,2])
    comments = st.text_area("Remarks if any:")
    submitted = st.form_submit_button(label="Submit")

if submitted:
 #    st.write(datetime.now(tz=None))
     timestmp=datetime.now(tz=None)
     add_row_to_gsheet(
         gsheet_connector, [[player_name, session_name, shuttles_contributed, attendance, court_payment, comments,str(timestmp)]]
     )

     st.success("Thanks! Your participation has been recorded.")
     st.balloons()
     #st.write(session_name)



expander= st.expander("Raw Data from 10 Jan 2023")
with expander:
    st.write(f"Open original [data]({GSHEET_URL})")
    st.dataframe(get_data(gsheet_connector)[["player_name","session_name","attendance","shuttles_contributed","court_payment","comments"]])

expander3=st.expander("No Accounts Carried Forward to 10 Jan 2023")
#with expander3:
#    data = {'Player': ['Adrian Chuah', 'Mike', 'WL'], 'Credit': [-1.80, -29.10, 30.90]}  
#    df=pd.DataFrame(data)
#    st.write(df)

# expander2 = st.expander("See Accounts Status")
# with expander2:

#     df=get_data(gsheet_connector)

#     # Fixed Data
#     shuttle_cost=2.75
#     dict_attendance = {"Yes" : 1, "No" : 0}
#     dict_venue_cost={"Clementi Sports Hall":7.4,"Mt Faber SAFRA":5.2,"Kim Seng CC":5,"Chinese Swimming Club":9}
#     dict_court_payment = {"Yes" : 1, "No" : 0}
#     csc_entrancefee=3
# #    dict_case2_venue={"Clementi Sports Hall":0,"Mt Faber SAFRA":0,"Kim Seng CC":0,"Chinese Swimming Club":1}
# #    dict_case2_player={"Mike":0,"Hugo Boss":0, "Wing Gor":0,"Super Stan":0,"Soon":1}

#     # Derive dataframe
#     df[['date', 'venue', 'hour']] = df['session_name'].str.split(',', expand=True)
#     df['date']=pd.to_datetime(df['date'])#,format='%d %b %y')
#     df['hour']=pd.to_numeric(df['hour'].str.rstrip('hour'))
#     #df.venue=df.venue.str.replace(' ','')
#     df['court_payment']=pd.to_numeric(df['court_payment'].replace(dict_court_payment,regex=True))
#     df['attendance']=df['attendance'].replace(dict_attendance, regex=True)  
#     df['shuttle_expense']=pd.to_numeric(df['shuttles_contributed'])*shuttle_cost
#     df['court_expense']=df['venue'].replace(dict_venue_cost,regex=True)*df['hour']*df['court_payment']
#     df['case1']=df['court_payment']-df['attendance']
#     df['case1']=df['case1'].loc[df['case1']>0]
#     df['case1']=df['case1'].fillna(0)
# #    df['case21']=df.venue.apply(lambda venue_var: 1 if venue_var==" Chinese Swimming Club" else 0)
# #    df['case22']=df.player_name.apply(lambda player_var: 1 if player_var=="Soon" else 0)
#     df["case21"]=0
#     df.loc[(df.venue==" Chinese Swimming Club") & (df.player_name=="Soon"), "case21"] = 1
#     df['case22']=0
#     df.loc[(df.venue==" Chinese Swimming Club") & (df.player_name!="Soon"), "case22"] = 1
   

#     # Pivot Table
#     df_attendance=df.pivot_table(index='date',columns='player_name',values='attendance',fill_value=0)
#     df_shuttle=df.pivot_table(index='date',columns='player_name',values='shuttle_expense',aggfunc=np.sum,fill_value=0)
#     df_court=df.pivot_table(index='date',columns='player_name',values='court_expense',fill_value=0)
#     df_case1=df.pivot_table(index='date',columns='player_name', values='case1',fill_value=0)*df_court
#     df_case21=df.pivot_table(index='date',columns='player_name', values='case21',fill_value=0)
#     df_case22=df.pivot_table(index='date',columns='player_name', values='case22',fill_value=0)*csc_entrancefee*(-1)
#     #st.write(df_case22)
#     df_expense=df_court+df_shuttle
#     df_totalexpense=df_expense.sum(axis=1)
#     df_averageexpense=df_totalexpense/df_attendance.sum(axis=1)
#     df_csc_entrance=df_case22.sum(axis=1)
#     df_case21["Soon"]=df_case21["Soon"]*df_csc_entrance*(-1)
#     #st.dataframe(df_case21)
#     #st.dataframe(df_case22)

#     # Process Pivot Tables
#     df_recon=df_expense.sub(df_averageexpense, axis='rows')*df_attendance
#     df_recon=df_recon+df_case1+df_case21+df_case22
#     #df_recon.loc["total"]=df_recon[1:-1].sum(axis=1)
#     df_recon['CheckSum']=df_recon.sum(axis=1)
#     #df_recon.loc['Total']=df_recon.sum(numeric_only=True,axis=0).T
#     #st.dataframe(pd.concat(df_recon,df_recon.sum(axis=0).to_frame().T))
#     #st.dataframe(df_recon.dtype)
#     #st.write('Recon')
#     #st.write(df_recon)
#  #   st.dataframe(df_recon.style.format("{:.2f}"))
#     #df_recon
#     #st.write(df_recon.dtypes)
#     st.write(df_recon)
#     st.write()
#     st.write("Total")
# #    st.dataframe(df_recon.sum(axis=0).to_frame().T)
    

    

