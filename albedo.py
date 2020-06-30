#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:44:27 2020

@author: jarekj

"""
import datetime
import numpy as np
import pandas as pd
from astral import sun 
from astral import Observer
import pickle
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def time_since_midnight(t):
    date = datetime. date(1, 1, 1)
    d1 = datetime. datetime. combine(date, t.min)
    d2 = datetime. datetime. combine(date, t)
    return d2 - d1


class albedo:
    def __init__(self,step=1,year=None):
        self.__a = sun 
        self.__sec_in_min = 60
        self.__step = step
        self.__year = datetime.datetime.today().year if year is None else year
        self.__current_date = datetime.datetime(self.__year, 1, 1)
        self.__noon_time = self.__current_date.replace(hour=12) #12:00
        #self.__noon_time = None
        self.__current_date_copy = self.__current_date
        self.__ax = None
        self.__errors = None
        self.__results_data = None
                
        self.__error_colors = ['#AF1E1E','#F2A62C','#F0F22C']
        self.__mean_color_V = '#00A203'
        self.__mean_color_H = '#C1CACF'
        self.__curve_color = '#CC6600'
    
    def load_parameters(self,soil_curve,location):
        self.__soil = soil_curve
        self.__location = Observer(*location)
    
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
        self.__noon_time = self.__current_date.replace(hour=12) #12:00
        self.__sun_time = self.__a.sun(self.__location,self.__current_date)
    
    def set_date_by_date(self,day,month,year=None):
        if year is None:
            year = self.__year
        self.__current_date = datetime.datetime(year,month,day)
        self.__sun_time = self.__a.sun(self.__location,self.__current_date)
        self.__noon_time = self.__current_date.replace(hour=12) #12:00
    
    
    @property
    def location(self):
        return self.__location
    
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
 
    @property
    def noon_time(self):
        return self.__noon_time
    
    def __angle(self,step,i):
        h = self.__sun_time['noon'] + datetime.timedelta(0,self.__sec_in_min*step*i)
        an = self.__a.elevation(self.__location,h)
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
   
    
    def get_mean_albedo_slt_time(self,value):
        if self.__albedos.min() >= value:
            return None
        below_value = np.where(self.__albedos<value)[0].max()
        start = below_value * self.__sec_in_min
        stop = below_value * self.__sec_in_min + self.__sec_in_min
        tune = [self.__angle(self.__step/60,i) for i in range(start,stop)]
        tune = np.array(tune)

        albedos_tune = self.__aTS(tune)
        below_value_tune = np.where(albedos_tune<value)[0].max()     
        local_time = datetime.timedelta(0,60*int(below_value)+int(below_value_tune))
        return local_time

    def _val_and_time(self,value,coef):
        delta = self.get_mean_albedo_slt_time(value)
        #noon_time = self.__current_date.replace(hour=12) #12:00
        if delta is None:
            return None,None
        else:
            return value,(self.noon_time+coef*delta).time()

    def get_albedo_max_error(self):
        mean_value = self.get_mean_albedo()
        min_value = self.__albedos.min()
        return (1-min_value/mean_value)*100
        

    def get_mean_albedo_times(self,value,errors):

        utc_noon_time = self.__sun_time['noon'].replace(microsecond=0)
        utc_sunrise_time = self.__sun_time['sunrise'].replace(microsecond=0)
        utc_sunset_time = self.__sun_time['sunset'].replace(microsecond=0)
        delta = self.get_mean_albedo_slt_time(value)
    
        utc_am_time = utc_noon_time - delta
        utc_pm_time = utc_noon_time + delta
       
        slt_am_time = self.noon_time-delta
        slt_pm_time = self.noon_time+delta
        
        slt_sunrise = self.noon_time - (utc_noon_time-utc_sunrise_time)
        slt_sunset = self.noon_time + (utc_sunset_time-utc_noon_time)
        
        day = [self.day_of_year,utc_am_time.date()]
        utc_times=[utc_sunrise_time.time(),
                   utc_am_time.time(),
                   utc_noon_time.time(),
                   utc_pm_time.time(),
                   utc_sunset_time.time()]

        
        times = []
        values = []
        
        values+=[1]
        times+=[slt_sunrise.time()]
        
        for error in errors[::-1]:
            val = value*(1+error)
            v = self._val_and_time(val,-1)
            values+=[v[0]]
            times+=[v[1]]
        
        values+=[value]
        times+=[slt_am_time.time()]

        for error in errors:
            val = value*(1-error)
            v = self._val_and_time(val,-1)
            values+=[v[0]]
            times+=[v[1]]            
       
        for error in errors[::-1]:
            val = value*(1-error)
            v = self._val_and_time(val,1)
            values+=[v[0]]
            times+=[v[1]]    
        
        values.append(value)
        times+=[slt_pm_time.time()]
        
        for error in errors:
            val = value*(1+error)
            v = self._val_and_time(val,1)
            values+=[v[0]]
            times+=[v[1]]    

        
        values+=[1]
        times+=[slt_sunset.time()]
        return day,utc_times,times,values
    
    def batch_mean_albedo_time(self,start_day=1,end_day=366,interval=1,errors=[]):
        if len(errors) > 0:
            errors = tuple(i for i in errors if 0 <= i <=1)
        
        results = []
        colnames = []
        self.store_current_date()
        colnames += ['day','date','mean_albedo','max_error']
        colnames += ["UTM_sunrise",'UTM_am_mat','UTM_noon','UTM_pm_mat','UTM_sunset']# mat - mean albedo time
        colnames +=['SLT_sunrise']
        for error in errors[::-1]:
            colnames +=['SLT_am-{}%'.format(round(error*100))]
        colnames += ['SLT_am_mat']
        for error in errors:    
            colnames +=['SLT_am+{}%'.format(round(error*100))]
        for error in errors[::-1]:
            colnames +=['SLT_pm-{}%'.format(round(error*100))]
        colnames += ['SLT_pm_mat']
        for error in errors:    
            colnames +=['SLT_pm+{}%'.format(round(error*100))]    
        colnames +=['SLT_sunset']
        
        for day_of_year in range(start_day,end_day+1,interval):
            self.set_date_by_day(day_of_year)
            mean_albedo_value = round(self.get_mean_albedo(),5)
            max_error = round(self.get_albedo_max_error(),5)
            w = self.get_mean_albedo_times(mean_albedo_value,errors)
            row = w[0]+[mean_albedo_value,max_error]+w[1]+w[2]
            results.append(row)

        self.restore_current_date()
        self.__results_data = pd.DataFrame(results,columns=colnames)

    
    def get_data(self):
        return self.__results_data
    
    def get_record(self,index):
        return None if self.__results_data is None else self.__results_data.iloc[index].copy()
        
    def plot_time_curve(self,figure=None,suptitle='',errors=[]):
                
        delta = datetime.timedelta(seconds=60)
        noon = self.noon_time
        mean_albedo_value = self.get_mean_albedo()
        times_am = [(noon - n * delta).time() for n in range(len(self.__elevations))]
        times_pm = [(noon + n * delta).time() for n in range(len(self.__elevations))]
        times = times_am[::-1]+times_pm[1:]
        y = np.concatenate((np.flip(self.__albedos)[:-1],self.__albedos))
        #return times,y

        w = self.get_mean_albedo_times(mean_albedo_value,errors=errors)
        w_times = w[2][1:-1] # remove sunset and sunrise
        w_values = w[3][1:-1]
        n = len(w_times)//2
        central = n//2

        error_colors = self.__error_colors
        mean_color_V = self.__mean_color_V
        mean_color_H = self.__mean_color_H
        curve_color = self.__curve_color
        span = 150
        
        fig = plt.figure(figsize=(8,8)) if type(figure) is str or figure is None else figure
        gs = gridspec.GridSpec(2, 2, figure=fig,wspace=0.1,hspace=0.4)
        #left
        ax0 = fig.add_subplot(gs[0,0])
        ax0.plot(times[0:span],y[0:span])
        tick_spacing=900
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        error_labels = [str(round(error*100,2))+'%' for error in errors[::-1]]
        
        for h,er,erc in zip(w_times[:central],error_labels,error_colors):
            ax0.axvline(x = h,color=erc,linestyle="--",linewidth=1,label="error "+er)

        ax0.axvline(x = w_times[central],color=mean_color_V,linestyle="--",linewidth=2, label="mean albedo time")
        for h,erc in zip(w_times[central+1:n],error_colors[::-1]):
            ax0.axvline(x = h,color=erc,linestyle="--",linewidth=1)
        
        ax0.axhline(y = mean_albedo_value,color=mean_color_H,linestyle="--",alpha=0.5,label="mean albedo value")
        ax0.set_ylim(min(w_values)*0.9,max(w_values)*2)
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
        
        for h,er,erc in zip(w_times[n:n+central],error_labels,error_colors):
            ax1.axvline(x = h,color=erc,linestyle="--",linewidth=1,label="error "+er)
        
        ax1.axvline(x = w_times[n+central],color=mean_color_V,linestyle="--",linewidth=2, label="mean albedo time")
        for h,erc in zip(w_times[n+central+1:],error_colors[::-1]):
            ax1.axvline(x = h,color=erc,linestyle="--",linewidth=1)
        
        ax1.set_ylim(min(w_values)*0.9,max(w_values)*2)
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
        axn.axvline(x = w_times[central],color=mean_color_V,linestyle="--",linewidth=2)
        axn.axvline(x = w_times[n+central],color=mean_color_V,linestyle="--",linewidth=2)
        axn.set_title("Full day albedo change")
        axn.set_xlabel("Solar Local Time")

        for ax in fig.axes:
            ax.tick_params(axis='x', labelrotation=45, labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
        plt.gcf().subplots_adjust(bottom=0.15)
        fig.suptitle("Soil: {}, day: {}".format(suptitle,self.__day_of_the_year))
        
        if type(figure) is str:
            fig.savefig(figure)
        plt.close()
       
    def plot_time_bar(self,figure=None,time=True,labels=False,errors=[]):
        #TODO: całość wymaga jeszcze weryfikacji
       
        mean_albedo_value = self.get_mean_albedo()
        w = self.get_mean_albedo_times(mean_albedo_value,errors=errors)
        n = len(w[2])//2
        error_colors = self.__error_colors
        mean_color_V = self.__mean_color_V
        times = w[2][:n]
        xticks = [time_since_midnight(t).total_seconds() for t in times]
        xmin = time_since_midnight(datetime.time(2,0,0)).total_seconds()
        xmax = time_since_midnight(datetime.time(10,0,0)).total_seconds()
        trange = xmax-xmin
        regular_xticks = np.linspace(xmin,xmax,9)
        ticks = xticks if time is True else regular_xticks
        #TODO: Dodać wschód i zachód słońca
        #return (ticks,labels)
        fig = plt.figure(figsize=(8,0.4)) if type(figure) is str or figure is None else figure
        ax = fig.add_subplot(111)
        ax.scatter(times,np.repeat(1,n),zorder=3,c=error_colors+[mean_color_V]+error_colors[::-1],s=80)
        m1=(xticks[0]-xmin)/trange
        m2=(xticks[-1]-xmin)/trange
        ax.axhline(y=1,c='#AAAAAA',lw=0.5,zorder=1,ls='--')
        ax.axhline(y=1,xmin=m1,xmax=m2,c='#446683',lw=4,zorder=2)

        plt.xticks(rotation=90)
        ax.get_yaxis().set_visible(False)
        ax.spines['bottom'].set_color(None)
        ax.spines['left'].set_color(None)
        ax.spines['right'].set_color(None)
        ax.spines['top'].set_color(None)
        ax.set_xlabel(None)
        ax.grid(alpha=0.5,ls='--')
        ax.set_xlim(xmin,xmax)
        ax.set_xticks(ticks)
        if not labels:
            ax.set_xticklabels([])


        
        
