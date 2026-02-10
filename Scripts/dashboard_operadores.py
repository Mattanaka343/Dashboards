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
    df_bar = df_valid.groupby('Operator', as_index = False)['Duration(h)'].sum()
    df_bar.sort_values('Duration(h)',ascending = False)

    fig = px.bar(
        df_bar,
        x = 'Duration(h)',
        y = 'Operator',
        title = 'Horas Recolectadas'
    )

    fig.add_vline(
        x = 5.5,
        line_dash = 'dot',
        line_color = 'red'
    )
    
    return fig

data = load()
fig = AsusTabla(data)
st.header('Horas Recolectadas Hoy')
st.markdown('---')
st.plotly_chart(fig)

        
