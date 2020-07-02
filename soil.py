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
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import copy, os, pickle
#from io import StringIO będzie niezbędne przy rozbudowie

#%%

class soilDatabase():
    def __init__(self,databaseDir=None,databaseFile=None):
        self._databaseDir = databaseDir or ".SOILS"
        self._soilsDir = os.path.join(self._databaseDir,"soils") 
        self._databaseFile = databaseFile or os.path.join(self._databaseDir,"soilDatabase.p")
        self._rebuildDatabase()

    def createSoilDatabase(self):
        if not os.path.isdir(self._databaseDir):
            print("create database")
            os.mkdir(self._databaseDir)
        if not os.path.isdir(self._soilsDir):
            os.mkdir(self._soilsDir)
        if not os.path.isfile(self._databaseFile):
            print("create database file")
            pickle.dump({},open(self._databaseFile,"wb+")) # dump empty dict
        print("database exists")
            
    def _soilName(self,soilName):
        soilName = ''.join(soilName.split())
        name,ext = os.path.splitext(soilName)
        if ext == '.sl': # remove extension if file name
            return name
        return soilName
    
    def _getDatabase(self):
        try:
            database = pickle.load(open(self._databaseFile,"rb"))
        except FileNotFoundError:
            self._rebuildDatabase()
            database = pickle.load(open(self._databaseFile,"rb"))
        
        fileList = os.listdir(os.path.join(self._soilsDir))
        if list(database.keys()) == [] and fileList == []:
            return {}
        try:
            soilnames_sorted = list(database.keys())
            soilnames_sorted.sort()
        except TypeError:
            self._rebuildDatabase()
            soilnames_sorted = list(database.keys())
            soilnames_sorted.sort()
        fileList = [self._soilName(soilName) for soilName in fileList]
        fileList.sort()
        if soilnames_sorted != fileList:
            self._rebuildDatabase()
        return database
        
    def listDatabase(self):
        database = self._getDatabase()
        for key,value in database.items():
            print(key,os.path.basename(value))
        
    @property
    def soilNames(self):
        database = self._getDatabase()
        names = list(database.keys())
        names.sort()
        return names
    
    def getPath(self,soilName):
        database = self._getDatabase()
        try:
            return database[soilName]
        except KeyError:
            return None

    @property
    def database(self):
        return self._getDatabase()
        
    def rebuildDatabase(self):
        self._rebuildDatabase()

    def _rebuildDatabase(self):
        fileList = os.listdir(self._soilsDir)
        if fileList == []:
            pickle.dump({},open(self._databaseFile,"wb+")) # dump empty dict
            return
        database = {}
        fileList.sort()
        for file in fileList:
            soil = pickle.load(open(os.path.join(self._soilsDir,file),"rb"))
            name = self._soilName(soil['name'])
            database[name] = os.path.join(self._soilsDir,file)
        pickle.dump(database,open(self._databaseFile,"wb+"))
        self._database = database

        
    def addToDatabase(self,soil):
        database = pickle.load(open(self._databaseFile,"rb"))
        soilName = self._soilName(soil['name'])
        if soilName in database.keys():
            return "Cannot add soil", "Soil with name {} exists in database. Use different name".format(soil['name'])
        
        soilFileName = soilName+'.sl'
        soilFileName = os.path.join(self._soilsDir,soilFileName)
        pickle.dump(soil,open(soilFileName,"wb+"))
        database[soilName] = soilFileName
        pickle.dump(database,open(self._databaseFile,"wb+"))
        return None

    
    def removeFromDatabase(self,soilName): 
        database = self._getDatabase()
        if soilName not in list(database.keys()):
            return "Cannot find soil: {}".format(soilName),"Check soil name"
        database.pop(soilName)
        try:
            os.remove(os.path.join(self._soilsDir,soilName+'.sl'))
        except NameError: #sould never happen
            return "File error",None
        pickle.dump(database,open(self._databaseFile,"wb+"))
        return None


    def replaceSoil(self,currentSoilName,soil):
        #remove and add new soil must be craated
        database = self._getDatabase()
        if currentSoilName not in list(database.keys()):
            return "Cannot find soil: {}".format(currentSoilName),"Check soil name"
        soilName = self._soilName(soil['name'])
        
        if soilName == currentSoilName: #in modify file only
            soilFileName = currentSoilName+'.sl'
            soilFileName = os.path.join(self._soilsDir,soilFileName)
            pickle.dump(soil,open(soilFileName,"wb+"))
            return None
        
        warning = self.addToDatabase(soil)
        if warning:
            return warning
        warning = self.removeFromDatabase(currentSoilName)
        if warning:
            self.removeFromDatabase(soilName)
            return warning
        return None
   
    
    def clearDatabase(self):
        fileList = os.listdir(self._soilsDir)
        for filename in fileList:
            file_path = os.path.join(self._soilsDir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        pickle.dump({},open(self._databaseFile,"wb+")) # dump empty dict
        
    
    def getSoil(self,soilName):
        soilPath = self.getPath(soilName)
        if soilPath is None:
            return None
        soilData = pickle.load(open(soilPath,"rb"))
        return soilData

#%%
def read_csv(fileName):
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

class soil():
    def __init__(self):
        self._const = {}
        self._const[574] = -5795.4
        self._const[1087] = -510.24
        self._const[1355] = 7787.2
        self._const[1656] = 12161
        self._const[698] = 6932.8
        self.soilName = None
        self.coordinates = None

    def importFromFile(self,fileName):
        
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
    
    def importSeries(self,wavelengths,reflectance):
        self._wavelengths = wavelengths
        self._reflectance = reflectance
        self._f = interp1d(self._wavelengths,self._reflectance,kind="quadratic")
        self._gl = {}
        for key,value in self._const.items():
            self._gl[key] = value*derivative(self._f,key,dx=10,n=2)

        return None

    
    @property
    def a45(self):    
        a45 = sum(self._gl.values())
        return a45

    @property
    def params(self):
        return self._gl
    
    @property
    def coefs(self):
        return self._const
    
    @property
    def interp(self):
        return self._f
    
    def exportSoil(self,name,lat=None,lon=None):
        #domyślna nazwa tworzona na zewnątrz
        soil = {}
        soil['name'] = name
        soil['coords'] = (lat,lon)
        soil['reflectance'] = self._reflectance
        soil['wavelengths'] = self._wavelengths
        soil['params'] = self._gl
        soil['a45'] = self.a45
        return soil
    
    def importFromDatabase(self,soil):
        lat,lon = soil['coords']
        name = soil['name']
        self._reflectance = soil['reflectance']
        self._wavelengths = soil['wavelengths']
        self._gl = soil['params']
        self._f = interp1d(self._wavelengths,self._reflectance,kind="quadratic")    
        return name,lat,lon
    

    def drawSpectrum(self,ax,lines=True,title=False):
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

#%%
def _exportSoilToDf(soilData,resolution=0):
    columns = [soilData['name']]
    coords_df = pd.DataFrame(soilData['coords'],index=["lat","lon"],columns=columns)
    #
    reflectance = soilData['reflectance']
    wavelengths = soilData['wavelengths']
    if resolution:
        f = interp1d(wavelengths,reflectance,kind="quadratic")
        wavelengths = np.arange(wavelengths.min(),wavelengths.max(),step=resolution)
        reflectance = f(wavelengths)
    
    spectrum_df = pd.DataFrame(reflectance,index=wavelengths)
    return coords_df,spectrum_df
    

#%%

def exportSoilToText(soilData,resolution=0):
    dataframes = _exportSoilToDf(soilData,resolution)
    df1 = dataframes[0]
    df2 = dataframes[1]

    text = ",".join(['symbol']+[str(x) for x in df1.columns.values.tolist()])+os.linesep

    for index,record in df1.iterrows():
        text += ",".join([str(index)] + [str(x) for x in record.values.tolist()]) + os.linesep

    for index,record in df2.iterrows():
        text += ",".join([str(index)] + [str(x) for x in record.values.tolist()]) + os.linesep

    return text


#%%
def batchExport(filepath,selection,database=None,resolution=0):
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

#%%
def batchImport(fileName,database=None,listonly=False,selection=None):
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
        s = soil()
        s.importSeries(wavelengths,reflectance)
        sl = s.exportSoil(name,*coords)
        sldb.addToDatabase(sl)
    return None
#%%
class soilCurve():
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
        self._soil_params = []
        self.__y_test = None
    
   
    def fit(self,GL,T3D,HSD,soilName=''):
        self.GL = GL
        self.T3D = T3D # usunąć selfy
        self.HSD = HSD
        self.name = soilName
        
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
        self.modify_curve_parameters(b=-2/200)

        params  = [self.name,self.T3D,self.HSD,self.a45_stright]
        names = ["Soil","T3D","HSD","\u03b145"]
        self._soil_params = list(zip(names,params))
        self.__y_test = self.__aTS(self.__abcd,self.__x_test)
            
    def get_soil_params(self):
        return self._soil_params
    

    def drawFitted(self,ax=None,current=True):
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

    def exportCurve(self):
        df = pd.DataFrame(self.__y_test,index=self.__x_test,columns=["albedo"])
        return df        

    def exportParams(self):
        cindex = self.get_curve_params().keys()
        cvalues = self.get_curve_params().values()
        sindex,svalues = list(zip(*self.get_soil_params()))
        index = list(sindex)+list(cindex)
        values = list(svalues)+list(cvalues)
        df = pd.Series(values,index=index)
        return df
        
        
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
 
