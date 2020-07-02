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
import pickle, os
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
        self._a = sun #module sun
        self._sec_in_min = 60
        self._step = step
        self._year = datetime.datetime.today().year if year is None else year
        self._current_date = datetime.datetime(self._year, 1, 1)
        self.colnames = None
        self._twelve_noon = self._current_date.replace(hour=12) #12:00

        self._ax = None
        self._errors = []
        self._utm_time = None
        self._slt_time = {}
        self._agregated_values = None
                
        self._error_colors = ['#AF1E1E','#FA861E','#F2A62C','#F0F22C']
        self._mean_color_V = '#00A203'
        self._mean_color_H = '#C1CACF'
        self._curve_color = '#CC6600'
    
    def load_parameters(self,soil_curve,location,errors=[]):
        self._soil = soil_curve
        self._location = Observer(*location)
    
        if len(errors) > 0:
            errors = tuple(i for i in errors if 0 <= i <=1)
        self._errors = errors

        colnames = []
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
        self.colnames = colnames
    
    def set_year(self,year):
        self._year = year
    
    def set_date_by_day(self,day_of_the_year,year=None):
        if year is not None:
            self._year = year
        self._day_of_the_year = day_of_the_year
        self._current_date = datetime.datetime(self._year, 1, 1) + datetime.timedelta(self._day_of_the_year- 1)
        self._calculate_day()
    
    def set_date_by_date(self,day,month,year=None):
        if year is None:
            year = self._year
        self._current_date = datetime.datetime(year,month,day)
        self._day_of_the_year = self._current_date.timetuple().tm_yday
        self._calculate_day()
        
    @property
    def errors(self):
        return self._errors
    
    @property
    def location(self):
        return self._location
    
    @property    
    def date(self):
        return self._current_date
    
    def print_current_date(self):
        return str(self._current_date)
    
    @property
    def day_of_year(self):
        return self._day_of_the_year
    
    @property
    def half_length_of_the_day(self):
        return self._utm_time['sunset']-self._utm_time['noon']
 
    @property
    def slt_noon_time(self):
        return self._twelve_noon
    
    def _angle(self,step,i):
        h = self._utm_time['noon'] + datetime.timedelta(0,self._sec_in_min*step*i)
        an = self._a.elevation(self._location,h)
        return 90-an
        
    def _aTS(self,X): #albedo curve
        return np.exp((self._soil[0]+self._soil[2]*X)/
                      (1+self._soil[1]*X+self._soil[3]*X**2))

    def _calculate_day(self):
        self._utm_time = self._a.sun(self._location,self._current_date)
        self._twelve_noon = self._current_date.replace(hour=12) #12:00
        half_day = self.half_length_of_the_day
        n_steps = int(half_day.seconds/(self._sec_in_min*self._step))
        
        elevations = [self._angle(self._step,i) for i in range(n_steps)]
        elevations = elevations + [90]
        elevations = np.array(elevations)
        above = np.where((elevations>=0) &  (elevations <=90))[0]
        self._elevations = elevations[above]
        self._albedos = self._aTS(self._elevations)
        
        self._utm_time['noon'] = self._utm_time['noon'].replace(microsecond=0)
        self._utm_time['sunrise'] = self._utm_time['sunrise'].replace(microsecond=0)
        self._utm_time['sunset'] = self._utm_time['sunset'].replace(microsecond=0)
        
        self._slt_time['noon'] = self._twelve_noon
        self._slt_time['sunrise']  = self._slt_time['noon'] - (self._utm_time['noon'] - self._utm_time['sunrise'])
        self._slt_time['sunset']  = self._slt_time['noon'] + (self._utm_time['sunset'] - self._utm_time['noon'])
    
    def describe_day(self):
        return self.print_current_date(),self._angle(self._step,0),str(self.half_length_of_the_day), \
            self._utm_time['sunrise'].strftime("%H:%M:%S"), \
            self._utm_time['noon'].strftime("%H:%M:%S"), \
            self._utm_time['sunset'].strftime("%H:%M:%S")                           

    def get_mean_albedo(self):
        return self._albedos.mean()   

    def get_albedo_max_error(self):
        mean_value = self.get_mean_albedo()
        min_value = self._albedos.min()
        return (1-min_value/mean_value)*100    
    
    def get_mean_albedo_time_delta(self,value):
        if self._albedos.min() >= value:
            return None
        below_value = np.where(self._albedos<value)[0].max()
        start = below_value * self._sec_in_min
        stop = below_value * self._sec_in_min + self._sec_in_min
        tune = [self._angle(self._step/60,i) for i in range(start,stop)]
        tune = np.array(tune)

        albedos_tune = self._aTS(tune)
        below_value_tune = np.where(albedos_tune<value)[0].max()     
        local_time = datetime.timedelta(0,60*int(below_value)+int(below_value_tune))
        return local_time

    def _val_and_time(self,value,coef):
        delta = self.get_mean_albedo_time_delta(value)
        if delta is None:
            return None,None
        else:
            return value,(self._twelve_noon+coef*delta).time()
        

    def get_albedo_main_times(self):
        value = self.get_mean_albedo()
        delta = self.get_mean_albedo_time_delta(value)
    
        utm_am_time = self._utm_time['noon'] - delta
        utm_pm_time = self._utm_time['noon'] + delta
        slt_am_time = self._slt_time['noon'] - delta
        slt_pm_time = self._slt_time['noon'] + delta
      
        day = [self.day_of_year,utm_am_time.date()]
        utm_times=[self._utm_time['sunrise'].time(),
                   utm_am_time.time(),
                   self._utm_time['noon'].time(),
                   utm_pm_time.time(),
                   self._utm_time['sunset'].time()]
        
        times = []
        values = []
        
        values+=[1]
        times+=[self._slt_time['sunrise'].time()]
        
        errors = self._errors
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
        times+=[self._slt_time['sunset'].time()]
        return day,utm_times,times,values

        
    def _get_times_day_serie(self, UTM = False):
        delta_step = datetime.timedelta(seconds=self._sec_in_min)
        noon = self._utm_time['noon'] if UTM else self._slt_time['noon']
        times_am = [(noon - n * delta_step).time() for n in range(len(self._elevations))]
        times_pm = [(noon + n * delta_step).time() for n in range(len(self._elevations))]
        times = times_am[::-1]+times_pm[1:]
        return times
    
    def _get_albedos_day_serie(self):
        return  np.concatenate((np.flip(self._albedos)[:-1],self._albedos))
          
    def _get_elevations_day_serie(self):
        return np.concatenate((np.flip(self._elevations)[:-1],self._elevations))
    
    def _aggregate(self):
        aggregate = {} 
        aggregate['tSLT'] = self._get_times_day_serie(UTM=False)
        aggregate['tUTM'] = self._get_times_day_serie(UTM=True)
        aggregate['albedo'] = self._get_albedos_day_serie()
        aggregate['elevtions'] = self._get_elevations_day_serie()

        aggregate['utc_sunrise_time'] = self._utm_time['sunrise']
        aggregate['utc_sunset_time'] = self._utm_time['sunset']
        aggregate['utc_noon_time'] = self._utm_time['noon']

        aggregate['slt_sunrise_time'] = self._slt_time['sunrise']
        aggregate['slt_sunset_time'] = self._slt_time['sunset']
        self._agregated_values = aggregate

        
    def time_slider(self):
        self._aggregate()
        return self._agregated_values
    
    def times_DataFrame(self):
        if self._agregated_values is None:
            self._aggregate()
        
        a = self._agregated_values
        colnames = ["UTM","SLT","albedo","sun_elev"]
        df = pd.DataFrame(dict(zip(colnames,[a["tUTM"],a["tSLT"],a["albedo"],a['elevtions']])))
        self._agregated_values = None
        return df
    
    def get_record(self,header=False):
        w = self.get_albedo_main_times()
        mean_albedo = round(self.get_mean_albedo(),5)
        max_error = round(self.get_albedo_max_error(),5)
        record = w[0]+[mean_albedo,max_error]+w[1]+w[2]
        if header:
            return pd.Series(record,index=self.colnames)
        else:
            return record
    
    def plot_time_curve(self,figure=None,suptitle=''):
        mean_albedo_value = self.get_mean_albedo()
        errors = self._errors
        times =self._get_times_day_serie()
        y = self._get_albedos_day_serie()
        w = self.get_albedo_main_times()

        w_times = w[2][1:-1] # remove sunset and sunrise
        w_values = w[3][1:-1]
        n = len(w_times)//2
        central = n//2

        error_colors = self._error_colors
        mean_color_V = self._mean_color_V
        mean_color_H = self._mean_color_H
        curve_color = self._curve_color
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
        fig.suptitle("Soil: {}, day: {}".format(suptitle,self._day_of_the_year))
        
        if type(figure) is str:
            fig.savefig(figure)
        plt.close()
       
    def plot_time_bar(self,figure=None,time=True,labels=False,errors=[]):
        #TODO: całość wymaga jeszcze weryfikacji
       
        mean_albedo_value = self.get_mean_albedo()
        w = self.get_albedo_main_times(mean_albedo_value,errors=errors)
        n = len(w[2])//2
        error_colors = self._error_colors
        mean_color_V = self._mean_color_V
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
        
 
def batch_day_description(albedo,start_day=1,end_day=355,ndays=None):
    
    if ndays is not None:
        end_day = start_day+ndays
    results = []
    for day_of_the_year in range(start_day,end_day):
        albedo.set_date_by_day(day_of_the_year)
        results.append(albedo.describe_day())
    return results        


def batch_albedo_main_times(albedo,start_day=1,end_day=365,interval=1):

    results = []
    for day_of_year in range(start_day,end_day+1,interval):
        albedo.set_date_by_day(day_of_year)
        record = albedo.get_record()
        results.append(record)
    return pd.DataFrame(results,columns=albedo.colnames)
