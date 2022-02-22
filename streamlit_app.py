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
        "Venue of session:", ["Clementi Sports Hall", "Chinese Swimming Club", "Mt Faber SAFRA"], index=2
    )
#    cols = st.columns(2)
    
#    bug_severity = cols[1].slider("Bug severity:", 1, 5, 2)
    courts = cols[1].selectbox("Paid for Court Booking?",["No.","Yes and attended session.", "Yes but did not attend session."])
#    cols = st.columns(2)
    shuttles = cols[0].selectbox("Shuttlecocks Contributed",[0,1,2,3,4])
    hours = cols[1].selectbox("Length of Session (in hours):",[1,2])

    comment = st.text_area("Remarks if any:")
    submitted = st.form_submit_button(label="Submit")


if submitted:
    timestmp=datetime.now(tz=None)
    add_row_to_gsheet(
        gsheet_connector, [[player, str(date), venue, shuttles, hours, courts, comment,str(timestmp)]]
    )
    st.success("Thanks! Your participation has been recorded.")
    st.balloons()

expander = st.expander("See all records")
with expander:
    st.write(f"Open original [Google Sheet]({GSHEET_URL})")
    st.dataframe(get_data(gsheet_connector))
