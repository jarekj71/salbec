#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 10:24:41 2020

@author: jarek
"""
import os, pickle
from PyQt5 import QtCore
from soil import soilDatabase

#%%
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
    
    def getModel(self):
        return self.collectionModel
    
    def getCollection(self,key):
        return self.collections[key]
    
    def addCollection(self,key,*values):
        self.collections[key] = set(values)
        self.collectionModel.setStringList(self.collections.keys()) # redraw soil list
    
    def removeCollection(self,key):
        try:
            del self.collections[key]
        except KeyError: 
            pass
    
    def addToCollection(self,key,*values):
        try: 
            self.collections[key] = self.collection.union(values)
        except KeyError: 
            self.addCollection(key,*values) 
            
    def removeFromCollection(self,key,*values):
        try:
            self.collections[key] = self.collection.difference(values)
        except KeyError:
            pass

    def getActiveCollection(self):
        return self.activeCollection
