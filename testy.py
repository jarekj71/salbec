#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 10:18:24 2023

@author: jarekj
"""

#%%
import os
os.chdir(os.path.dirname(__file__))
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

#%%
from soilalbedo import soilSpectrum, soilModel
xerosol = soilSpectrum() # create soil object
xerosol.importFromFile("ASSETS/EU_Bd1_NO.xlsx") 
model = soilModel() #create soil model object
model.fit(xerosol.spectra,1.05,25) # fits model to the spectrum with t3d 1.99 and hsd = 39

#%%
from diurnalalbedo import albedo 
alb = albedo() # create albedo object
longitude = 0
alb.load_parameters(model.get_model_coefs(),location=(longitude,10.9),errors = [0.02,0.03,0.05]) # load parameters: model, location and errors

#%%
d=1
alb.set_date_by_day(d)
angle = alb._elevations
albed = alb._albedos
n_seconds = alb.half_length_of_the_day.seconds

#%%

alb = albedo() # create albedo object
longitude = 62
alb.load_parameters(model.get_model_coefs(),location=(longitude,10.9),errors = [0.02,0.03,0.05]) # load parameters: model, location and errors


dates = [(6,1),(15,2),(21,3),(5,5),(21,6),(1,8),(21,9),(1,11),(21,12)]


ang_color = 'tab:blue'
alb_color = 'tab:green'
alpha=0.1

angles = []
albeds = []
for day in dates:
    alb.set_date_by_date(*day)
    angles.append(np.flip(alb._elevations))
    albeds.append(np.flip(alb._albedos))
#%%

fig,axes = plt.subplots(ncols=2,nrows=len(dates),figsize=(12,20))

for date,angle1,albed1,ax in zip(dates,angles,albeds,axes):
    
    for angle,albed in zip(angles,albeds):

        ax[0].plot(angle,color=ang_color,alpha=alpha)
        ax[0].invert_xaxis()
        ax[0].set_title("Angle {}/{}".format(*date))
        
        ax[1].plot(albed,color=alb_color,alpha=alpha)
        ax[1].invert_xaxis()
        ax[1].set_title("Albedo {}/{}".format(*date))
    ax[0].plot(angle1,color=ang_color,alpha=1,lw=2)
    ax[1].plot(albed1,color=ang_color,alpha=1,lw=2)

ax[0].set_xlabel("Seconds from Sunset")
ax[1].set_xlabel("Seconds from Sunset")

fig.suptitle("{:2f} degrees".format(longitude))
fig.tight_layout()
fig.savefig("deg_{:0f}.pdf".format(longitude))
#%%




#    ax1_twin = ax1.twinx()
#    ax1_twin.plot(albed,color=alb_color,alpha=alpha)

    ax2.plot(angle,color=ang_color,alpha=alpha)
#    ax2_twin = ax2.twinx()
#    ax2_twin.plot(albed,color=alb_color,alpha=alpha)

#ax1.set_ylim(38,91)
#ax1_twin.set_ylim(0,1)

ax2.set_ylim(88,90.05)
ax2.set_xlim(0,1000)
#ax2_twin.set_ylim(0,1)


#%%
results = []
for d in range(1,365,15):
    alb.set_date_by_day(d) # set day of the analysis
    alb.get_mean_albedo()
    v = (alb._albedos>0.3)
    results.append((d,len(v),v.sum()))

#%%
df = pd.DataFrame(results,columns=["day","n_sec","n_sec_030"])
df.to_excel("seconds2.xlsx")

#%%
record = alb.get_day_record(header=True) # get record with results
times = alb.get_diurnal_albedo() # get details as data frame

#%%

w = alb.get_albedo_main_times()
alb.plot_time_curve("time_curve.pdf")


alb._errors
#%%
w_times = w[2][1:-1][0] # remove sunset and sunrise
fig,ax= plt.subplots()
ax.plot(x,y)
ax.axvline(x = w_times,color='r',linestyle="--",linewidth=1,label="error ")
#%%

#w_values = w[3][1:-1]

w
#%%
