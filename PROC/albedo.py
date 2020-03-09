#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:44:27 2020

@author: jarekj

"""
import datetime
import numpy as np
import pandas as pd
import astral
import pickle
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

class albedo:
    def __init__(self,step=1,year=None):
        self.__a = astral.Astral() 
        self.__sec_in_min = 60
        self.__step = step
        self.__year = datetime.datetime.today().year if year is None else year
        self.__current_date = self.today()
        self.__current_date_copy = self.__current_date
        self.__ax = None
    
    def load_parameters(self,soil_curve,location):
        self.__soil = soil_curve
        self.__location = location
    
    def store_current_date(self):
        self.__current_date_copy = self.__current_date
        
    def restore_current_date(self):
        self.__current_date = self.__current_date_copy
    
    def today(self):
        return datetime.datetime.today().date()
    
    def set_year(self,year):
        self.__year = year
    
    def set_date_by_day(self,day_of_the_year,year=None):
        if year is not None:
            self.__year = year
        self.__day_of_the_year = day_of_the_year
        self.__current_date = datetime.datetime(self.__year, 1, 1) + datetime.timedelta(self.__day_of_the_year- 1)
        self.__sun_time = self.__a.sun_utc(self.__current_date, *self.__location)
    
    def set_date_by_date(self,day,month,year=None):
        if year is None:
            year = self.__year
        self.__current_date = datetime.datetime(year,month,day)
        self.__sun_time = self.__a.sun_utc(self.__current_date, *self.__location)
    
    @property    
    def current_date(self):
        return self.__current_date
    
    def print_current_date(self):
        return str(self.__current_date)
    
    @property
    def day_of_year(self):
        return self.__current_date.timetuple().tm_yday
    
    @property
    def half_length_of_the_day(self):
        return self.__sun_time['sunset']-self.__sun_time['noon']
 
    
    def __angle(self,step,i):
        h = self.__sun_time['noon'] + datetime.timedelta(0,self.__sec_in_min*step*i)
        an = self.__a.solar_elevation(h, *self.__location)
        return 90-an

    def describe_day(self):
        return self.print_current_date(),self.__angle(self.__step,0),str(self.half_length_of_the_day), \
                str(self.__sun_time['sunrise'].time()),str(self.__sun_time['noon'].time()),str(self.__sun_time['sunset'].time())                           
   
  
    def batch_days(self,end_day):
        results = []
        self.store_current_date()
        current_day = self.day_of_year
        for day_of_the_year in range(current_day,current_day+end_day):
            results.append(self.describe_day())
        self.restore_current_date()
        return results
        
    def __aTS(self,X):
        return np.exp((self.__soil[0]+self.__soil[2]*X)/
                      (1+self.__soil[1]*X+self.__soil[3]*X**2))

    def get_mean_albedo(self):
        
        half_day = self.half_length_of_the_day
        n_steps = int(half_day.seconds/(self.__sec_in_min*self.__step))
        
        elevations = [self.__angle(self.__step,i) for i in range(n_steps)]
        elevations = elevations + [90]
        elevations = np.array(elevations)
        above = np.where((elevations>=0) &  (elevations <=90))[0]
        self.__elevations = elevations[above]
        self.__albedos = self.__aTS(self.__elevations)
        
        #pickle.dump((self.__elevations,self.__albedos),open("x.p","wb+"))
        return self.__albedos.mean()   
    
    
    
    def get_mean_albedo_local_time(self,value):
        below_value = np.where(self.__albedos<value)[0].max()
        start = below_value * self.__sec_in_min
        stop = below_value * self.__sec_in_min + self.__sec_in_min
        tune = [self.__angle(self.__step/60,i) for i in range(start,stop)]
        tune = np.array(tune)

        albedos_tune = self.__aTS(tune)
        below_value_tune = np.where(albedos_tune<value)[0].max()     
        local_time = datetime.timedelta(0,60*int(below_value)+int(below_value_tune))
        return local_time

    def get_mean_albedo_times(self,value,errors):

        #zmodyfikować nazwy tab
        utc_noon_time = self.__sun_time['noon']
        delta = self.get_mean_albedo_local_time(value)
        am_utc_time = utc_noon_time - delta
        pm_utc_time = utc_noon_time + delta
        
        noon_time = self.__current_date.replace(hour=12) #12:00
        am_local_time = noon_time-delta
        pm_local_time = noon_time+delta
        
        
        day = [self.day_of_year,am_utc_time.date()]
        utc_times=[am_utc_time.time(),pm_utc_time.time()]
        times = []
        values = []
        
        for error in errors[::-1]:
            val = value*(1+error)
            delta = self.get_mean_albedo_local_time(val)
            values.append(val)
            times+=[(noon_time-delta).time()]
        
        values.append(value)
        times+=[am_local_time.time()]
        
        for error in errors:
            val = value*(1-error)
            delta =  self.get_mean_albedo_local_time(val)    
            values.append(val)
            times+=[(noon_time-delta).time()]
                
        for error in errors[::-1]:
            val = value*(1-error)
            delta = self.get_mean_albedo_local_time(val)
            values.append(val)
            times+=[(noon_time+delta).time()]
        
        values.append(value)
        times+=[pm_local_time.time()]
        
        for error in errors:
            val = value*(1+error)
            values.append(val)
            delta =  self.get_mean_albedo_local_time(val)    
            times+=[(noon_time+delta).time()]

        return day,utc_times,times,values
    
    
    
    def batch_mean_albedo_time(self,start_day=1,end_day=366,interval=1,errors=[]):
        if len(errors) > 0:
            errors = tuple(i for i in errors if 0 <= i <=1)
        
        results = []
        colnames = []
        self.store_current_date()
        colnames += ['day','date','utm_am','utm_pm','local_am','local_pm']
        for error in errors:
            tmp_colnames = ['am_{}_l','am_{}_u','pm_{}_l','pm_{}_u']
            colnames +=[c.format(error) for c in tmp_colnames]
        colnames.append('mean_albedo')
        
        for day_of_year in range(start_day,end_day+1,interval):
            self.set_date_by_day(day_of_year)
            #print(self.describe_day())
            mean_albedo_value = self.get_mean_albedo()
            #print(mean_albedo_value)
            row = self.get_mean_albedo_times(day_of_year,mean_albedo_value,errors)
            results.append(row)
        self.restore_current_date()
        
        results = pd.DataFrame(results,columns=colnames)
        return results    
    
    def plot_curve(self,ax=None,day_of_year=1):
        ax = ax or plt.gta()
        self.store_current_date()
        self.set_date_by_day(day_of_year)

        mean_albedo_value = self.get_mean_albedo()
        
        x = np.concatenate((self.__elevations,np.flip(self.__elevations)[1:]))
        y = np.concatenate((np.flip(self.__albedos)[:-1],self.__albedos))
        pickle.dump((x,y),open("x.p","wb+"))
        ax.plot(y,linewidth=2)
        ax.axhline(y = mean_albedo_value,color='r',linestyle="--")
        self.restore_current_date()
        
    def plot_time_curve(self,figure=None,region_name=''):
                
        delta = datetime.timedelta(seconds=60)
        noon = self.__current_date.replace(hour=12)
        mean_albedo_value = self.get_mean_albedo()
        times_am = [(noon - n * delta).time() for n in range(len(self.__elevations))]
        times_pm = [(noon + n * delta).time() for n in range(len(self.__elevations))]
        times = times_am[::-1]+times_pm[1:]
        y = np.concatenate((np.flip(self.__albedos)[:-1],self.__albedos))
        #return times,y
        w = self.get_mean_albedo_times(mean_albedo_value,errors=[0.02,0.03,0.05])
        n = len(w[2])//2
        central = n//2

        error_colors = ['#B53ADB','#5769BF','#67C393']
        mean_color_V = '#007638'
        mean_color_H = '#C1CACF'
        curve_color = '#CC6600'
        span = 150
        
        fig = plt.figure(figsize=(8,8)) if type(figure) is str or figure is None else figure
        gs = gridspec.GridSpec(2, 2, figure=fig,wspace=0.1,hspace=0.4)
        
        #left
        ax0 = fig.add_subplot(gs[0,0])
        ax0.plot(times[0:span],y[0:span])
        tick_spacing=900
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        
        for h,er,erc in zip(w[2][:central],["5%","3%","2%"],error_colors):
            ax0.axvline(x = h,color=erc,linestyle="--",linewidth=1,label="error "+er)

        ax0.axvline(x = w[2][central],color=mean_color_V,linestyle="--",linewidth=2, label="mean albedo time")
        for h,erc in zip(w[2][central+1:n],error_colors[::-1]):
            ax0.axvline(x = h,color=erc,linestyle="--",linewidth=1)
        
        ax0.axhline(y = mean_albedo_value,color=mean_color_H,linestyle="--",alpha=0.5,label="mean albedo value")
        ax0.set_ylim(min(w[3])*0.9,max(w[3])*2)
        ax0.plot(times[0:span],y[0:span],color=curve_color)
        ax0.set_xlabel("Solar Local Time")
        ax0.set_ylabel("Albedo")
        ax0.set_title("Optimal a.m. time with errors")
        ax0.legend()
            
        #right
        ax1 = fig.add_subplot(gs[0,1])
        ax1.plot(times[-span:],y[-span:])
        ax1.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax1.yaxis.tick_right()
        ax1.axhline(y = mean_albedo_value,color=mean_color_H,linestyle="--",alpha=0.5)
        
        for h,er,erc in zip(w[2][n:n+central],["5%","3%","2%"],error_colors):
            ax1.axvline(x = h,color=erc,linestyle="--",linewidth=1,label="error "+er)
        
        ax1.axvline(x = w[2][n+central],color=mean_color_V,linestyle="--",linewidth=2, label="mean albedo time")
        for h,erc in zip(w[2][n+central+1:],error_colors[::-1]):
            ax1.axvline(x = h,color=erc,linestyle="--",linewidth=1)
        
        
        ax1.set_ylim(min(w[3])*0.9,max(w[3])*2)
        ax1.plot(times[-span:],y[-span:],color=curve_color)
        ax1.set_xlabel("Solar Local Time")
        ax1.set_title("Optimal p.m. time with errors")
        ax1.get_yaxis().set_visible(False)
        
        #down        
        axn = fig.add_subplot(gs[1,:])
        axn.plot(times,y,color=curve_color,linewidth=2)
        tick_spacing=3600
        axn.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        axn.set_xlim([datetime.time(0,0), datetime.time(23,59,59)])
        axn.axhline(y = mean_albedo_value,color=mean_color_H,linestyle="--",alpha=0.5)
        axn.axvline(x = w[2][central],color=mean_color_V,linestyle="--",linewidth=2)
        axn.axvline(x = w[2][n+central],color=mean_color_V,linestyle="--",linewidth=2)
        axn.set_title("Full day albedo change")
        axn.set_xlabel("Solar Local Time")
        
        for ax in fig.axes:
            plt.sca(ax) # aktywowanie axes
            plt.xticks(fontsize=8,rotation=45)
            plt.yticks(fontsize=8)
        plt.gcf().subplots_adjust(bottom=0.15)
        plt.suptitle("region: {}, day: {}".format(region_name,self.__day_of_the_year))
        
        if type(figure) is str:
            fig.savefig(figure)
        plt.close()
        
    