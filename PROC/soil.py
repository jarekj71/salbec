#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 07:44:48 2020

@author: jarekj
"""
from scipy.interpolate import interp1d
from scipy.misc import derivative
from scipy.optimize import least_squares
import numpy as np
import matplotlib.pyplot as plt
import copy
#from io import StringIO będzie niezbędne przy rozbudowie


class soil():
    def __init__(self,spectrum=None):
        
        const = {}
        const['D574'] = -5795.4
        const['D1087'] = -510.24
        const['D1355'] = 7787.2
        const['D1656'] = 12181
        const['D698'] = 6932.8
        self.__const = const

        #s = open(spectrum).read().replace(',','.')
        #self.__data = np.loadtxt(StringIO(s),skiprows=1,delimiter=";")
        self.__data = spectrum
        
    @property
    def a45(self):    
        f = interp1d(self.__data[:,0],self.__data[:,1],kind="quadratic")
        
        self.__GL = self.__const['D574']*derivative(f,574,dx=10,n=2) + \
                 self.__const['D1087']*derivative(f,1087,dx=10,n=2) + \
                 self.__const['D1355']*derivative(f,1355,dx=10,n=2) + \
                 self.__const['D1656']*derivative(f,1656,dx=10,n=2) + \
                 self.__const['D698']*derivative(f,698,dx=10,n=2)
        
        return self.__GL

class soilCurve():
    def __init__(self):
        self.__x_test=np.concatenate((np.arange(0,90.),np.linspace(89,90,9)))
        self.reset_plot()
        self.__indexes = {k:v for v,k in enumerate('abcd')}
        self.__aTs = None
        self.__abcd = None
        
    def __recalc(self):
        self.a45 = 0.33 - 0.11 * self.T3D + self.GL
        sA = 6.26 * 7.41e-8 + 0.0043*pow(self.HSD,-1.418)
        Ts = np.arange(0,76)
        self.__aTs = self.a45*(1+sA*(Ts-45))
        
    @property
    def a45_stright(self):
        if self.__aTs is None:
            return None
        return self.__aTs[45]
    
    @property
    def a45_fitted(self):
        if self.__abcd is None:
            return
        return self.__aTS(self.__abcd,45)
    
    def __fit_aTS(self,x,Ts,y):
        return np.exp((x[0]+x[2]*Ts)/(1+x[1]*Ts+x[3]*Ts**2)) - y

    def __aTS(self,x,Ts):
        return np.exp((x[0]+x[2]*Ts)/(1+x[1]*Ts+x[3]*Ts**2))
    
    def reset_plot(self):
        self.models = []
        self.params = []
    
   
    def fit(self,GL,T3D,HSD,add=False):
        self.GL = GL
        self.T3D = T3D # usunąć selfy
        self.HSD = HSD
        self.__recalc()
        
        p2 = np.arange(15,76,1)
        p3 = np.array([90])
        x_train = np.concatenate((p2,p3))

        y2 = self.__aTs[p2]
        y3 = np.array([1])
        y_train = np.concatenate((y2,y3))
        
        

        x0 = np.array([-2.,-0.01,0.01,-1.0e-7]) # wartości początkowe mogą być trudne do ustawienia
        self.__res = least_squares(self.__fit_aTS,x0,args=(x_train,y_train))
        self.__reset_abcd = copy.copy(self.__res.x)
        self.__abcd = copy.copy(self.__res.x)
        if add:
            self.models.append(self.__res)
            self.params.append((self.T3D,self.HSD))
            

    def plot(self,ax=None,current=True):
        ax = ax or plt.gca()
        if current:
            p_x = np.array([0,10,20,45,65,75])
            p_y = self.__aTs[p_x]
            y_test = self.__aTS(self.__abcd,self.__x_test)
            label = "T3D: {}, HSD: {}".format(self.T3D,self.HSD)
            label +='\n'
            label += " a: {:0.3e}\n b: {:0.3e} \n c: {:0.3e} \n d: {:0.3e}".format(*self.__abcd)
            ax.scatter(p_x,p_y,s=10,c='#FA1121')
            ax.plot(self.__x_test,y_test,linewidth=2,label=label)
            
            ax.set_ylim((0,1))
            ax.legend(loc='upper left',fontsize='large')
        else:
            for model,params in zip(self.models,self.params):
                y_test = self.__aTS(model.x,self.__x_test)
                ax.plot(self.__x_test,y_test,linewidth=2,label="T3D: {}, HSD: {}".format(*params))
            ax.ylim((0,0.4))
            #plt.xlim((0,91))
            ax.legend(loc='upper left',fontsize='large')  
     
           

    def modify_curve_parameters(self,**kwargs):
        """
        

        Parameters
        ----------
        **kwargs : TYPE
            modyfikatory (0-1) dla poszczególnych parametrów 0 aby zresetować.

        Returns
        -------
        None.

        """
        for key in kwargs.keys():
            index = self.__indexes[key]
            self.__abcd[index] = self.__reset_abcd[index]*(1+kwargs[key])

     
    def get_curve_model(self):
        return self.__abcd
    
    def get_curve_params(self):
        curve_params = {}
        for key,index in self.__indexes.items():
            curve_params[key] = self.__abcd[index]
        return curve_params
 