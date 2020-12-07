#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 14 Nov 2020

Dash app for covid analysis

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


#-------------
# Launch the dash app
#---------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Get mathjax for latex
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML']


app = dash.Dash(__name__, 
				external_stylesheets=external_stylesheets,
                external_scripts = external_scripts,
				)


print('Launching dash')
server = app.server



# Import covid data
df_covid = pd.read_csv('data/df_covid2.csv')
list_countries = df_covid['location'].unique()

#------------
# functions
#-------------




def make_grid_plot(countries, res, scale):
    '''
    Make grid plot showing covid trajectories and
    derived metrics.

    Parameters
    ----------
    countries : list of strings
        List of countries to plot
    res : string
        One of ['Daily','7 day average']
    scale: string
        One of ['Raw','Per million habitants']

    Returns
    -------
    Plotly fig.

    ''' 
    

    fig = make_subplots(rows=4, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02   ,
                        )
    
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





def make_traj_plot(countries, var, res):
    '''
    Make plot of covid trajectories

    Parameters
    ----------
    countries : list of strings
        List of countries to plot
    var : string
        One of ['New cases','New deaths']
    res : string
        One of ['Daily','7 day average']

    Returns
    -------
    Plotly fig.

    '''

    # Based on var and res, which column are we plotting
    if var=='New cases':
        if res=='Daily':
            col_plot = 'new_cases'
        else:
            col_plot = 'new_cases_7dayAv'
            
    if var=='New deaths':
        if res=='Daily':
            col_plot = 'new_deaths'
        else:
            col_plot = 'new_deaths_7dayAv'
   
    # Filter df to only include list of countries provided
    df_plot = df_covid[df_covid['location'].isin(countries)]

    # If df_plot is empty, make empty plot
    if len(df_plot)==0:
        fig = px.line(df_plot,
                      x='date',
                      y=col_plot)

    else:
        fig = px.line(df_plot,
                      x='date',
                      y=col_plot,
                      color='location')
    
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title=var)
    fig.update_layout(legend_title='Country',
                      height=300)

    return fig
    

def make_r_plot(countries):
    '''
    Make plot of disease contact rate (R)

    Parameters
    ----------
    countries : list of strings
        List of countries to plot

    Returns
    -------
    Plotly fig.

    '''


   
    # Filter df to only include list of countries provided
    df_plot = df_covid[df_covid['location'].isin(countries)]

    # If df_plot is empty, make empty plot
    if len(df_plot)==0:
        fig = px.line(df_plot,
                      x='date',
                      y='R')

    else:
        fig = px.line(df_plot,
                      x='date',
                      y='R',
                      color='location')
    
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='R')
    fig.update_layout(legend_title='Country',
                      height=300)

    return fig
    



#-----------------
# Generate figures
#-------------------


# Defualt values for simulation
def_countries = ['United States']
def_res = 'Daily'
def_scale = 'Raw'


# Make grid plot
fig_grid = make_grid_plot(def_countries, def_res, def_scale)


#--------------------
# App layout
#–-------------------


# Font sizes
size_slider_text = '15px'
size_title = '30px'

# Dropdown box options
opts_countries = [{'label':x, 'value':x} for x in list_countries]
opts_var = [{'label':x, 'value':x} for x in ['New cases','New deaths']]
opts_res = [{'label':x, 'value':x} for x in ['Daily','7 day average']]
opts_scale = [{'label':x, 'value':x} for x in ['Raw','Per million habitants']]


app.layout = html.Div([
      
    html.Div(
        html.H1('Analysis of Covid-19 trajectories',
                 style={'textAlign':'center',
                        'fontSize':size_title,
                        'color':'black'}
                )
        ),
    
    # Left half of app
 	html.Div([
      
        # Dropdown box for countries
        html.Label('Country',
                   style={'fontSize':14}
        ),         
        dcc.Dropdown(
            id='dropdown_countries',
            options=opts_countries,
            value=def_countries,
            multi=True,
            optionHeight=20,
        ),
        
        html.Br(),
      



        # Dropdown box for temporal resolution
        html.Label('Resolution',
                   style={'fontSize':14},
        ),         
        dcc.Dropdown(
            id='dropdown_res',
            options=opts_res,
            value=def_res,
            optionHeight=20,
            clearable=False,
        ),     
        
        
        html.Br(),
        
        
        # Dropdown box for scale
        html.Label('Scale',
                   style={'fontSize':14},
        ),         
        dcc.Dropdown(
            id='dropdown_scale',
            options=opts_scale,
            value=def_scale,
            optionHeight=20,
            clearable=False,
        )             
        
        
        
        
        ],       
		style={'width':'25%',
			   'height':'1000px',
			   'fontSize':'10px',
			   'padding-left':'5%',
			   'padding-right':'5%',
			   'padding-bottom':'0px',
                'padding-top':'40px',
			   'vertical-align': 'middle',
			   'display':'inline-block'},
        ),


 	# Trajectory figure
 	html.Div(
		[dcc.Graph(id='fig_grid',
 				   figure = fig_grid,
 				   # config={'displayModeBar': False},
 				   ),
 		 ],
		style={'width':'60%',
			   'height':'1000px',
			   'fontSize':'10px',
			   'padding-left':'0%',
			   'padding-right':'5%',
			   'vertical-align': 'middle',
			   'display':'inline-block'},
 	),



])



#–-------------------
# Callback functions
#–--------------------

# Update figures
@app.callback(
            
            Output('fig_grid','figure'),
            
            [
              Input('dropdown_countries','value'),
              Input('dropdown_res','value'),
              Input('dropdown_scale','value'),
            ],
            )

def update_figs(countries, res, scale):
    
    # Make figure of trajectories
    fig_grid = make_grid_plot(countries, res, scale)

    return fig_grid



# -----------------
# # Add the server clause
# #–-----------------

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='127.0.0.1',
        )

