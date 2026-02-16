import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title = 'Operadores',
    layout = 'centered'
)

@st.cache_data(ttl=100)

def load():
    try:
        data =  pd.read_csv('../Data/reporte_detallado.csv')
        data['Operator'] = data['Operator'].str.replace(' ','')
        data['Operator'] = data['Operator'].str.replace('H_ALCARAZ','L_AGUILERA')
        data = data[data['Operator']!= 'JUAN']
        data['Start_Time'] = pd.to_datetime(data['Start_Time'])
        return data 
    except Exception as e:
        st.error(f'Error al cargar los datos: {e}')

def weekly_data(df):
    cutoff = (pd.Timestamp.today() - pd.Timedelta(days=7)).date()
    df['Start_Time'] = pd.to_datetime(df['Start_Time'])
    week_db = df[df['Start_Time'].dt.date >= cutoff]
    return week_db

def daily_data(df):
    cutoff = pd.Timestamp.today().date()
    df['Start_Time'] = pd.to_datetime(df['Start_Time'])
    day_db = df[df['Start_Time'].dt.date == cutoff]
    return day_db

def yester_data(df):
    cutoff = (pd.Timestamp.today() - pd.Timedelta(days=1)).date()
    df['Start_Time'] = pd.to_datetime(df['Start_Time'])
    yester_df = df[df['Start_Time'].dt.date >= cutoff]
    return yester_df

def monthly_data(df):
    pass

def graphs(df,expectation):
    df_valid = df[df['IsValid']==True]
    df_valid['Duration(h)'] = df_valid['Duration(s)']/3600

    fig1 = px.pie(
        df_valid,
        names = 'SkillName',
        title = 'Distribución de tareas realizadas'
    )

    df_bar1 = df_valid.groupby()
    fig2 = px.bar(
        df_bar1,
        x = 'Operator',
        y = 'Duration(h)'
    )

    return fig1
