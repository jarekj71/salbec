#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 07:44:48 2020

@author: jarekj
"""
import copy, os, pickle

class soilDatabase():
    """Class intended to work with file database. This database stores soils in following format:
     - 
     -
     -
     -
     
    """
    def __init__(self,databaseDir:str=None,databaseFile:str=None):
        """Join with existing databse. Defaults parameters are intended to work with GUI. Data may not to exist.
            If database does not exists it creates a new empty one.

        Args:
            databaseDir (str, optional): Path to databsase directory. May not exist Defaults to None.
            databaseFile (str, optional): Path to databsase file. May not exist. Defaults to None.
        """
        self._databaseDir = databaseDir or ".SOILS"
        if not os.path.isdir(self._databaseDir):
            os.mkdir(self._databaseDir)
            print("directory <{}> created".format(self._databaseDir))

        self._soilsDir = os.path.join(self._databaseDir,"soils") 
        if not os.path.isdir(self._soilsDir):
            os.mkdir(self._soilsDir)
            print("directory <{}> created".format(self._soilsDir))          

        self._databaseFile = databaseFile or os.path.join(self._databaseDir,"soilDatabase.p")
        self._rebuildDatabase()

    def createSoilDatabase(self) -> None:
        """Creates new empty soil database
        """
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
        
    def listDatabase(self)-> None:
        """Prints list od soils in the database
        """
        database = self._getDatabase()
        for key,value in database.items():
            print(key,os.path.basename(value))
        
    @property
    def soilNames(self):
        database = self._getDatabase()
        names = list(database.keys())
        names.sort()
        return names
    
    def getPath(self,soilName:str) -> str:
        """[summary]

        Args:
            soilName (str): Name of soil in the database. Use .listDatabase() to see it all

        Returns:
            str or None: string with path to database entity or None if such entity does not exist
        """
        database = self._getDatabase()
        try:
            return database[soilName]
        except KeyError:
            return None

    @property
    def database(self):
        return self._getDatabase()
        
    def rebuildDatabase(self) -> None:
        """Check internal consistency and rebuilds database id necessary
        """
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

        
    def addToDatabase(self,soil:dict) -> None:
        """Adds soil dict to the database. See class description for details. 

        Args:
            soil (dict): Soil dict

        Returns:
            None or Error string: If returns string it is an Error string passed to GUI. None means success.
        """
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

    
    def removeFromDatabase(self,soilName:str) -> None:
        """Removes soil from the database with given name

        Args:
            soilName (str): Name of soil to be removed

        Returns:
            None or Error string: If returns string it is an Error string passed to GUI. None means success.
        """
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


    def replaceSoil(self,currentSoilName:str,soil:dict) ->None:
        """[summary]

        Args:
            currentSoilName (str): soil name to be replaced
            soil (dict): soil dict (see class description) to replace existing soils

        Returns:
             None or Error string: If returns string it is an Error string passed to GUI. None means success.
        """
        database = self._getDatabase()
        if currentSoilName not in list(database.keys()):
            return "Cannot find soil: {}".format(currentSoilName),"Check soil name"
        soilName = self._soilName(soil['name'])
        
        if soilName == currentSoilName: #in modify file only
            soilFileName = currentSoilName+'.sl'
            soilFileName = os.path.join(self._soilsDir,soilFileName)
            pickle.dump(soil,open(soilFileName,"wb+"))
            return None
        
        error = self.addToDatabase(soil)
        if error:
            return error
        error = self.removeFromDatabase(currentSoilName)
        if error:
            self.removeFromDatabase(soilName)
            return error
        return None
   
    
    def clearDatabase(self) -> None:
        """Clear entire databse

        Returns:
             None or Error string: If returns string it is an Error string passed to GUI. None means success.
        """
        fileList = os.listdir(self._soilsDir)
        for filename in fileList:
            file_path = os.path.join(self._soilsDir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        pickle.dump({},open(self._databaseFile,"wb+")) # dump empty dict
        return None
        
    
    def getSoil(self,soilName:str) -> dict:
        """[summary]

        Args:
            soilName (str): Soil name to get from the database

        Returns:
            dict: Soil dict, see class description for details.
        """
        soilPath = self.getPath(soilName)
        if soilPath is None:
            return None
        soilData = pickle.load(open(soilPath,"rb"))
        return soilData
 
