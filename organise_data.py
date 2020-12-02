#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 10:06:18 2020

Test app functions

@author: tbury
"""


import numpy as np
import pandas as pd

import plotly.express as px


# Import covid data
cols = ['location','date','new_cases','new_deaths',
        'new_cases_per_million','new_deaths_per_million',
        'reproduction_rate','population']

df_covid = pd.read_csv('../data/owid-covid-data.csv',
                       usecols=cols,)

# Sort by location
df_covid.sort_values(['location','date'],inplace=True)

# Get 7-day rolling average for new cases and new deaths
df_covid['new_cases_7dayAv'] = df_covid.groupby('location').rolling(7)['new_cases'].mean().reset_index(0,drop=True)
df_covid['new_deaths_7dayAv'] = df_covid.groupby('location').rolling(7)['new_deaths'].mean().reset_index(0,drop=True)

# # Get countries in the top 10 for total cases
# df_count_cases = df_covid.groupby('location').sum()['new_cases'].sort_values()[::-1][:30]
# list_countries = list(df_count_cases.index)

# df_top10 = df_covid[df_covid['location'].isin(list_countries)]

# Export dataframe
df_covid.to_csv('data/df_covid.csv',index=False)




# fig = px.line(df_top10,
#               x='date',
#               y='new_cases',
#               color='location')
# fig.write_html('temp.html')

# fig = px.line(df_top10,
#               x='date',
#               y='new_cases_7dayAv',
#               color='location')
# fig.write_html('temp2.html')






