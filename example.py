import os
os.chdir("/home/jarekj/Dropbox/CODE/salbec")
from soilalbedo import soil, soilCurve
from diurnalalbedo import albedo 
from diurnalalbedo import batch_albedo_main_times
from soildatabase import soilDatabase
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import datetime


#%%
xerosol = soilSpectrum() # create soil object
xerosol.importFromFile("ASSETS/testing.xlsx") # import soil spectrum
model = soilModel() #create soil model object
model.fit(xerosol,1.99,39) # fits model to the spectrum
alb = albedo() n# create albedo object
alb.load_parameters(model,location=(17.2,50.1),errors = [2,3,5]) # load parameters: model, location and errors
alb.set_date_by_day(220) # set day of the analysis
record = alb.get_day_record(header=True) # get record with results
times = alb.get_diurnal_albedo() # get details

# images:
xerosol.drawSpectrum()
model.drawFitted()
alb.plot_time_curve("time_curve.pdf")

#%% import full abledo

