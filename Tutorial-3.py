import streamlit as st
import pandas as pd
import numpy as np
from datetime import date


# read csv file
df = pd.read_csv("KKM_Incidents.csv",  index_col=0)

# format DatabaseInsertTime column from object to datetime
# 2025-11-14 20:37:33.000 +0800 --> 14-11-2025
df['DatabaseInsertTime'] = pd.to_datetime(
    df['DatabaseInsertTime'],
    errors='coerce'
)


# filter selected columns only
df = df[["DatabaseInsertTime", "AgencyEventId", "AgencyEventSubtypeCode", "AgencyEventSubtypeCodeDesc", "AgencyEventTypeCode", "AgencyEventTypeCodeDesc", "ProQACaseType"]]



today = date.today()
last_day = date.today()

start_date = st.date_input('Start Date', last_day, format='DD-MM-YYYY')
end_date = st.date_input('End Date', today, format='DD-MM-YYYY')

# Filter by date (inclusive of both start and end dates)
filtered_df = df[
    (df['DatabaseInsertTime'].dt.date >= start_date) &
    (df['DatabaseInsertTime'].dt.date <= end_date)
]

# Display date in DD-MM-YYYY format if required
filtered_df['DatabaseInsertTime'] = (
    filtered_df['DatabaseInsertTime'].dt.strftime('%d-%m-%Y')
)


### data declarations
# total KKM Callcards
total_incidents = len(filtered_df) 

# total callcards that did protocols
allowed_codes = (
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', 
    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 
    '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 
    '31', '32', '33', '34', '35', '36', '37', '39X1', '39X2'
)
proqa_cases = filtered_df[filtered_df["AgencyEventTypeCode"].isin(allowed_codes)
                    & filtered_df["ProQACaseType"].notna()]
medical_proqaCases = len(proqa_cases) 

# total callcards without protocols
without_proqa = total_incidents - medical_proqaCases


# count the incidents by medical proqa cases
event_counts = (
    proqa_cases.groupby(['AgencyEventTypeCode', 'AgencyEventTypeCodeDesc'])
    .size()
    .reset_index(name='Count')
    .sort_values(by='Count', ascending=False)
)
event_counts = event_counts.reset_index(drop=True)



st.set_page_config(layout="wide")
st.title("KKM Incidents")
st.divider()

total, proqa = st.tabs(["KKM Overall Summary", "ProQA Cases"])

with total:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total KKM Call Card", total_incidents)
    with col2:
        st.metric("ProQA Incidents", medical_proqaCases)
    with col3:
        st.metric("Non ProQA Incidents", without_proqa)

    
    st.subheader("Callcard List")
    st.dataframe(filtered_df, use_container_width=True)
with proqa:
    st.subheader("ProQA Case Classification")
    st.dataframe(event_counts, use_container_width=True)

    st.divider()
    st.subheader("ProQA CallCards")
    st.dataframe(proqa_cases, use_container_width=True, hide_index=True)