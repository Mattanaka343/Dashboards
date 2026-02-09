import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


st.set_page_config(
    page_title = 'Asustadores',
    layout = 'wide'
)

@st.cache_data(ttl=100)
def load():
    try:
        data = pd.read_csv('../Data/reporte_detallado.csv')
        data['Start_Time'] = pd.to_datetime(data['Start_Time'])
        cutoff = (pd.Timestamp.today()).date()
        data = data[data['Start_Time'] == cutoff]
        return data
    except Exception as e:
        st.error(f'Error while loading data : {e}')
        return None
    
def AsusTabla(df):
    df_valid = df[df['IsValid']==True]
    df_valid['Duration(h)'] = df_valid['Duration(s)']/3600
    df_bar = 


    pass

        
