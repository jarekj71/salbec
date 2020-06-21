#!/home/jarek/albedo/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 06:56:47 2020

@author: jarekj
"""

import os, pickle, sys
#os.chdir("/home/jarek/Dropbox/CODE/albedo")
from PyQt5 import QtWidgets, QtCore
from soil import soil, soilDatabase
from GUI.baseGui import baseGui


#%%
class collections:
    def __init__(self):
        self._path = ".SOILS/collections.cl"
        self._loadCollections()
        self.collectionModel = QtCore.QStringListModel()
        self.collectionModel.setStringList(self.collections.keys()) # redraw soil list
        
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

  
class colManagerDialog(QtWidgets.QDialog,baseGui): 
    def __init__(self,collections,soilDatabase):
        super().__init__()
        self.setFixedSize(800,500)
        self.setWindowTitle("Collection manager")

        self.listCollections = collections        
        self.collectionList = QtWidgets.QListView()
        self.collectionList.setModel(self.listCollections.getModel())                
        

        self.items = self._soilDatabase.soilNames
        
        self.itemModel = QtCore.QStringListModel()
        self.itemModel.setStringList(self.items) # redraw soil list
        self.itemList = QtWidgets.QListView()
        self.itemList.setModel(self.itemModel)   
        self.itemList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        
        self.tmp_button = QtWidgets.QPushButton("Duda")
        self.tmp_button.clicked.connect(self.addToCollection)
        self.collectionList.clicked.connect(self.selectCollection)
        
        upperLayout = QtWidgets.QHBoxLayout()
        upperLayout.addWidget(self.collectionList)
        upperLayout.addWidget(self.itemList)
        upperLayout.addWidget(self.tmp_button)
        upperLayout.addStretch()
        self.setLayout(upperLayout)

    def selectCollection(self,index):
        model = self.listCollections.getModel()
        collectionName = model.data(index,QtCore.Qt.DisplayRole)
        collectionItems = self.listCollections.getCollection(collectionName)
        self.itemList.selectionModel().clear()
        for i in range(self.itemModel.rowCount()):
            ix = self.itemModel.index(i, 0)
            collectionItem = self.itemModel.data(ix,QtCore.Qt.DisplayRole)
            if collectionItem in collectionItems:
                self.itemList.selectionModel().select(ix,QtCore.QItemSelectionModel.Select)

        
    def addToCollection(self):
        pass
                


#if __name__ == '__main__':
#    model = collections()
#    window = colManagerDialog(model)
#    window.show()
#    sys.exit(app.exec_())

