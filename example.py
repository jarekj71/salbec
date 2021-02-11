import os
os.chdir("/home/jarekj/Dropbox/CODE/salbec")
from soilalbedo import soil, soilCurve
from diurnalalbedo import albedo # nazwa do zmiany
from diurnalalbedo import batch_albedo_main_times
from soildatabase import soilDatabase
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import datetime



#%%

xerosol = soil()
xerosol.importFromFile("ASSETS/xerosol.xlsx")
xerosol.params

fig,ax = plt.subplots()
xerosol.drawSpectrum(ax) #Draw tghe spectrum on selected ax, zmiana dodać gca()
model = soilCurve() # zmiana nazwy na soilModel
model.fit(xerosol.a45,1.99,39) #zmiana API podać obiekt soil w całości
model.drawFitted() #Draw the fitted curve,
params = model.get_curve_model()

alb = albedo()
location=(17.2,50.1)
alb.load_parameters(params,location) # przekazać obiekt model w całości
alb.set_date_by_day(220)
alb.get_record(header=True) # zmiana nazwy, zmienić domyślnie header
alb.plot_time_curve("fig.pdf")

times = alb.times_DataFrame() # zmienić nazwę

# dodać batch dla całości

#%%

xerosol = soil()
xerosol.importFromFile("ASSETS/xerosol.xlsx")
model = soilModel()
model.fit(xerosol,1.99,39)
alb = albedo()
alb.load_parameters(model,location=(17.2,50.1),errors = [2,3,5])
alb.set_date_by_day(220)
record = alb.get_day_record(header=True)
times = alb.get_diurnal_albedo()

# images:
xerosol.drawSpectrum()
model.drawFitted()
alb.plot_time_curve("time_curve.pdf")


