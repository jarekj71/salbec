#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 09:27:40 2020

@author: jarek
"""

#import os, pickle
from PyQt5 import QtWidgets, QtCore
from GUI.baseGui import baseGui
from SOILMANAGER._soilManagerWidget import _soilsManager
from SOILMANAGER._collManagerWidget import _collectionsManager


#%%
class soilsDialog(QtWidgets.QDialog,baseGui):
    def __init__(self,collections):
        super().__init__()
        self.setFixedSize(800,600)
        self.setWindowTitle("Soil manager")
        self.currentSoilName = None
        self.collections = collections
        self.listModel = self.collections.getSoilsDataModel()

        self.soilList = QtWidgets.QListView()
        self.soilList.setMinimumWidth(190)
        self.soilList.setModel(self.listModel)
        self.clearButton = QtWidgets.QPushButton('&CLEAR')
        self.clearButton.setToolTip("clear all selections")
        
        closeButton = QtWidgets.QPushButton("&CLOSE")

        
        listLayout = QtWidgets.QVBoxLayout()
        listLayout.addWidget(QtWidgets.QLabel("Soils"))
        listLayout.addWidget(self.soilList)
        listLayout.addWidget(self.clearButton)
        listLayout.addWidget(closeButton)

        # tab with collection manager is 0
        # tab with soil manager is 1
        
        
        self.collectionsManager = _collectionsManager(self.soilList,self.collections)
        self.soilsManager = _soilsManager(self.soilList,self.collections)
        self.tab_changed(0) #inital position
        
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.collectionsManager,"Collection Manager")
        tabs.addTab(self.soilsManager,"Spectra Manager")
        
        tabs.currentChanged.connect(self.tab_changed)
        closeButton.clicked.connect(self.accept)

        
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(tabs)
        mainLayout.addLayout(listLayout)
        self.setLayout(mainLayout)

    def get_soil(self,index):
        soilName = self.listModel.data(index,QtCore.Qt.DisplayRole)
        self.currentSoilName = soilName
        self.soilsManager.soil_clicked(soilName)
    
    def nothing(self):
        pass


    def tab_changed(self,index):
        self.currentTab = index
        if self.currentTab == 1:
            selectionMode = QtWidgets.QAbstractItemView.SingleSelection
            f = self.get_soil
            s = self.soilsManager.clearAll
        else:
            selectionMode = QtWidgets.QAbstractItemView.MultiSelection
            f = self.nothing
            s = self.collectionsManager.clearAll
        
        try:
            self.soilList.clicked.disconnect()
            self.clearButton.clicked.disconnect()
        except TypeError:
            pass
        self.soilList.clicked.connect(f)
        self.clearButton.clicked.connect(s)
        self.soilList.setSelectionMode(selectionMode)

