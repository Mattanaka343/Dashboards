import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_dark"

st.set_page_config(
    page_title = 'Dashboard Horas',
    layout = 'wide',
    page_icon = '../Resources/Images/NSym.png'
)

@st.cache_data(ttl=100)
def load_and_clean():
    try:
        data = pd.read_csv('../Data/general_data.csv')
        data['Operator'] = data['Operator'].str.replace(' ','')
        data['Operator'] = data['Operator'].str.replace('H_ALCARAZ','L_AGUILERA')
        data['Operator'] = [val.lower() if isinstance(val,str) else 'unknown' for val in data['Operator']]
        data = data[data['Operator'] != 'juan']
        data['Start_Time'] = pd.to_datetime(data['Start_Time'])
        data = data.drop_duplicates()
        return data
    except Exception as e:
        st.error(f'Error while loading data: {e}')
        return None
    
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

def monthly_data(df,month=pd.Timestamp.today().month ):
    df['Start_Time'] = pd.to_datetime(df['Start_Time'])
    month_df = df[df['Start_Time'].dt.month == month]
    return month_df

def by_operator(df,operator):
    if operator is not None:
        return df[df['Operator']==operator]
    else:
        return df

def by_skill(df,skill):
    if skill is not None:
        return df[df['SkillName'] == skill]
    else:
        return df


def graphs(df):
    fig1  = px.histogram(
        df,
        x = 'Duration(s)',
        nbins = 30,
        title = 'Recording Duration Distribution'
    )

    mean_duration = df['Duration(s)'].mean()

    fig1.add_vline(
        x = mean_duration,
        line_dash = 'dot',
        line_color = 'red'
    )

    fig2 = px.pie(
        df,
        names = 'SkillName',
        title = 'Skill Distribution'
    )


    df_valid = df[df['IsValid']==True]
    df_valid['Duration(h)'] = df_valid['Duration(s)']/3600
    df_bar1 = df_valid.groupby('SkillName',as_index=False)["Duration(h)"].sum()
    df_bar1 = df_bar1.sort_values(by ='Duration(h)',ascending=True)

    fig3 = px.bar(
        df_bar1,
        x = 'Duration(h)',
        y = 'SkillName',
        title = 'Valid Hours Collected per Skill',
        labels = {
            'x':'Hours Collected',
            'y':'Skill Name'
        }
    )

    fig3.add_vline(
        x = 30,
        line_dash = "dot",
        line_color = 'red'
    )

    df_bar2 = df_valid.groupby('Operator',as_index=False)["Duration(h)"].sum()
    df_bar2 = df_bar2.sort_values(by = 'Duration(h)')

    fig4 = px.bar(
        df_bar2,
        x = 'Duration(h)',
        y = 'Operator',
        title = 'Valid Hours Collected Per Operator',
        labels = {
            'x':'Hours Collected',
            'y': 'Operator'
        }
    )

    df_valid['Start_Time'] = df_valid['Start_Time'].dt.date
    df_timeline = df_valid.groupby('Start_Time', as_index = False)['Duration(h)'].sum()
    df_timeline['trend'] = df_timeline["Duration(h)"].rolling(window=20, min_periods=1).mean()
    df_timeline = df_timeline.rename(columns={
    "Duration(h)": "Real Amount",
    "trend": "Projected Amount"
})
    
    fig5 = px.line(
        df_timeline,
        x = 'Start_Time',
        y = ['Real Amount','Projected Amount'],
        title = 'Timeline of valid hours collected',
    )

    fig5.update_yaxes(title_text="Hours Collected")
    fig5.update_xaxes(title_text="Date")
    fig5.update_layout(legend_title_text="Metric Type")

    

    return (fig1,fig2,fig3,fig4,fig5)

def key_figures(df):
    total_hour_amount = df['Duration(s)'].sum()/3600
    df_valid = df[df['IsValid']==True]
    df_valid['Duration(h)'] = df_valid['Duration(s)']/3600
    total_valid_hour_amount = df_valid['Duration(h)'].sum()

    valid_hour_percentage = total_valid_hour_amount/total_hour_amount * 100

    return (total_valid_hour_amount, total_hour_amount, valid_hour_percentage)

def get_averages_and_totals(df):
    df_valid = df[df['IsValid']==True]
    df_valid['Duration(h)'] = df_valid['Duration(s)']/3600
    df_valid['Start_Time'] = df_valid['Start_Time'].dt.date

    avgs = df_valid.groupby('Start_Time')['Duration(h)'].mean()

    means = []
    avgs = df_valid.groupby('Start_Time')['Duration(h)'].mean()

    means = []
    for date in avgs.index:
        date_totals = []
        for operator in df_valid['Operator'].unique():
            tmp = df_valid[df_valid['Operator']==operator]
            op_dates = tmp['Start_Time'].unique()
            if date in op_dates:
                vals = tmp.groupby('Start_Time')['Duration(h)'].sum()
                date_totals.append(vals.loc[date])
        day_mean = np.array(date_totals).mean()
        means.append(day_mean)
            
    averages = pd.DataFrame(
            index= avgs.index,
            columns=['Duration(h)'],
            data=means
        )
    
    totals = df_valid.groupby('Start_Time')['Duration(h)'].sum()

    return (averages,totals)

data = load_and_clean()

if data is not None:
    st.title('Operative KPI Dashboard')
    st.markdown('---')

    with st.sidebar:
        st.header('Define the period')

        form = st.selectbox(
            'Select a timeframe',
            options = ['All Time','Weekly','Daily','Monthly','Yesterday'],
            index = 0
        )

        with st.expander('Further Options'):
            opes = list(data['Operator'].unique())
            opes.insert(0,'All')
            ope = st.selectbox(
                'Select an operator',
                options = opes,
                index = 0
            )
            
            skills = list(data['SkillName'].unique())
            skills.insert(0,'All')
            skill = st.selectbox(
                'Select a skill',
                options = skills,
                index = 0
            )

            if form == 'Monthly':
                idx = int(pd.Timestamp.today().month) -1

                month = st.selectbox(
                    'Select a month',
                    options = [i for i in range(1,13)],
                    index = idx
                )
    
        bot  = st.button(
            'Launch',
            use_container_width = True,
            type = 'primary'
        )


        metrics = key_figures(data)

        st.markdown('---')
        st.header('Key Values')
        st.metric('Total Hours:', metrics[1].round(2))
        st.metric('Valid Hours:', metrics[0].round(2))
        st.metric('Valid Rate (Percentage):', metrics[2].round(2))

    if bot:
        if form == 'Weekly':
            data = weekly_data(data)
        elif form == 'Today':
            data = daily_data(data)
        elif form == 'Monthly':
            data = monthly_data(data,month)
        elif form == 'Yesterday':
            data = yester_data(data)

        if ope != 'All':
            data = by_operator(data,ope)

        if skill != 'All':
            data = by_skill(data,skill)
            
        figures = graphs(data)

        st.plotly_chart(figures[0])
        if skill == 'All':
            st.plotly_chart(figures[2])
        
        if ope == 'All':
            st.plotly_chart(figures[3])

        col3, col4 = st.columns(2)

        d_info = get_averages_and_totals(data)

        if form in ['Monthly','All Time','Weekly']:
            with col3:
                st.header('Daily Averages')
                st.markdown('How much data was collected per operator per day on average')
                st.dataframe(d_info[0])
            
            with col4:
                st.header('Daily Totals')
                st.markdown('Total hours collected by all operators on a given date')
                st.dataframe(d_info[1])
            
            st.plotly_chart(figures[4])

    else:
        st.header('Welcome')
        st.markdown("""
        Welcome to the KPI dashboard. Select a timeframe to view and click launch!
                    """)
        




        






    

    

     