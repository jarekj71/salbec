#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 09:27:40 2020

@author: jarek
"""

import os
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
from PROC.soil import soil, soilDatabase
from GUI.baseGui import baseGui

#%%

class soilImporterDialog(QtWidgets.QDialog,baseGui): 
    def __init__(self):
        super().__init__()
        self.setFixedSize(600,500)
        self.setWindowTitle("Soil importer")
        
        self.figure = Figure(figsize=(6,4))
        self.canvas = FigureCanvas(self.figure)
        self.gl = None
        self.plotted = False
       
        self._soilDatabase = soilDatabase()
                
        #import layout
        importLayout = QtWidgets.QVBoxLayout()
        
        openFileButton=QtWidgets.QPushButton("Open")
        fileLayout=QtWidgets.QHBoxLayout() 
        fileLayout.addStretch()
        fileLayout.addWidget(openFileButton)
        importLayout.addLayout(fileLayout)
       
        openFileButton.clicked.connect(self.openButton_clicked) 
       
        #image layout
        imageLayout = QtWidgets.QHBoxLayout()
        imageLayout.addWidget(self.canvas)
        
        
        soilLayout = QtWidgets.QVBoxLayout()
        #soil name
        nameLayout=QtWidgets.QHBoxLayout() 
        soilNameLabel=QtWidgets.QLabel("&Soil Name")
        self.soilNameField=QtWidgets.QLineEdit()
        soilNameLabel.setBuddy(self.soilNameField)
        nameLayout.addWidget(soilNameLabel)
        nameLayout.addWidget(self.soilNameField)
        soilLayout.addLayout(nameLayout)
        
        # and coordinates
        coorLayout=QtWidgets.QHBoxLayout() 
        lambdaLabel=QtWidgets.QLabel("lo&ngitude")
        self.lambdaField=QtWidgets.QLineEdit()
        lambdaLabel.setBuddy(self.lambdaField)
        phiLabel=QtWidgets.QLabel("la&titude")
        self.phiField=QtWidgets.QLineEdit()
        phiLabel.setBuddy(self.phiField)
        coorLayout.addWidget(lambdaLabel)
        coorLayout.addWidget(self.lambdaField)
        coorLayout.addWidget(phiLabel)
        coorLayout.addWidget(self.phiField)
        soilLayout.addLayout(coorLayout)
        
        #save layout
        saveLayout = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QPushButton("&ADD")
        addButton.setToolTip("add soil to the database")
        plotButton = QtWidgets.QPushButton("&PLOT")
        plotButton.setToolTip("save soil curve as pdf")
        closeButton = QtWidgets.QPushButton("&CLOSE")
      
        saveLayout.addWidget(addButton)
        saveLayout.addWidget(plotButton)
        saveLayout.addWidget(closeButton)
        saveLayout.addStretch() 
        self.a45Label = QtWidgets.QLabel("a45: ")
        saveLayout.addWidget(self.a45Label)
        soilLayout.addLayout(saveLayout)

        addButton.clicked.connect(self.addButton_clicked)  # connect to Add function
        plotButton.clicked.connect(self.plotButton_clicked)  # connect to Add function
        closeButton.clicked.connect(self.accept)
        
        #main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(importLayout)
        mainLayout.addLayout(imageLayout)
        mainLayout.addLayout(soilLayout)
        self.setLayout(mainLayout)


    def openButton_clicked(self):   
        filetypes = "Comma separated (*.csv);;Excel (*.xls, *.xlsx)"
        
        fileName,_ = QtWidgets.QFileDialog.\
            getOpenFileName(self,"File to take spectrum from", self.inputDir,filetypes) #2B
      
        self.gl = soil()
        warning = self.gl.importFromFile(fileName)
        if warning:
            self.warning(*warning)
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.gl.drawSpectrum(ax)
        self.canvas.draw()
        self.plotted = True
        self.a45Label.setText("a45 spectrum: {}".format(self.gl.a45))
    

    def _getCoordinates(self):
        # wymaga modyfikacji
        try:
            latValue =  float(self.lambdaField.text())
        except ValueError:
            latValue = None
            
        try:
            lonValue =  float(self.phiField.text())
        except ValueError:
            lonValue = None
        return(latValue,lonValue)
    

    def _clearAddForm(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis('off')
        self.canvas.draw()        
        self.lambdaField.clear()
        self.phiField.clear()
        self.soilNameField.clear()
        self.soilNameField.clear()
        self.plotted = False
    
    
    def addButton_clicked(self):
        coordinates = self._getCoordinates()
        soilName = self.soilNameField.text()
        if self.gl is None:
            self.warning("Open spectrum file first",None)
            return

        if soilName =='':
            self.warning("Soil name cannot be empty")
            return
        
        soil = self.gl.exportSoil(soilName,*coordinates)
        warning =  self._soilDatabase.addToDatabase(soil)
        if warning:
            self.warning(*warning)
            return
        else:
            self.gl = None
            self._clearAddForm()
            self._e.message("Soil {} added to database".format(soilName))
        return
    

    def plotButton_clicked(self):
        if self.plotted ==False:
            self.warning("Nothing to plot",None)
            return
        
        filetypes = "pdf (*pdf);;png (*png);;svg (*svg)"
        fileName,fileType = QtWidgets.QFileDialog.\
            getSaveFileName(self,"File to plot results", self.outputDir,filetypes)
        file,ext = os.path.splitext(fileName)
        
        if ext not in ['.pdf','.png','.svg']:
            fileName = fileName+"."+fileType[:3]
        
        fig,ax = matplotlib.pyplot.subplots(1,1,figsize=(9,5),dpi=150)
        self.gl.drawSpectrum(ax,title=self.soilNameField.text())
        fig.savefig(fileName)
        
