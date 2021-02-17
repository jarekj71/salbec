#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 07:44:48 2020

@author: jarekj
"""
from typing import Sequence, Union
from scipy.interpolate import interp1d
from scipy.misc import derivative
from scipy.optimize import least_squares
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import copy, os, pickle
from soildatabase import soilDatabase

def read_csv(fileName: str) -> pd.DataFrame:
    """Read csv (comma sepparated) and csv2 (semicolon separated)


    Args:
        fileName (str): Name of csv file

    Returns:
        pd.DataFrame: Data formated as pandas data frame
    """
    sep = ","
    dec = "."
    with open(fileName) as cc:
        z =cc.readline()
        cc.close()
        if ";" in z and "," in z: 
            sep = ";"
            dec = ","
    tmp = pd.read_csv(fileName,header=None,sep=sep,decimal=dec)
    return tmp

class soilSpectrum():
    def __init__(self):
        """set coefficient of soil
        """
        self._const = {}
        self._const[574] = -5795.4
        self._const[1087] = -510.24
        self._const[1355] = 7787.2
        self._const[1656] = 12161
        self._const[698] = 6932.8
        self.soilName = None
        self.coordinates = None

    def importFromFile(self,fileName: str) -> None:
        """import either csv and xls/xlsx files

        Args:
            fileName (str): csv/csv2 or xls/xlsx file
        """
        
        if not os.path.isfile(fileName):
            return "Wrong file name or file path",None

        _,ext = os.path.splitext(fileName)
        self.soilName = None
        self.coordinates = None
        if ext in ['.xlsx','.xls']:
            _e = pd.read_excel(fileName,nrows=0)
            if _e.columns.values[0] == "symbol" and type(_e.columns.values[1]) is str:
                coords = pd.read_excel(fileName,nrows=2,index_col="symbol")
                spectra = pd.read_excel(fileName,skiprows=[1,2])
                self.soilName = coords.columns.values[0]
                self.coordinates = coords[self.soilName].values
            else:
                spectra = pd.read_excel(fileName,header=None)
        elif ext == '.csv':
            spectra = read_csv(fileName)
        else:
            return "Unrecognised file type",None
        
        if len(spectra.columns) != 2:
            return "Wrong number of columns in data","Only two columns, one with wavelength, second with reflectance are allowed"
            
        wavelengths = spectra.iloc[:,0].values
        if wavelengths[0] != 350:
            return "Incorrect first column","Wavelength values must be between 350 and 2500"
        
        reflectance = spectra.iloc[:,1].values
        if reflectance.min() <0 or reflectance.max() >1:
            return "Incorrect second column","Reflectance values must be between 0 and 1"
        
        self.importSeries(wavelengths,reflectance)
    
    def importSeries(self,wavelengths: np.ndarray,reflectance: np.ndarray):
        """import data already formatted as numpy nd array

        Args:
            wavelengths (np.ndarray): wavelengths 1D ndarray values between 350 and 2500
            reflectance (np.ndarray): reflectance value values between 0 and 1

        """
        self._wavelengths = wavelengths
        self._reflectance = reflectance
        self._f = interp1d(self._wavelengths,self._reflectance,kind="quadratic")
        self._gl = {}
        for key,value in self._const.items():
            self._gl[key] = value*derivative(self._f,key,dx=10,n=2)

        return None

    
    @property
    def spectra(self):    
        spectra = sum(self._gl.values())
        return spectra

    @property
    def params(self):
        return self._gl
    
    @property
    def coefs(self):
        return self._const
    
    @property
    def interp(self):
        return self._f
    
    def exportSoil(self,name:str,lat:float=None,lon:float=None) -> dict:
        """export soil dict formatted to be used with soil database
            - name - name
            - coords-  = (lat,lon)
            - reflectance - original values of reflectance measured at given wavelength(0-1)
            - wavelengths - = original values of wavelengths, ussualy between 350 and 2500, in nm
            - params - = second derivatives at given wavelength
            - a45 - = spectral part of A45 (without constant and T3D compoentent)

        Args:
            name (str): name of soil/location
            lat (float, optional): latitude  of soil sample. Defaults to None.
            lon (float, optional): longitude of soil sample. Defaults to None.

        Returns:
            dict: structure (dict containg soil description)
        """
        soil = {}
        soil['name'] = name
        soil['coords'] = (lat,lon)
        soil['reflectance'] = self._reflectance
        soil['wavelengths'] = self._wavelengths
        soil['params'] = self._gl
        soil['spectra'] = self.spectra
        return soil
    
    def importFromDatabase(self,soil:dict) -> tuple:
        """import soil dict formatted from the database

        Args:
            soil (dict): soil dictionary

        Returns:
            tuple: name and soil sample coordinates
        """
        lat,lon = soil['coords']
        name = soil['name']
        self._reflectance = soil['reflectance']
        self._wavelengths = soil['wavelengths']
        self._gl = soil['params']
        self._f = interp1d(self._wavelengths,self._reflectance,kind="quadratic")    
        return name,lat,lon
    

    def drawSpectrum(self,ax:plt.Axes=None,lines:bool=True,title:str=None) -> None:
        """plot spectrum on given Axes. Axes must be created before method call

        Args:
            ax (plt.Axes): Axes to plot spectrum
            lines (bool, optional): Plot lines of important wavelengths. Defaults to True.
            title (str, optional): Custom title, None to keep default. Defaults to None.
        """
        ax = ax or plt.gca()
        ax.plot(self._wavelengths,self._reflectance)
        ax.set_ylabel("Reflectance")
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylim(0,0.7)
        if lines:
            ax.vlines(self._gl.keys(),ymin=0,ymax=0.7,colors='#8298A8',ls='--')
            ax2 = ax.twiny()
            ax2.set_xlim(*ax.get_xlim())
            ticks = list(self._gl.keys())
            ax2.set_xticks(ticks)
            
        if title:
            ax.set_title(title)

def _exportSoilToDf(soilData:dict,resolution:float=0) -> tuple:
    columns = [soilData['name']]
    coords_df = pd.DataFrame(soilData['coords'],index=["lat","lon"],columns=columns)
    #
    reflectance = soilData['reflectance']
    wavelengths = soilData['wavelengths']
    if resolution < 0:
        print("resolution cannot be negative")
        return None
    if resolution:
        f = interp1d(wavelengths,reflectance,kind="quadratic")
        wavelengths = np.arange(wavelengths.min(),wavelengths.max(),step=resolution)
        reflectance = f(wavelengths)
    
    spectrum_df = pd.DataFrame(reflectance,index=wavelengths)
    return coords_df,spectrum_df

def exportSoilToText(soilData:dict,resolution:float=0)->str:
    """Export soil database as comma sepatated values

    Args:
        soilData (dict): Soil data formatted to be used with soil Database
        resolution (float, optional): Resolution of spectrum 0 to keep current resolution. Defaults to 0.

    Returns:
        str: text formatted as comma separated values
    """
    dataframes = _exportSoilToDf(soilData,resolution)
    df1 = dataframes[0]
    df2 = dataframes[1]

    text = ",".join(['symbol']+[str(x) for x in df1.columns.values.tolist()])+os.linesep

    for index,record in df1.iterrows():
        text += ",".join([str(index)] + [str(x) for x in record.values.tolist()]) + os.linesep

    for index,record in df2.iterrows():
        text += ",".join([str(index)] + [str(x) for x in record.values.tolist()]) + os.linesep

    return text


def batchExport(filepath:str,selection:Sequence[str],database:soilDatabase=None,resolution:float=0):
    """Export all soils in selection list as excel file. Both batch... functions are intened to be used in GUI

    Args:
        filepath (str): path to new excel file where soils will be saved
        selection (Sequence[str]): list of soils to save
        database (soilDatabase, optional): Use only in text mode. Defaults to None.
        resolution (float, optional): resolution of exported spectra. Defaults to 0 keep orginal resolution.
    """
    sldb = soilDatabase() if database is None else database
    writer = pd.ExcelWriter(filepath)
    index = True
    for col, soilName in enumerate(selection):
        soilData = sldb.getSoil(soilName)
        dataframes = _exportSoilToDf(soilData,resolution)
        if col > 0:
            col+=1
            index=False
        dataframes[0].to_excel(writer,sheet_name='exported',startrow=0, startcol=col, index=index, index_label='symbol')   
        dataframes[1].to_excel(writer,sheet_name='exported',startrow=3, startcol=col, index=index, header=False)
    writer.save()        


def batchImport(fileName:str,database:soilDatabase=None,listonly:bool=False,selection:Sequence[str]=None) -> None:
    """Import all soils in selection list from excel file. Both batch... functions are intened to be used in GUI

    Args:
        fileName (str): path to existing w excel file where soils are stored
        database (soilDatabase, optional): Use existing database or create new. Defaults to None (create).
        listonly (bool, optional):  Only return soil names and exit. Defaults to False.
        selection (Sequence, optional): List of soils to be imported. Must be a subset od soils in excel file. Defaults to None.

    Returns:
        None or List(str): List with all soils in given Excel file
    """

    sldb = soilDatabase() if database is None else database
    try:
        coordinates = pd.read_excel(fileName,nrows=2,index_col="symbol")
        spectra = pd.read_excel(fileName,skiprows=[1,2],index_col="symbol")
        wavelengths = spectra.index.values
        names = coordinates.columns.values
    except:
        return None
    if listonly:
        return names
    if selection is not None:
        if not set(selection).issubset(names):
            return None
        names = selection
    for name in names:
        coords = coordinates[name].values
        reflectance = spectra[name].values
        s = soilSpectrum()
        s.importSeries(wavelengths,reflectance)
        sl = s.exportSoil(name,*coords)
        sldb.addToDatabase(sl)
    return None

class soilModel():
    def __init__(self):
        self.__x_test=np.concatenate((np.arange(0,89.),np.linspace(89,90,9)))
        self.__y_test = None
        self.reset_plot()
        self.__indexes = {k:v for v,k in enumerate('abcd')}
        self.__aTs = None
        self.__abcd = None
        self._soil_params = None
        
    def __recalc(self):
        self.a45 = 0.33 - 0.11 * self.T3D + self.GL
        sA = 6.26e-7 + 0.0043*pow(self.HSD,-1.418)
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
        self._soil_params = []
        self.__y_test = None
    
   
    def fit(self,spectra:float,T3D:float,HSD:float,soilName:str='') -> None:
        """fit soil albedo model to the generated date

        Args:
            GL (float): soil second derivatives of spectral components at given wavelengths
            T3D (float): terrain 3D ratio (ratio between real surface and flat surface)
            HSD (float): roughness in mm
            soilName (str, optional): Name for soil. Defaults to ''.
        """

        self.GL = spectra
        self.T3D = T3D 
        self.HSD = HSD
        self.name = soilName
        
        self.__recalc()
        
        p2 = np.arange(15,76,1)
        p3 = np.array([90])
        x_train = np.concatenate((p2,p3))

        y2 = self.__aTs[p2]
        y3 = np.array([1])
        y_train = np.concatenate((y2,y3))

        x0 = np.array([-2.,-0.01,0.01,-1.0e-7]) # starting values, possible source of overfitting
        self.__res = least_squares(self.__fit_aTS,x0,args=(x_train,y_train))
        self.__reset_abcd = copy.copy(self.__res.x)
        self.__abcd = copy.copy(self.__res.x)
        self.modify_curve_parameters(b=-2/200)

        params  = [self.name,self.T3D,self.HSD,self.a45_stright]
        names = ["Soil","T3D","HSD","\u03b145"]
        self._soil_params = list(zip(names,params))
        self.__y_test = self.__aTS(self.__abcd,self.__x_test)
            
    def get_soil_params(self) -> dict:
        """getter, returns soil paramteres

        Returns:
            dict: soil parameters
        """

        return self._soil_params
    

    def drawFitted(self,ax:plt.Axes=None) -> None:
        """draw fitted curve on selected axis.

        Args:
            ax (plt.Axes, optional): Axis where curwe is to be drown. If None use current graphic device (gca). Defaults to None.
        """
 
        ax = ax or plt.gca()
        p_x = np.array([0,10,20,45,65,75])
        p_y = self.__aTs[p_x]
        
        label = "T3D: {}     HSD: {}    \u03b145: {:0.4} \n".format(self.T3D,self.HSD,self.a45)
        label += "a: {:0.4}    b: {:0.4} \nc: {:0.4}   d: {:0.4e}".format(*self.__abcd)
        #ax.scatter(p_x,p_y,s=10,c='#FA1121')
        #ax.plot(self.__x_test,y_test,linewidth=2,label=label)
        ax.plot(self.__x_test,self.__y_test,linewidth=2)
        
        ax.set_ylim((0,1))
        ax.xaxis.set_major_locator(MultipleLocator(10))
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.1))
        ax.grid(which='both',linestyle=":",linewidth="1",color="#AAAAAA")
        ax.text(5, 0.95, label, fontsize=12, linespacing = 1.5,
                verticalalignment='top', bbox=dict(facecolor='white'))
        ax.set_xlabel("Solar Zenith Angle")
        ax.set_ylabel("Albedo")

    def exportCurve(self) -> pd.DataFrame:
        """Exports curve in a form of two column pandas data frame to draw curve externally

        Returns:
            pd.DataFrame: Date frame with curve data
        """
        df = pd.DataFrame(self.__y_test,index=self.__x_test,columns=["albedo"])
        return df        

    def exportParams(self) -> pd.Series:
        """Exports curve parameters as pandas serie

        Returns:
            pd.Series: curve parameters
        """
        cindex = self.get_curve_params().keys()
        cvalues = self.get_curve_params().values()
        sindex,svalues = list(zip(*self.get_soil_params()))
        index = list(sindex)+list(cindex)
        values = list(svalues)+list(cvalues)
        df = pd.Series(values,index=index)
        return df
        
        
    def modify_curve_parameters(self,**kwargs):
        """Allow to manually modify curve parameters (a,b,c,d)
        """

        for key in kwargs.keys():
            index = self.__indexes[key]
            self.__abcd[index] = self.__reset_abcd[index]*(1+kwargs[key])

     
    def get_model_coefs(self) -> list:
        """Returns model coefficients as list [a,b,c,d]
        """
        return self.__abcd
    
    def get_parameters(self) -> dict:
        """Returns model coefficeints as dict [a,b,c,d]
        """

        curve_params = {}
        for key,index in self.__indexes.items():
            curve_params[key] = self.__abcd[index]
        return curve_params
 
