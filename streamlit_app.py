import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import numpy as np

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
#SPREADSHEET_ID = "1QlPTiVvfRM82snGN6LELpNkOwVI1_Mp9J9xeJe-QoaA"
SPREADSHEET_ID="1cH3TrGx0VShMbVDlswhSqRshBdRgTq9ary-ISD-Ibzk"
SHEET_NAME = "Database"
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
            range=f"{SHEET_NAME}!A:H",
            body=dict(values=row),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )


#st.set_page_config(page_title="Bug report", page_icon="🐞", layout="centered")
st.set_page_config(page_title="Badminton Kakis", page_icon="🏸", layout="centered")

st.title("🏸 Badminton Kakis")
st.subheader("Beta Version")

gsheet_connector = connect_to_gsheet()

#st.sidebar.write(
#    f"This app shows how a Streamlit app can interact easily with a [Google Sheet]({GSHEET_URL}) to read or store data."
#)

#st.sidebar.write(
#    f"[Read more](https://docs.streamlit.io/knowledge-base/tutorials/databases/public-gsheet) about connecting your Streamlit app to Google Sheets."
#)

form = st.form(key="annotation")

with form:
    cols = st.columns((1, 1))
    player = cols[0].selectbox("I am:",["Mike","Hugo Boss", "Wing Gor","Super Stan","Soon"])
    date = cols[1].date_input("Date of session played or court booked:")
    venue = cols[0].selectbox(
        "Venue of session:", ["Clementi Sports Hall", "Mt Faber SAFRA","Kim Seng CC], index=2
    )
#    cols = st.columns(2)
    
#    bug_severity = cols[1].slider("Bug severity:", 1, 5, 2)
    courts = cols[1].selectbox("Paid for Court Booking?",["No.","Yes and attended session.", "Yes but did not attend session."])
#    cols = st.columns(2)
    shuttles = cols[0].selectbox("Shuttlecocks Contributed",[0,1,2,3,4])
    hours = cols[1].selectbox("Length of Session (in hours):",[1,2])

    comment = st.text_area("Remarks if any:")
    submitted = st.form_submit_button(label="Submit")

#"""    
#if submitted:
#    timestmp=datetime.now(tz=None)
#    add_row_to_gsheet(
#        gsheet_connector, [[player, str(date), venue, shuttles, hours, courts, comment,str(timestmp)]]
#    )
#    st.success("Thanks! Your participation has been recorded.")
#    st.balloons()

#expander = st.expander("See all records")
#with expander:
#    st.write(f"Open original [Google Sheet]({GSHEET_URL})")
#    st.dataframe(get_data(gsheet_connector))
#"""
if submitted:
#    st.write(datetime.now(tz=None))
    timestmp=datetime.now(tz=None)
    add_row_to_gsheet(
        gsheet_connector, [[player, str(date), venue, shuttles, hours, courts, comment,str(timestmp)]]
    )
    st.success("Thanks! Your participation has been recorded.")
    st.balloons()

expander = st.expander("See Accounts Status")
with expander:
#    st.write(f"Open original [Google Sheet]({GSHEET_URL})")
#    st.dataframe(get_data(gsheet_connector))
    df=get_data(gsheet_connector)
    #st.write(df)

##START HERE
    # Fixed Data
    ShuttleCost=2.75
    dict_attendance = {"Yes and attended session." : 1, "No." : 1,"Yes but did not attend session.":0}
    dict_courts={"Yes and attended session." : 1, "No." : 0,"Yes but did not attend session.":1}
    dict_recon={"Yes and attended session." : 0, "No." : 0,"Yes but did not attend session.":1}
    dict_venue={"Clementi Sports Hall":7.4,"Mt Faber SAFRA":5.2,"Kim Seng CC":5}

    # Derive dataframe
    df.insert(8,'Attendance', df['PaymentnAttendance'] )
    df['Attendance']=df['Attendance'].replace(to_replace=dict_attendance)
    df.insert(9,'Courts', df['PaymentnAttendance'] )
    df['Courts']=df['Courts'].replace(to_replace=dict_courts)
    df.insert(10,'Recon1', df['PaymentnAttendance'] )
    df['Recon1']=df['Recon1'].replace(to_replace=dict_recon)
    df.insert(11,'VenueCost', df['Venue'] )
    df['VenueCost']=df['VenueCost'].replace(to_replace=dict_venue)
    df['ShuttleExpense']=pd.to_numeric(df.Shuttles)*ShuttleCost  #change df.Shuttles to float
    df['CourtExpense']=df.Courts*pd.to_numeric(df.Hours)*df.VenueCost
    df['Recon1']=df['Recon1']*df['CourtExpense']

    # Pivot Table
    df_Attendance=df.pivot_table(index='Date',columns='Player',values='Attendance',fill_value=0)
    df_Shuttle=df.pivot_table(index='Date',columns='Player',values='ShuttleExpense',aggfunc=np.sum,fill_value=0)
    df_Court=df.pivot_table(index='Date',columns='Player',values='CourtExpense',fill_value=0)
    df_Recon1=df.pivot_table(index='Date',columns='Player',values='Recon1',fill_value=0)#*df1.pivot_table(index='Date',columns='PlayerID',values='Hours',fill_value=0)
    
    #st.write(df.Player)
#    st.write(df_Attendance)
    
    df_Cost=df_Court+df_Shuttle
    df_TotalCost=df_Cost.sum(axis=1)
    df_AverageCost=df_TotalCost/df_Attendance.sum(axis=1)
#    st.write(df_AverageCost)

    # Process Pivot Table
    df_Recon2=df_Cost.sub(df_AverageCost, axis='rows')*df_Attendance
    df_ReconNew=df_Recon1+df_Recon2
    df_ReconNew.sum(axis=1)
    df_ReconNew.loc['Total']=df_ReconNew.sum(axis=0)
    df_ReconNew['CheckSum']=df_ReconNew.sum(axis=1)
    st.write(df_ReconNew)
#    st.write(df_ReconNew.sum(axis=0))
 #   st.write(df_ReconNew.sum(axis=0).to_frame().T)    
##END HERE

expander2= st.expander("See Raw Data")
with expander2:
#    st.write(f"Open original [Google Sheet]({GSHEET_URL})")
    st.dataframe(get_data(gsheet_connector))

#st.container()
#with st.container():
#    st.write(f"Open original [Google Sheet]({GSHEET_URL})")
#    st.dataframe(get_data(gsheet_connector))
