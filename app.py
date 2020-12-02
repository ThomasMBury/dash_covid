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
df_covid = pd.read_csv('data/df_covid.csv')
list_countries = df_covid['location'].unique()

#------------
# functions
#-------------


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
    fig.update_layout(legend_title='Country')

    return fig
    


#-----------------
# Generate figures
#-------------------


# Defualt values for simulation
def_countries = ['United States']
def_var = 'New cases'
def_res = 'Daily'


# Make line plot of covid trajectories
fig_traj = make_traj_plot(def_countries, def_var, def_res)


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
      
        # Dropdown box for variable to plot
        html.Label('Variable',
                   style={'fontSize':14},
        ),         
        dcc.Dropdown(
            id='dropdown_var',
            options=opts_var,
            value=def_var,
            optionHeight=20,
            clearable=False,
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
        )     
        
        
        
        ],       
		style={'width':'30%',
			   'height':'500px',
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
		[dcc.Graph(id='fig_traj',
 				   figure = fig_traj,
 				   # config={'displayModeBar': False},
 				   ),
 		 ],
		style={'width':'55%',
			   'height':'500px',
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
            Output('fig_traj','figure'),
            [
              Input('dropdown_countries','value'),
              Input('dropdown_var','value'),    
              Input('dropdown_res','value'),           
            ],
            )

def update_figs(countries, var, res):
    
    # Make figure of trajectories
    fig_traj = make_traj_plot(countries, var, res)

    return fig_traj



#-----------------
# Add the server clause
#–-----------------

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='127.0.0.1',
        )

