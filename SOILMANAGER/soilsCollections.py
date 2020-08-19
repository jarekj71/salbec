#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 10:24:41 2020

@author: jarek
"""
import os, pickle
from PyQt5 import QtCore
from PyQt5.QtCore import (pyqtSignal)
from soilalbedo import soilDatabase

class soilsCollections():
    def __init__(self):
        self._soilDatabase = soilDatabase()
        self.listModel = QtCore.QStringListModel()
        self.listModel.setStringList(self._soilDatabase.soilNames) # redraw soil list
        
        self._path = ".SOILS/collections.cl"
        self._loadCollections()
        self.collectionModel = QtCore.QStringListModel()
        self.collectionModel.setStringList(self.collections.keys()) # redraw soil list
        self.activeCollection = self._soilDatabase.soilNames #inital full list
        
        self.selectionModel = QtCore.QStringListModel()
        self.selectionModel.setStringList(self.getSoilsNames())
        
    #Database
    def getSoilsNames(self):
        return self._soilDatabase.soilNames
    
    def getSoilsDataModel(self):
        return self.listModel
    
    def getSoilsDatabase(self):
        return self._soilDatabase
    
    #collections
    def _loadCollections(self):
        if not os.path.isfile(self._path):
            self.collections = {}
            self._saveCollections()
        self.collections = pickle.load(open(self._path,"rb"))
    
    def _saveCollections(self):
        pickle.dump(self.collections,open(self._path,"wb+"))
    
    def reloadSoilDataModel(self):
        self.listModel.setStringList(self._soilDatabase.soilNames)
    
    def _reloadCollections(self):
        self.collectionModel.setStringList(self.collections.keys()) # redraw soil list
        self._saveCollections()

    def getModel(self):
        return self.collectionModel
    
    def getCollection(self,key):
        try:
            return self.collections[key]
        except KeyError:
            return "collection {} does not exist",None 
    
    def addCollection(self,key,*values):
        if key in self.collections.keys():
            return "collection {} already exists",None
        self.collections[key] = set(values)
        self._reloadCollections()
        return None
    
    def modifyCollection(self,key,*values):
        if key not in self.collections.keys():
            return "collection {} does not exist",None
        self.collections[key] = set(values)
        self._reloadCollections()            
        return None
   
    def removeCollection(self,key):
        try:
            del self.collections[key]
            self._reloadCollections()
        except KeyError: 
            return "collection {} does not exist",None 

    def setActiveSelection(self,*activeSelection):
        if list(activeSelection) == []:
            activeSelection = self.getSoilsNames()
        self.selectionModel.setStringList(activeSelection)  
