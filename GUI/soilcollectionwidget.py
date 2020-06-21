#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:24:47 2020

@author: jarek
"""
import pickle
from PyQt5 import QtWidgets, QtCore
from soil import soil, soilDatabase
from GUI.baseGui import baseGui
from GUI.soilsCollections import soilsCollections
#%%
class collectionsManager(QtWidgets.QWidget,baseGui):
    def __init__(self):
        super().__init__()
        
        self.collectionsList = QtWidgets.QListView()
        self.collectionsList.setMaximumWidth(190)
        self.newCollection = QtWidgets.QLineEdit()
        self.newCollection.setMaximumWidth(190)
        
        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addWidget(self.newCollection)
        leftLayout.addWidget(self.collectionsList)
        
        newButton = QtWidgets.QPushButton('&New')
        modButton = QtWidgets.QPushButton('&Modify')
        delButton = QtWidgets.QPushButton('&Delete')
        resButton = QtWidgets.QPushButton('&Reset')
        useButton = QtWidgets.QPushButton('&USE')
        clsButton = QtWidgets.QPushButton('&CLOSE')
        
        rightLayout = QtWidgets.QVBoxLayout()
        rightLayout.addWidget(newButton)
        rightLayout.addWidget(modButton)
        rightLayout.addWidget(delButton)
        rightLayout.addWidget(resButton)
        rightLayout.addStretch()
        rightLayout.addWidget(useButton)
        rightLayout.addWidget(clsButton)
        
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        
        self.setLayout(mainLayout)