#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:24:47 2020

@author: jarek
"""

from PyQt5 import QtWidgets, QtCore
from GUI.baseGui import baseGui
#%%
class _collectionsManager(QtWidgets.QWidget,baseGui):
    def __init__(self,soilList,collections):
        super().__init__()
        
        self.soilListWidget = soilList
        self.soilCollections = collections
        self.currentIndex = None

        self.collectionsList = QtWidgets.QListView()
        self.collectionsList.setMaximumWidth(190)
        self.collectionsList.setModel(self.soilCollections.getModel()) 
        self.newCollection = QtWidgets.QLineEdit()
        self.newCollection.setMaximumWidth(190)
       
        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addWidget(self.newCollection)
        leftLayout.addWidget(self.collectionsList)
        self.collectionsList.clicked.connect(self.selectCollection)
        
        self.newButton = QtWidgets.QPushButton('&New')
        self.newButton.setToolTip("add selection as new colection")
        modButton = QtWidgets.QPushButton('&Modify')
        modButton.setToolTip("modify saved collection to current selection")
        resButton = QtWidgets.QPushButton('&Reset')
        resButton.setToolTip("reset current selection to saved collection")
        delButton = QtWidgets.QPushButton('&Delete')
        clrButton = QtWidgets.QPushButton('&Clear')
        clrButton.setToolTip("clear all selections")
        useButton = QtWidgets.QPushButton('&USE')
        
        self.newButton.setEnabled(False)
        
        self.newButton.clicked.connect(self.newButton_clicked)
        resButton.clicked.connect(self.resetButton_clicked)
        clrButton.clicked.connect(self.clearButton_clicked)
        delButton.clicked.connect(self.deleteButton_clicked)
        modButton.clicked.connect(self.modifyButton_clicked)
        useButton.clicked.connect(self.useButton_clicked)
        self.newCollection.textChanged.connect(self._switchNewButton)
        
        rightLayout = QtWidgets.QVBoxLayout()
        rightLayout.addWidget(self.newButton)
        rightLayout.addWidget(modButton)
        rightLayout.addWidget(delButton)
        rightLayout.addWidget(resButton)
        rightLayout.addWidget(clrButton)
        rightLayout.addStretch()
        rightLayout.addWidget(useButton)
        
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        
        self.setLayout(mainLayout)
        
    def selectCollection(self,index):
        collectionModel = self.soilCollections.getModel()
        soilModel = self.soilCollections.getSoilsDataModel()
        
        collectionName = collectionModel.data(index,QtCore.Qt.DisplayRole)
        self.currentCollectionName = collectionName
        collectionItems = self.soilCollections.getCollection(collectionName)
        self.soilListWidget.selectionModel().clear()
        
        for i in range(soilModel.rowCount()):
            ix = soilModel.index(i, 0)
            possibleCollectionItem = soilModel.data(ix,QtCore.Qt.DisplayRole)
            if possibleCollectionItem in collectionItems:
                self.soilListWidget.selectionModel().select(ix,QtCore.QItemSelectionModel.Select)

        self.currentIndex = index    

    def _switchNewButton(self):
        if self.newCollection.text() =="":
            self.newButton.setEnabled(False)
        else:
            self.newButton.setEnabled(True)
    
    def _getSelection(self):
        indexes = self.soilListWidget.selectionModel().selectedIndexes()
        soilModel = self.soilCollections.getSoilsDataModel()
        selection = [soilModel.data(index,QtCore.Qt.DisplayRole) for index in indexes]
        return selection

    def _clearCurrentSelection(self):
        self.soilListWidget.selectionModel().clear()

    def _clearAll(self):
        self._clearCurrentSelection()
        self.collectionsList.selectionModel().clear()
    
    def clearButton_clicked(self):
        self._clearAll()
    
    def useButton_clicked(self):
        selection = self._getSelection()
        self.soilCollections.setActiveSelection(*selection)
        
    def resetButton_clicked(self):
        if self.currentIndex is None:
            self._clearCurrentSelection()
            return
        self.selectCollection(self.currentIndex)
        
    def modifyButton_clicked(self):
        selection = self._getSelection()
        warning = self.soilCollections.modifyCollection(self.currentCollectionName,*selection)
        if warning:
            self.warning(*warning)
        
    def deleteButton_clicked(self):
        warning = self.soilCollections.removeCollection(self.currentCollectionName)
        if warning:
            self.warning(*warning)
            return
        self._clearAll()
    
    def newButton_clicked(self):
        newCollectionName = self.newCollection.text()
        if newCollectionName == "":
            self.warning("cannot add collection without name")
            return
        selection = self._getSelection()
        if selection == []:
            self.warning("cannot add empty collection")
            return
        warning = self.soilCollections.addCollection(newCollectionName,*selection)
        if warning:
            self.warning(*warning)
            return
        self.newCollection.clear()
        self._switchNewButton()
