#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 20:29:55 2020

@author: jarekj
"""


import os, pickle
from PyQt5 import QtWidgets

class database():
    def __init__(self,databaseName=None):
        self._databases = ".DATABASES"
        self._databaseDir = os.path.join(self._databases,databaseName) 
        self._databaseFile = os.path.join(self._databases,databaseName+".p")
        self._rebuildDatabase()

    def createDatabase(self):
        if not os.path.isdir(self._databases):
            print("create database")
            os.mkdir(self._databases)
        if not os.path.isdir(self._databaseDir):
            os.mkdir(self._databaseDir)
        if not os.path.isfile(self._databaseFile):
            print("create database file")
            pickle.dump({},open(self._databaseFile,"wb+")) # dump empty dict
        print("database exists")
            
    def _entryName(self,entryName):
        entryName = ''.join(entryName.split())
        name,ext = os.path.splitext(entryName)
        if ext == '.sl': # remove extension if file name
            return name
        return entryName
    
    def _getDatabase(self):
        try:
            database = pickle.load(open(self._databaseFile,"rb"))
        except FileNotFoundError:
            self._rebuildDatabase()
            database = pickle.load(open(self._databaseFile,"rb"))
        
        fileList = os.listdir(os.path.join(self._databaseDir))
        if list(database.keys()) == [] and fileList == []:
            return {}
        try:
            soilnames_sorted = list(database.keys())
            soilnames_sorted.sort()
        except TypeError:
            self._rebuildDatabase()
            names_sorted = list(database.keys())
            names_sorted.sort()
        fileList = [self._entryName(entryName) for entryName in fileList]
        fileList.sort()
        if names_sorted != fileList:
            self._rebuildDatabase()
        return database
        
    def listDatabase(self):
        database = self._getDatabase()
        for key,value in database.items():
            print(key,os.path.basename(value))
        
    @property
    def entryNames(self):
        database = self._getDatabase()
        names = list(database.keys())
        names.sort()
        return names
    
    def getPath(self,entryName):
        database = self._getDatabase()
        try:
            return database[entryName]
        except KeyError:
            return None

    @property
    def database(self):
        return self._getDatabase()
        
    def rebuildDatabase(self):
        self._rebuildDatabase()

    def _rebuildDatabase(self):
        fileList = os.listdir(self._databaseDir)
        if fileList == []:
            pickle.dump({},open(self._databaseFile,"wb+")) # dump empty dict
            return
        database = {}
        fileList.sort()
        for file in fileList:
            soil = pickle.load(open(os.path.join(self._databaseDir,file),"rb"))
            name = self._entryName(soil['name'])
            database[name] = os.path.join(self._databaseDir,file)
        pickle.dump(database,open(self._databaseFile,"wb+"))
        self._database = database

        
    def addToDatabase(self,entry):
        database = pickle.load(open(self._databaseFile,"rb"))
        entryName = self._entryName(entry['name'])
        if entryName in database.keys():
            return "Cannot add entity", "Entity with name {} exists in database. Use different name".format(entry['name'])
        
        entryFileName = entryName+'.sl'
        entryFileName = os.path.join(self._databaseDir,entryFileName)
        pickle.dump(entry,open(entryFileName,"wb+"))
        database[entryName] = entryFileName
        pickle.dump(database,open(self._databaseFile,"wb+"))
        return None

    
    def removeFromDatabase(self,entryName): 
        database = self._getDatabase()
        if entryName not in list(database.keys()):
            return "Cannot find entity: {}".format(entryName),"Check entry name"
        database.pop(entryName)
        try:
            os.remove(os.path.join(self._databaseDir,entryName+'.sl'))
        except NameError: #sould never happen
            return "File error",None
        pickle.dump(database,open(self._databaseFile,"wb+"))
        return None


    def replaceEntry(self,currentEntryName,entry):
        #remove and add new soil must be craated
        database = self._getDatabase()
        if currentEntryName not in list(database.keys()):
            return "Cannot find entity: {}".format(currentEntryName),"Check entry name"
        entryName = self._entryName(entry['name'])
        
        if entryName == currentEntryName: #in modify file only
            entryFileName = currentEntryName+'.sl'
            entryFileName = os.path.join(self._databaseDir,entryFileName)
            pickle.dump(entry,open(entryFileName,"wb+"))
            return None
        
        warning = self.addToDatabase(entry)
        if warning:
            return warning
        warning = self.removeFromDatabase(currentEntryName)
        if warning:
            self.removeFromDatabase(entryName)
            return warning
        return None
   
    
    def clearDatabase(self):
        fileList = os.listdir(self._databaseDir)
        for fileName in fileList:
            filePath = os.path.join(self._databaseDir, fileName)
            try:
                if os.path.isfile(filePath):
                    os.unlink(filePath)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (filePath, e))
        pickle.dump({},open(self._databaseFile,"wb+")) # dump empty dict
