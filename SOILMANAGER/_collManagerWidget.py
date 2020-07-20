#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:24:47 2020

@author: jarek
"""
import os
from PyQt5 import QtWidgets, QtCore
from GUI.baseGui import baseGui
from soil import batchExport, batchImport
#%%

class _collectionsManager(QtWidgets.QWidget,baseGui):
    def __init__(self,soilList,collections):
        super().__init__()
        
        self.soilListWidget = soilList
        self.soilCollections = collections
        self.currentIndex = None
        self.import_file_name = None
        
        self.collectionsList = QtWidgets.QListView()
        self.collectionsList.setMaximumWidth(190)
        self.collectionsList.setModel(self.soilCollections.getModel()) 
        self.newCollection = QtWidgets.QLineEdit()
        self.newCollection.setMaximumWidth(190)
       
        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addWidget(QtWidgets.QLabel("Soils Collections"))
        newLayout = QtWidgets.QHBoxLayout()
        newLayout.addWidget(QtWidgets.QLabel("New"))
        newLayout.addWidget(self.newCollection)
        leftLayout.addLayout(newLayout)
        leftLayout.addWidget(self.collectionsList)
        self.collectionsList.clicked.connect(self.selectCollection)
        
        self.newButton = QtWidgets.QPushButton('&New')
        self.newButton.setToolTip("add selection as new colection")
        modButton = QtWidgets.QPushButton('&Modify')
        modButton.setToolTip("modify saved collection to current selection")
        resButton = QtWidgets.QPushButton('&Reset')
        resButton.setToolTip("reset current selection to saved collection")
        delButton = QtWidgets.QPushButton('&Delete')

        useButton = QtWidgets.QPushButton('&USE')
        
        self.newButton.setEnabled(False)
        
        self.newButton.clicked.connect(self.newButton_clicked)
        resButton.clicked.connect(self.resetButton_clicked)
        delButton.clicked.connect(self.deleteButton_clicked)
        modButton.clicked.connect(self.modifyButton_clicked)
        useButton.clicked.connect(self.useButton_clicked)
        self.newCollection.textChanged.connect(self._switchNewButton)
        
        rightLayout = QtWidgets.QVBoxLayout()
        rightLayout.addWidget(self.newButton)
        rightLayout.addWidget(modButton)
        rightLayout.addWidget(delButton)
        rightLayout.addWidget(resButton)
        rightLayout.addStretch()
        rightLayout.addWidget(useButton)

        self.importLabel = QtWidgets.QLabel("")
        importSelect = QtWidgets.QPushButton("Select")
        importImport = QtWidgets.QPushButton("import")
        importClear = QtWidgets.QPushButton("Clear")
        self.importText = QtWidgets.QTextEdit("")
        self.importText.setReadOnly(True)
        importButtonsLayout = QtWidgets.QHBoxLayout()
        importButtonsLayout.addWidget(importSelect)
        importButtonsLayout.addWidget(importClear)
        importButtonsLayout.addWidget(importImport)
        

        importLayout = QtWidgets.QVBoxLayout()
        importLayout.addWidget(self.importLabel)
        importLayout.addLayout(importButtonsLayout)
        importLayout.addWidget(self.importText)
        importBox = QtWidgets.QGroupBox("Import collection")
        importBox.setLayout(importLayout)
        
        importSelect.clicked.connect(self.selectImport_clicked)
        importImport.clicked.connect(self.importImport_clicked)
        importClear.clicked.connect(self.importText.clear)

        self.resEdit = QtWidgets.QSpinBox()
        self.resEdit.setRange(0,1000)
        self.resEdit.setToolTip("Set resolution in nm of exported spectrum, 0 to keep original resolution")
        label = QtWidgets.QLabel('resolution (nm)')
        label.setBuddy(self.resEdit)
        resolutionLayout = QtWidgets.QHBoxLayout()
        resolutionLayout.addWidget(label)
        resolutionLayout.addWidget(self.resEdit)
        
        exportSelect = QtWidgets.QPushButton("Select")
        exportExport = QtWidgets.QPushButton("Export")
        exportClear = QtWidgets.QPushButton("Clear")
        self.exportText = QtWidgets.QTextEdit("")
        self.exportText.setReadOnly(True)
        exportButtonsLayout = QtWidgets.QHBoxLayout()
        exportButtonsLayout.addWidget(exportSelect)
        exportButtonsLayout.addWidget(exportClear)
        exportButtonsLayout.addWidget(exportExport)


        exportLayout = QtWidgets.QVBoxLayout()
        exportLayout.addLayout(resolutionLayout)
        exportLayout.addLayout(exportButtonsLayout)
        exportLayout.addWidget(self.exportText)
        exportBox = QtWidgets.QGroupBox("Export collection")
        exportBox.setLayout(exportLayout)
        
        exportSelect.clicked.connect(self.selectExport_clicked)
        exportExport.clicked.connect(self.exportExport_clicked)
        exportClear.clicked.connect(self.exportText.clear)
        
        ioLayout = QtWidgets.QVBoxLayout()
        ioLayout.addWidget(importBox)
        ioLayout.addWidget(exportBox)
        ioLayout.addStretch()
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(ioLayout)
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        
        self.setLayout(mainLayout)
        
    def selectExport_clicked(self):
        self.import_file_name = None
        selection = self._getSelection()
        if selection == []:
            self.warning("Nothing to export", "Select collection or soil[s] from the soil list first")
            return
        self.exportText.setText(",".join(selection))
        
    def selectImport_clicked(self):
        filetypes = "Excel (*.xls, *.xlsx)"
        
        fileName,_ = QtWidgets.QFileDialog.\
             getOpenFileName(self,"File to plot results", self.inputDir,filetypes) #2B
        if fileName=="":
            return
        
        database = self.soilCollections.getSoilsDatabase()
        names = batchImport(fileName,database,listonly=True)
        if names is None:
            self.warning("Nothing to import or wrong structure of the data")
            return
        soilsInDatabase = self.soilCollections.getSoilsNames()
       
        if len(set(soilsInDatabase).intersection(names)):
            self.warning("Some soil names are already present in database","Reset and check import file or import only selected soils")
        soilsToImport = set(names).difference(soilsInDatabase)
        self.importText.setText(",".join(soilsToImport))
        self.import_file_name = fileName
            
    def exportExport_clicked(self):
        filetypes = "Excel (*.xls, *.xlsx)"
        
        fileName,_ = QtWidgets.QFileDialog.\
             getSaveFileName(self,"File to save results", self.outputDir,filetypes) #2B
        if fileName=="":
            return
        file,ext = os.path.splitext(fileName)
        if ext != '.xlsx':
            fileName = fileName+'.xlsx'
                
        resolution = self.resEdit.value()
        selection = self.exportText.toPlainText().split(",")
        database = self.soilCollections.getSoilsDatabase()

        batchExport(fileName,selection,database,resolution)
        self.message("{} Exported".format(os.path.basename(fileName)))
    
    def importImport_clicked(self):
        if self.import_file_name is None:
            return
        
        selection = self.importText.toPlainText().split(",")
        database = self.soilCollections.getSoilsDatabase()
        batchImport(self.import_file_name,database,listonly=False,selection=selection)
        self.soilCollections.reloadSoilDataModel()
        self._select_in_list(selection)
        self.import_file_name = None
        self.message("{} Imported".format(os.path.basename(self.import_file_name)))

    def selectCollection(self,index):
        collectionModel = self.soilCollections.getModel()
        soilModel = self.soilCollections.getSoilsDataModel()
        
        collectionName = collectionModel.data(index,QtCore.Qt.DisplayRole)
        self.currentCollectionName = collectionName
        collectionItems = self.soilCollections.getCollection(collectionName)
        self._select_in_list(collectionItems)

        self.currentIndex = index    

    def _select_in_list(self,selection):
        soilModel = self.soilCollections.getSoilsDataModel()
        self.soilListWidget.selectionModel().clear()
        for i in range(soilModel.rowCount()):
            ix = soilModel.index(i, 0)
            possibleCollectionItem = soilModel.data(ix,QtCore.Qt.DisplayRole)
            if possibleCollectionItem in selection:
                self.soilListWidget.selectionModel().select(ix,QtCore.QItemSelectionModel.Select)
        

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

    def clearAll(self):
        self._clearCurrentSelection()
        self.collectionsList.selectionModel().clear()
        self.exportText.clear()
        self.importText.clear()
  
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
        self.clearAll()
    
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
