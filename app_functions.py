#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 20:29:40 2020

@author: tbury
"""



import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output



cols = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]    
    

def make_r_d_scatter(df_covid, countries, n_days=30,
                     scale='Raw',
                     start_date='2020-03-01',
                     delay=0):
    '''
    Make a scatter plot of r (contact rate) as a funciton of number of new
    deaths in the past n_days.

    Parameters
    ----------
    df_covid : DataFrame
        covid dataset.
    countries: list
        list of countries to plot
    n_days: int
        number of days of death count to include
    scale: string
        One of ['Raw','Per million habitants','Max value']
    start_date: string
        date from which to begin plotting
    delay: int
        number of days delay in computing cumulative deaths

    Returns
    -------
    fig: Plotly figure

    '''
    
    # If no data, return empty figure
    if len(countries)==0:
        return px.scatter()
    

    # Get covid data for select countries
    df_plot = df_covid[df_covid['location'].isin(countries)].copy()
    
    
    # Compute accumulative deaths over previous n_days for each country
    df_plot['new_deaths_acc'] = \
        df_plot.groupby('location')['new_deaths'].rolling(n_days).sum().reset_index(0,drop=True)
    
    # Add a delay by shifting new_deaths_acc
    df_plot['new_deaths_acc_delay'] = df_plot['new_deaths_acc'].shift(delay)
    
    
    # Function to scale data
    def normalise_deaths(df_sub):
        if scale=='Per million habitants':
            df_sub['new_deaths_acc_delay'] = df_sub['new_deaths_acc_delay']*1e6/df_sub['population']
        if scale=='Max value':
            df_sub['new_deaths_acc_delay'] = df_sub['new_deaths_acc_delay']/df_sub['new_deaths_acc_delay'].max()
        return df_sub
    # Apply function
    df_plot = df_plot.groupby('location').apply(normalise_deaths)
    
    
    # Sort according to list of countries
    df_plot['location'] = df_plot['location'].astype('category')
    df_plot['location'].cat.set_categories(countries, inplace=True)
    df_plot.sort_values(['location','date'],inplace=True)
    
    # Only keep values > start_date
    df_plot = df_plot[df_plot['date']>start_date]

    # If multiple countries provided, use different colour for each country
    if len(countries)!=1:
        # Create scatter plot of contact rate vs consecutive deaths
        fig = px.scatter(df_plot,
                         x='new_deaths_acc_delay',
                         y='reproduction_rate',
                         hover_data=['date'],
                         color='location',
                         color_discrete_sequence=cols,
                         )
    
    # If only 1 country provided, color code time points
    else:
        # Make integer values for each date entry
        date_to_val = df_plot['date'].map(
            pd.Series(np.arange(len(df_plot)), 
                      index=df_plot['date'].values).to_dict())
        
        tickvals = [0,int(len(date_to_val)/2),len(date_to_val)-1]
        index_tickvals = [date_to_val.index[tv] for tv in tickvals]
        ticktext = [str(df_plot['date'][idx]) for idx in index_tickvals]
        
        customdata=df_plot['date']
        # Create scatter plot of contact rate vs consecutive deaths
        fig = go.Figure(
            go.Scatter(
                x=df_plot['new_deaths_acc_delay'],
                y=df_plot['reproduction_rate'],
                mode='markers',
                marker_color=date_to_val,
                marker_colorscale='Plasma',
                marker_showscale=True,
                marker_size=8,
                marker_colorbar=dict(tickvals=tickvals, 
                                     ticktext=ticktext, 
                                     title_text='date'
                                     ),
                customdata=customdata,
                hovertemplate="Date: %{customdata}<br>x: %{x}<br>y: %{y}",
                )
            )
    
    fig.update_xaxes(title='Cumulative deaths over {} days'.format(n_days))
    fig.update_yaxes(title='Contact rate')
        
    
    return fig




# fig = make_r_d_scatter(df_covid, countries=['United Kingdom'])
# fig.write_html('temp.html')



def make_grid_plot(df_covid, countries, res, scale):
    '''
    Make grid plot showing covid trajectories and
    derived metrics.

    Parameters
    ----------
    df_covid : DataFrame
        dataframe containing covid data
    countries : list of strings
        List of countries to plot
    res : string
        One of ['Daily','7 day average']
    scale: string
        One of ['Raw','Per million habitants','Max value']

    Returns
    -------
    Plotly fig.

    ''' 
    

    fig = make_subplots(rows=4, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02   ,
                        )

    
    if res=='Daily':
        cases_col = 'new_cases'
        deaths_col = 'new_deaths'
        I_col = 'I'
        R_col = 'R'
    else:
        cases_col = 'new_cases_7dayAv'
        deaths_col = 'new_deaths_7dayAv'
        I_col = 'I'
        R_col = 'R_7dayAv'



    
    # Loop through each country
    count=0
    for country in countries:
        
        # Get country-specific data
        df_plot = df_covid[df_covid['location']==country]
        population = df_plot['population']
        
        # Assign plot values
        x = df_plot['date']
        if scale=='Raw':
            y1 = df_plot[cases_col]
            y2 = df_plot[deaths_col]
            y3 = df_plot[I_col]
            y4 = df_plot[R_col]
        
        if scale=='Per million habitants':
            y1 = df_plot[cases_col]*1e6/population
            y2 = df_plot[deaths_col]*1e6/population
            y3 = df_plot[I_col]*1e6/population
            y4 = df_plot[R_col]
            
            
        if scale=='Max value':
            y1 = df_plot[cases_col]/df_plot[cases_col].max()
            y2 = df_plot[deaths_col]/df_plot[deaths_col].max()
            y3 = df_plot[I_col]/df_plot[I_col].max()
            y4 = df_plot[R_col]
        
        # Plot new cases
        fig.add_trace(
            go.Scatter(x=x,
                       y=y1,
                       mode='lines',
                       name=country,
                       legendgroup=country,
                       marker={'color':cols[count]},
                       ),
            row=1,col=1,
        )
        
        # Plot new deaths
        fig.add_trace(
            go.Scatter(x=x,
                       y=y2,
                       mode='lines',
                       name=country,
                       legendgroup=country,
                       showlegend=False,
                       marker={'color':cols[count]},
                       ),
            row=2,col=1,
        )    
        
        # Plot total infected
        fig.add_trace(
            go.Scatter(x=x,
                       y=y3,
                       mode='lines',
                       name=country,
                       legendgroup=country,
                       showlegend=False,
                       marker={'color':cols[count]},
                       ),
            row=3,col=1,
        )           
        
        # Plot contact ratio
        fig.add_trace(
            go.Scatter(x=x,
                       y=y4,
                       mode='lines',
                       name=country,
                       legendgroup=country,
                       showlegend=False,
                       marker={'color':cols[count]},
                       ),
            row=4,col=1,
        )
        
        count+=1
    
    # Layout properties
    fig.update_xaxes(title='Date',row=4,col=1)
    fig.update_yaxes(title='New cases',row=1,col=1)
    fig.update_yaxes(title='New deaths',row=2,col=1)
    fig.update_yaxes(title='Infected',row=3,col=1)
    fig.update_yaxes(title='Contact ratio',row=4,col=1)
    
    fig.update_layout(height=700,
                      margin={'l':0,'r':0,'b':20,'t':40}
                      )
    
    
    return fig

