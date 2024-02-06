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
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import pickle

#%%
from soilalbedo import soilSpectrum, soilModel
xerosol = soilSpectrum() # create soil object
xerosol.importFromFile("ASSETS/EU_Bd1_NO.xlsx") 
model = soilModel() #create soil model object
model.fit(xerosol.spectra,1.05,25) # fits model to the spectrum with t3d 1.99 and hsd = 39

#%%
from diurnalalbedo import albedo 
alb = albedo() # create albedo object
longitude = 10.68
alb.load_parameters(model.get_model_coefs(),location=(longitude,29.61),errors = [0.02,0.03,0.05]) # load parameters: model, location and errors

#%%
d=1
alb.set_date_by_day(d)
thetimes = alb.get_albedo_main_times()
alb.plot_time_curve()


#%%
slt = thetimes[2]
alb._albedos['morning']
alb._albedos['afternoon']
x = int(alb.am_half_length_of_the_day.seconds/60)
angle = alb._elevations
albed = alb._albedos
alb.morning_half_length_of_the_day.seconds
alb.afternoon_half_length_of_the_day.seconds
alb.full_length_of_the_day.seconds
alb.get_mean_albedo()


noon = alb._utm_time['noon']
am = noon+alb._mtd
pm = noon+alb._atd
#%%

lst = [1,2,3,4,5]

p = lst[::-1]+lst

#%%

np.arange(-10)

wh = np.where(albed<0.26)[0]

np.flatnonzero(np.array([1,9,2,2,2,2,1,5,6,6])>4)




atd,mtd = alb.get_albedo_time_delta(0.26)
noon = alb._utm_time['noon']
sunrise = alb._utm_time['sunrise']
sunset = alb._utm_time['sunset']
am = noon-atd
pm = noon+mtd
#%%
alb = albedo() # create albedo object
longitude = 10.68

latitudes = pd.read_csv("szerokosci.csv")
#%%

databases  =[]
for latitude in latitudes.lat.values:
    alb.load_parameters(model.get_model_coefs(),location=(latitude,longitude),errors = [0.02,0.03,0.05]) # load parameters: model, location and errors
    print(latitude)

    mean_albedos = []
    min_albedos = []
    angles = []
    second = []


    for i in range(1,366):
        alb.set_date_by_day(i)
        mean_albedos.append(alb.get_mean_albedo())
        min_albedos.append(alb.get_min_albedo())
        angles.append(alb._angle(0))
        second.append(alb.full_length_of_the_day)
    
    database = pd.DataFrame(np.array([mean_albedos,min_albedos,angles,second]).T,columns=["mean","min","angle","second"],index=range(1,366))
    databases.append(database)

pickle.dump(databases,open("databases.p","wb+"))
#%%

fig,axes = plt.subplots(5,2,figsize=(15,15))

for i,ax in enumerate(axes.T.flatten()):
    database = databases[i+8]
    ax.plot(database.angle,c="tab:green",lw=3)
    ax_tween = ax.twinx()
    ax_tween.plot(database['mean'],c="tab:orange",lw=3)
    ax.set_title(latitudes.lat.values[i+8])

fig.savefig("przebiegi.pdf")
#%%

day_172 = pd.DataFrame(columns=database.columns)
for database, lat in zip(databases,latitudes.lat.values):
    day_172.loc[lat] = database.loc[172]
    

day_173 = pd.DataFrame(columns=database.columns)
for database, lat in zip(databases,latitudes.lat.values):
    day_173.loc[lat] = database.loc[173]

day_355 = pd.DataFrame(columns=database.columns)
for database, lat in zip(databases,latitudes.lat.values):
    day_355.loc[lat] = database.loc[355]
    

day_356 = pd.DataFrame(columns=database.columns)
for database, lat in zip(databases,latitudes.lat.values):
    day_356.loc[lat] = database.loc[356]


day_172.to_excel("d172.xlsx")
day_173.to_excel("d173.xlsx")
day_355.to_excel("d355.xlsx")
day_356.to_excel("d356.xlsx")


#%%
#ddays = pd.DataFrame(columns=["angle"])
databases=pickle.load(open("databases.p","rb"))
longitude = 10.68
latitudes = pd.read_csv("szerokosci.csv")

#%%
for database,lat in zip(databases,latitudes.lat.values):
    print(database.sort_values("angle",ascending=False)[:2])


#%%

plt.plot(databases[10].angle)

################################################################################
#%%
mean_albedo = alb.get_mean_albedo()

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
