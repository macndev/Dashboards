import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import os
import warnings
import numpy as np
warnings.filterwarnings('ignore')

# set page title in tab and on page
st.set_page_config(page_title='Crop and Climate Data',page_icon=':seedling:',layout='wide')
st.title(' :seedling: View Crop and Climate Data')
# use a markdown with style html code to add a div block container to minimize space at top of page
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

# load dataset from .csv file
os.chdir(r'C:\Users\dearm\PycharmProjects\UdemyPlotlyandDash\StreamlitYT')
df = pd.read_csv('All_data_with_climate.csv')

# data contains no years on date entries, data sourced from 2004, so add date and make datetime objects
df['Plant.start.datetime'] = pd.to_datetime(df['Plant.start.date'] + '/2004')
df['Plant.end.datetime'] = pd.to_datetime(df['Plant.end.date'] + '/2004')
df['Harvest.start.datetime'] = pd.to_datetime(df['Harvest.start.date'] + '/2004')
df['Harvest.end.datetime'] = pd.to_datetime(df['Harvest.end.date'] + '/2004')

# set min and max dates for date picker as beginning and end of the year of 2004
startDate = pd.to_datetime('1/1/2004')
endDate = pd.to_datetime('12/31/2004')

# create 2 columns and enable date picking
st.subheader('Select Planting Date Range: ')
col1, col2 = st.columns((2))
with col1:
    date1 = pd.to_datetime(st.date_input('Planting Start Date', startDate))

with col2:
    date2 = pd.to_datetime(st.date_input('Planting End Date', endDate))

df = df[(df['Plant.start.datetime'] >= date1) & (df['Plant.start.datetime'] <= date2)].copy()

# enable temperature range picking
# monthly average temperatures
with col1:
    st.subheader('Select Average Temperature Range: ')
    # get min and max monthly weighted temp averages
    mintemp = df['temp.min'].min()
    maxtemp = df['temp.max'].max()
    temp1, temp2 = st.slider('Average Monthly Temp in degrees C', value=[mintemp,maxtemp])

df = df[(df['temp.min'] >= temp1) & (df['temp.max'] <= temp2)].copy()

# enable precipitation range picking
with col2:
    st.subheader('Select Precipitation Range: ')
    # get min and max precipitation amounts
    minprec = df['precip.min'].min()
    maxprec = df['precip.max'].max()
    prec1, prec2 = st.slider('Average Monthly Precipitation in mm/month', value=[minprec,maxprec])

df = df[(df['precip.min'] >= prec1) & (df['precip.max'] <= prec2)].copy()

# create data filters
st.sidebar.header('Select and filter data: ')
# filter by location
location = st.sidebar.multiselect('Select data location', df['Location'].unique())
if not location:
    df2 = df.copy()
else:
    df2 = df[df['Location'].isin(location)]

# filter by crop
crop = st.sidebar.multiselect('Select crop(s) of interest', df2['Crop'].unique())
if not crop:
    df3 = df2.copy()
else:
    df3 = df2[df2['Crop'].isin(crop)]

# filter the data
if not location and not crop:
    filtered_df = df
elif location:
    filtered_df = df3[df['Location'].isin(location)]
elif crop:
    filtered_df = df3[df3['Crop'].isin(crop)]
else:
    filtered_df = df3[df3['Location'].isin(location) & df3['Crop'].isin(crop)]

# display data in pie charts
with col1:
    st.subheader('Crops Planted by Harvest Area (km^2)')
    fig = px.pie(filtered_df, values='harvested.area',names='Crop')
    fig.update_traces(text = filtered_df['Crop'], textposition = 'outside')
    fig.update_layout(height = 1000, width = 700) # text cuts off on LHS, FIXME
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('Average Total Growing Days for each Crop')
    # calculate avg # of growing days
    by_crop_df = filtered_df.groupby(by = ['Crop'], as_index=False)['tot.days'].mean().round()
    #print(by_crop_df)
    fig = px.bar(by_crop_df, x = 'Crop', y = 'tot.days')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Table of Average Days from Plant to Harvest')
    with st.expander('View Data in Table'):
        tab = ff.create_table(by_crop_df, colorscale='ice')
        st.plotly_chart(tab, use_container_width=True)

    st.subheader('Download Data')
    with st.expander('Download Average Table'):
        csv = by_crop_df.to_csv(index = False).encode('utf-8')
        st.download_button('Download Data', data = csv, file_name='plant_averages.csv', mime = 'text/csv',
                           help='Click here to download the data as a CSV file')

    with st.expander('Download Filtered Dataset'):
        csv = filtered_df.to_csv(index = False).encode('utf-8')
        st.download_button('Download Data', data=csv, file_name='plant_data_filtered.csv', mime='text/csv',
                           help='Click here to download the data as a CSV file')

    with st.expander('Download Original Dataset'):
        csv = df.to_csv(index = False).encode('utf-8')
        st.download_button('Download Data', data=csv, file_name='plant_data.csv', mime='text/csv',
                           help='Click here to download the data as a CSV file')

# view some data over time, precipitation and temp at planting
data_precip = px.scatter(filtered_df, x = 'Plant.median', y = 'precip.at.planting', size = 'harvested.area', color = 'Crop')
data_precip['layout'].update(title = 'Precipitation during Middle of Planting',
                             titlefont=dict(size=20), xaxis=dict(title='Middle of Planting, day of year (1 = Jan 1, 365 = Dec 31)'),
                             yaxis=dict(title='Average Precipitation at Planting, mm/month'))
st.plotly_chart(data_precip, use_container_width=True)

data_temp = px.scatter(filtered_df, x = 'Plant.median', y = 'temp.at.planting', size = 'tot.days', color = 'Crop')
data_temp['layout'].update(title = 'Temperature during Middle of Planting',
                             titlefont=dict(size=20), xaxis=dict(title='Middle of Planting, day of year (1 = Jan 1, 365 = Dec 31)'),
                             yaxis=dict(title='Average Temperature at Planting, degrees C'))
st.plotly_chart(data_temp, use_container_width=True)


