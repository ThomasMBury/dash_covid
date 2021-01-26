#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 10:06:18 2020

Script to parse covid data obtained from
https://github.com/owid/covid-19-data/tree/master/public/data

Compute total infected using gamma distribution recovery and death

@author: tbury
"""


import numpy as np
import pandas as pd

import scipy.special as sp




def cdf_gamma(x, k, theta):
    '''
    Cumulative distribution function for the gamma distribution
    with shape k and scale theta

    '''
    return sp.gammainc(k, x/theta)

    
def prob_still_infected(T, k_r, theta_r, k_d, theta_d, delta):
    '''

    Function for probability that an individual is still infected T
    days after their onset.
    
    This is int_T^\infty p(x)dx, where p(x) is the pdf of the distribution
    

    Parameters
    ----------
    T : days after onset
    k_r : shape parameter for gamma distribution of individual who will recover
    theta_r : scale parameter for gamma distribution of individual who will recover
    k_d : shape parameter for gamma dist. of ind. who will die
    theta_d : scale parameter for gamma dist. of ind. who will die
    delta : infection fatility ratio

    Returns
    -------
    p : probability still infected

    '''
 
    # Probability a 'recovery individual' is still infected T days after onset
    p_rec = 1 - cdf_gamma(T, k_r, theta_r)

    # Probability a 'death individual' is still infected T days after onset
    p_death = 1 - cdf_gamma(T, k_d, theta_d)
    
    # Probability that any individual is still infected T days after onset
    p = delta*p_death + (1-delta)*p_rec
    
    return p


def compute_I(ar_cases, k_r, theta_r, k_d, theta_d, delta):
    '''
    
    Compute the total number infected in the population, given 
    the number of new cases on each day, and parameters for distributions
    of recovery/death times.

    Parameters
    ----------
    ar_cases: array of new cases on each day
    k_r : shape parameter for gamma distribution of individual who will recover
    theta_r : scale parameter for gamma distribution of individual who will recover
    k_d : shape parameter for gamma dist. of ind. who will die
    theta_d : scale parameter for gamma dist. of ind. who will die
    delta : infection fatility ratio

    Returns
    -------
    ar_I: array of total infected on each day

    '''

    # Compute gamma distribution values for 1000 days into future
    prob_values = np.array(
        [prob_still_infected(
            t,k_r,theta_r,k_d,theta_d,delta
            ) for t in np.arange(1000)])
    
    # Intialise array for total infections
    ar_I = np.zeros(len(ar_cases))

    # Do convolution between gamma dist. and number of cases
    for t in range(len(ar_cases)):
        # Compute total infected at this time
        i = np.dot(ar_cases[:t+1], prob_values[t::-1])
        ar_I[t] = i

    return ar_I



# Import covid data
cols = ['location','date','new_cases','new_deaths',
        'new_cases_per_million','new_deaths_per_million',
        'reproduction_rate','population']

# Import from github
print('Importing covid data from github')
url = 'https://github.com/owid/covid-19-data/raw/master/public/data/owid-covid-data.csv'
df_covid_raw = pd.read_csv(url,
                 usecols=cols,
                 )
print('Covid data imported')


# # Import locally
# df_covid_raw = pd.read_csv('data/owid-covid-data.csv',
#                        usecols=cols,)


# Sort by location
df_covid_raw.sort_values(['location','date'],inplace=True)

# Get 7-day rolling average for new cases and new deaths
df_covid_raw['new_cases_7dayAv'] = df_covid_raw.groupby('location').rolling(7)['new_cases'].mean().reset_index(0,drop=True)
df_covid_raw['new_deaths_7dayAv'] = df_covid_raw.groupby('location').rolling(7)['new_deaths'].mean().reset_index(0,drop=True)


#-------------
# Gamma distributions
#--------------

# Set gamma dist params for recovery (based on Verity et al.)
mean_r = 24.7
cv_r = 0.35
k_r = 1/(cv_r**2)
theta_r = mean_r/k_r


# Set gamma dist params for death (based on Verity et al.)
mean_d = 18.8
cv_d = 0.45
k_d = 1/(cv_d**2)
theta_d = mean_d/k_d


# Infection fataility rate
delta = 0.00657

# Mean infection time
inf_time_mean = mean_r*(1-delta) + mean_d*(delta)

# Loop through countries and compute R for each
list_df = []
list_countries = df_covid_raw['location'].unique()
for country in list_countries:
    df_temp = df_covid_raw[df_covid_raw['location']==country]
    # Get case data as an array (make Nan values 0)
    ar_cases = df_temp['new_cases'].fillna(0).values
    # Get total infection
    ar_I = compute_I(ar_cases,k_r,theta_r,k_d,theta_d,delta)
    # Put into df
    df_temp['I'] = ar_I
    # compute R
    df_temp['R'] = (df_temp['new_cases'].shift(-1)/df_temp['I'])*inf_time_mean
    df_temp['R_7dayAv'] = (df_temp['new_cases_7dayAv'].shift(-1)/df_temp['I'])*inf_time_mean
    list_df.append(df_temp)
    print('Compute R for country {}'.format(country))
    

df_covid = pd.concat(list_df)


# Export data
print('Exporting parsed covid data')
df_covid.to_csv('data/df_covid.csv')







