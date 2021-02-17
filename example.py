import os
os.chdir(os.path.dirname(__file__)) # if run from the salbec directory
from soilalbedo import soilSpectrum, soilModel
from diurnalalbedo import albedo 


#%%
xerosol = soilSpectrum() # create soil object
xerosol.importFromFile("ASSETS/testing.xlsx") # import soil spectrum
model = soilModel() #create soil model object
model.fit(xerosol.spectra,1.99,39) # fits model to the spectrum with t3d 1.99 and hsd = 39
alb = albedo() # create albedo object
alb.load_parameters(model,location=(17.2,50.1),errors = [2,3,5]) # load parameters: model, location and errors
alb.set_date_by_day(220) # set day of the analysis
record = alb.get_day_record(header=True) # get record with results
times = alb.get_diurnal_albedo() # get details as data frame

# images:
xerosol.drawSpectrum()
model.drawFitted()
alb.plot_time_curve("time_curve.pdf")


