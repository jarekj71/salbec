#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:24:47 2020

@author: jarek
"""
import pickle, os
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
from soilalbedo import soilSpectrum, exportSoilToText
from GUI.baseGui import baseGui

class _soilsManager(QtWidgets.QWidget,baseGui):
    def __init__(self,soilList,collections):
        super().__init__()

        self.figure = Figure(figsize=(7,4))
        self.canvas = FigureCanvas(self.figure)
        self.gl = None
        self._soil = None
        self.currentSoilName = None
        self.plotted = False
        self.soilListWidget = soilList
        self._collections = collections
        self._soilDatabase = self._collections.getSoilsDatabase()

        #upper layout
        self.soilLabel = QtWidgets.QLabel("")
        self.a45Label = QtWidgets.QLabel("")
        openFileButton=QtWidgets.QPushButton("Open")

        #
        upperLayout = QtWidgets.QHBoxLayout()
        upperLayout.addWidget(self.soilLabel)
        upperLayout.addStretch()
        upperLayout.addWidget(self.a45Label)
        upperLayout.addStretch()
        upperLayout.addWidget(openFileButton)
                
        #image layout
        imageLayout = QtWidgets.QHBoxLayout()
        imageLayout.addWidget(self.canvas) 

        #param layout
        soilNameLabel=QtWidgets.QLabel("&Soil Name")
        self.soilNameField=QtWidgets.QLineEdit()
        soilNameLabel.setBuddy(self.soilNameField)
        lonLabel=QtWidgets.QLabel("lo&ngitude")
        self.lonField=QtWidgets.QLineEdit()
        lonLabel.setBuddy(self.lonField)
        latLabel=QtWidgets.QLabel("la&titude")
        self.latField=QtWidgets.QLineEdit()
        latLabel.setBuddy(self.latField)
        #
        soilLayout = QtWidgets.QHBoxLayout()
        soilLayout.addWidget(soilNameLabel)
        soilLayout.addWidget(self.soilNameField)
        soilLayout.addWidget(lonLabel)
        soilLayout.addWidget(self.lonField)
        soilLayout.addWidget(latLabel)
        soilLayout.addWidget(self.latField)
        
        #buttons layout
        self.addButton=QtWidgets.QPushButton("ADD")
        self.addButton.setToolTip("add new soil in the database")
        self.modButton = QtWidgets.QPushButton("&MODIFY")
        self.modButton.setToolTip("modify soil in the database")
        self.remButton = QtWidgets.QPushButton("&REMOVE")
        self.remButton.setToolTip("remove soil from the database")
        self.plotButton = QtWidgets.QPushButton("&PLOT")
        self.plotButton.setToolTip("save soil curve as pdf")
        self.copyButton=QtWidgets.QPushButton("COPY")
        self.copyButton.setToolTip("copy soil to clipboard")
        
        self.resEdit = QtWidgets.QSpinBox()
        self.resEdit.setRange(0,1000)
        self.resEdit.setToolTip("Set resolution in nm of copied spectrum, 0 to keep original resolution")
        label = QtWidgets.QLabel('res. (nm)')
        label.setBuddy(self.resEdit)

        #
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.modButton)
        buttonLayout.addWidget(self.remButton)
        buttonLayout.addWidget(self.plotButton)
        buttonLayout.addWidget(self.copyButton)
        buttonLayout.addWidget(label)
        buttonLayout.addWidget(self.resEdit)
        buttonLayout.addStretch()

        
        #left layout
        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addLayout(upperLayout)
        leftLayout.addLayout(imageLayout)
        leftLayout.addLayout(soilLayout)
        leftLayout.addLayout(buttonLayout)
        #main layout
        self.setLayout(leftLayout)
        
        #connections
        openFileButton.clicked.connect(self.openButton_clicked) 
        self.addButton.clicked.connect(self.addButton_clicked)
        self.modButton.clicked.connect(self.modButton_clicked)
        self.remButton.clicked.connect(self.remButton_clicked)
        self.plotButton.clicked.connect(self.plotButton_clicked)
        self.copyButton.clicked.connect(self.copyButton_clicked)
        
    def clearAll(self):
        self._clearForm()
        self.soilListWidget.selectionModel().clear()
    

    def _clearForm(self):
        self.latField.clear()
        self.lonField.clear()
        self.soilNameField.clear()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis('off')
        self.figure.clear()
        self.canvas.draw() 
        self.plotted = False


    def _getCoordinates(self):
        # wymaga modyfikacji
        try:
            latValue =  float(self.latField.text())
        except ValueError:
            latValue = None
            
        try:
            lonValue =  float(self.lonField.text())
        except ValueError:
            lonValue = None
        
        return(latValue,lonValue)
    
    def openButton_clicked(self):   
        filetypes = "Excel (*.xls, *.xlsx);;Comma separated (*.csv)"
        
        fileName,_ = QtWidgets.QFileDialog.\
            getOpenFileName(self,"File to take spectrum from", self.inputDir,filetypes) #2B
        if fileName=="":
            return
        self.gl = soilSpectrum()
        warning = self.gl.importFromFile(fileName)
        if warning:
            self.warning(*warning)
            return
        soilFileName = os.path.basename(fileName)
        self._clearForm()
        ax = self.figure.add_subplot(111)
        self.gl.drawSpectrum(ax)
        self.canvas.draw()
        self.plotted = True
        self.soilLabel.setText("From file: {}".format(soilFileName))
        self.a45Label.setText("spectrum mod: {}".format(round(self.gl.spectra,6)))
        self.soilNameField.setText(self.gl.soilName)
        self.latField.setText(str(self.gl.coordinates[0]))
        self.lonField.setText(str(self.gl.coordinates[1]))       
        self.addButton.setEnabled(True)
        self.modButton.setEnabled(False)
        self.remButton.setEnabled(False)
        self.copyButton.setEnabled(False)
    
    def plotButton_clicked(self):
        if self.plotted ==False:
            self.warning("Nothing to plot",None)
            return
        
        filetypes = "pdf (*pdf);;png (*png);;svg (*svg)"
        fileName,fileType = QtWidgets.QFileDialog.\
            getSaveFileName(self,"File to plot results", self.outputDir,filetypes)
        if fileName=="":
            return

        file,ext = os.path.splitext(fileName)
        if ext not in ['.pdf','.png','.svg']:
            fileName = fileName+"."+fileType[:3]
        
        fig,ax = matplotlib.pyplot.subplots(1,1,figsize=(9,5),dpi=150)
        self.gl.drawSpectrum(ax,title=self.soilNameField.text())
        fig.savefig(fileName)
     
    def soil_clicked(self,soilName):
        soilPath = self._soilDatabase.getPath(soilName)
        soilData = pickle.load(open(soilPath,"rb"))
        self.gl = soilSpectrum()
        soilName,lat,lon = self.gl.importFromDatabase(soilData)
        self.latField.setText(str(lat))
        self.lonField.setText(str(lon))
        self.soilNameField.setText(soilName)
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)        
        self.gl.drawSpectrum(ax)
        self.canvas.draw()
        self.plotted = True
        self.soilLabel.setText("From database: {}".format(soilName))
        self.a45Label.setText("spectrum mod: {}".format(round(self.gl.spectra,6)))
        self.addButton.setEnabled(False)
        self.modButton.setEnabled(True)
        self.remButton.setEnabled(True)
        self.copyButton.setEnabled(True)
    
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
            self._clearForm()
            self._collections.reloadSoilDataModel()
            self.message("Soil {} added to database".format(soilName))
        return
    
    def remButton_clicked(self):
        soilName = self.soilNameField.text()
        warning = self._soilDatabase.removeFromDatabase(soilName)
        if warning:
            self.warning(*warning)
            return 
        self._collections.reloadSoilDataModel()
        self._clearForm()
        self.message("Soil {} removed".format(soilName))
        
    
    def modButton_clicked(self):
        soilName = self.soilNameField.text()
        coordinates = self._getCoordinates()
        soil = self.gl.exportSoil(soilName,*coordinates)
        if self.currentSoilName is None:
            return
        warning = self._soilDatabase.replaceSoil(self.currentSoilName,soil)
        if warning:
            self.warning(*warning)
            return
        self._collections.reloadSoilDataModel()
        self._clearForm()
        self.message("Soil {} modified".format(self.currentSoilName))
        self.currentSoilName = None

    def copyButton_clicked(self):
        soilName = self.soilNameField.text()
        soilData = self._soilDatabase.getSoil(soilName)
        resolution = self.resEdit.value()
        text = exportSoilToText(soilData,resolution)
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text, mode=cb.Clipboard)