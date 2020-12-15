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

import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app_functions import make_grid_plot, make_r_d_scatter


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


#-----------------
# Generate figures
#-------------------

# Defualt values for simulation
def_countries = ['United States']
def_res = 'Daily'
def_scale = 'Raw'
def_ndays = 30
def_delay = 0
def_start_date = '2020-03-01'

# Make grid plot
fig_grid = make_grid_plot(df_covid, def_countries, def_res, def_scale)

# Make r vs deaths scatter plot
fig_scatter = make_r_d_scatter(df_covid, def_countries, 
                               n_days=def_ndays, 
                               scale=def_scale)


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
opts_scale = [{'label':x, 'value':x} for x in ['Raw','Per million habitants','Max value']]

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
        ),     
        
    
        
        ],       
		style={'width':'25%',
			   'height':'700px',
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
			   'height':'700px',
			   'fontSize':'10px',
			   'padding-left':'0%',
			   'padding-right':'5%',
			   'vertical-align': 'middle',
			   'display':'inline-block'},
 	),
     
    html.Div(
         [
     
         html.Br(),

         # Slider for ndays
		 html.Label('Number of days included in death count = {}'.format(def_ndays),
 				   id='slider_ndays_text',
 				   style={'fontSize':14}),    
         
         dcc.Slider(
            id='slider_ndays',
            value=def_ndays,
            min=5,
            max=50,
            step=1,
         ),
         
         html.Br(),

         # Slider for delay
		 html.Label('Delay = {}'.format(def_delay),
 				   id='slider_delay_text',
 				   style={'fontSize':14}),    
         
         dcc.Slider(
            id='slider_delay',
            value=def_delay,
            min=0,
            max=20,
            step=1,
         ),         
         
         html.Br(),


         # Start time date picker
		 html.Label('Start date = {}'.format(def_start_date),
 				   id='date_picker_text',
 				   style={'fontSize':14}),
         
         dcc.DatePickerSingle(
              id='date_picker',
              min_date_allowed = datetime.date(2020, 1, 1),
              max_date_allowed = datetime.date(2021, 1, 1),
              initial_visible_month = datetime.date(2020, 1, 1),
              date = datetime.date(2020, 3, 1)
          ),
         
          ],
         
		style={'width':'25%',
			   'height':'400px',
			   'fontSize':'10px',
			   'padding-left':'5%',
			   'padding-right':'5%',
			   'padding-bottom':'0px',
               'padding-top':'40px',
			   'vertical-align': 'middle',
			   'display':'inline-block'},  
     ),
     
 	# Scatter plot
 	html.Div(
		[dcc.Graph(id='fig_scatter',
 				   figure = fig_scatter,
 				   # config={'displayModeBar': False},
 				   ),
 		 ],
		style={'width':'60%',
			   'height':'400px',
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
            [
            Output('fig_grid','figure'),
            Output('fig_scatter','figure'),
            Output('slider_ndays_text','children'),
            Output('slider_delay_text','children'),
            Output('date_picker_text','children'),
            ],
            
            [
              Input('dropdown_countries','value'),
              Input('dropdown_res','value'),
              Input('dropdown_scale','value'),
              Input('slider_ndays','value'),
              Input('slider_delay','value'),
              Input('date_picker','date'),
            ],
            
            )

def update_figs(countries, res, scale, n_days, delay, date_value):
    
    # Make figure of trajectories
    fig_grid = make_grid_plot(df_covid, countries, res, scale)
    
    # Convert start time to string of from y-m-d
    date_object = datetime.date.fromisoformat(date_value)
    date_string = date_object.strftime('%Y-%m-%d')
    
    # Make scatter plot
    fig_scatter = make_r_d_scatter(df_covid, countries, 
                                   n_days=n_days,
                                   scale=scale,
                                   delay=delay,
                                   start_date=date_string)

    slider_ndays_text = 'Number of days = {}'.format(n_days)
    slider_delay_text = 'Delay = {}'.format(delay)
    date_picker_text = 'Start date = {}'.format(date_string)


    return fig_grid, fig_scatter, slider_ndays_text, slider_delay_text, date_picker_text



# -----------------
# # Add the server clause
# #–-----------------

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='127.0.0.1',
        )

