#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 10:06:18 2020

Parse raw covid data
Compute contact rate 

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

# Export dataframe to local app directory
df_covid.to_csv('data/df_covid.csv',index=False)






