#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 09:27:40 2020

@author: jarek
"""

#import os, pickle
from PyQt5 import QtWidgets, QtCore
#os.chdir("/home/jarek/Dropbox/CODE/albedo")
#from soil import soil, soilDatabase
from GUI.baseGui import baseGui
from GUI.soilmanagerwidget import soilsManager
from GUI.soilcollectionwidget import collectionsManager
from GUI.soilsCollections import soilsCollections
#app=QtWidgets.QApplication([])

#%%
class soilsDialog(QtWidgets.QDialog,baseGui):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800,600)
        self.setWindowTitle("Soil manager")
        self.currentSoilName = None

        self.collections = soilsCollections()
        self.listModel = self.collections.getSoilsDataModel()
        self.soilList = QtWidgets.QListView()
        self.soilList.setMaximumWidth(190)
        self.soilList.setModel(self.listModel)

        # tab with collection manager is 0
        # tab with soil manager is 1
        self.tab_changed(0) #inital position
        
        self.collectionsManager = collectionsManager()
        self.soilsManager = soilsManager(self.collections.getSoilsDatabase())
        
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.collectionsManager,"Collection Manager")
        tabs.addTab(self.soilsManager,"Soil Manager")
        tabs.currentChanged.connect(self.tab_changed)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(tabs)
        mainLayout.addWidget(self.soilList)
        self.setLayout(mainLayout)

    def get_soil(self,index):
        soilName = self.listModel.data(index,QtCore.Qt.DisplayRole)
        self.currentSoilName = soilName
        self.soilsManager.soil_clicked(soilName)

    
    def get_selection(self):
        pass


    def tab_changed(self,index):
        self.currentTab = index
        if self.currentTab == 1:
            f = self.get_soil
            selectionMode = QtWidgets.QAbstractItemView.SingleSelection
        else:
            f = self.x
            selectionMode = QtWidgets.QAbstractItemView.MultiSelection
        
        try:
            self.soilList.clicked.disconnect()
        except TypeError:
            pass
        self.soilList.clicked.connect(f)
        self.soilList.setSelectionMode(selectionMode)

        
#if __name__ == '__main__':
#    window = soilsDialog()
#    window.show()
 #   app.exec_()