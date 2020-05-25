#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 19:28:02 2020

@author: jarek
"""

from PyQt5 import QtWidgets
import sys, os
filePath = os.path.abspath(__file__)
os.chdir(os.path.dirname(filePath))
from GUI.soilImporterDialog import soilImporterDialog
from GUI.curveFitWidget import curveFitWidget
from GUI.selectDaysWidget import selectDaysWidget
from GUI.latlonWidget import latlonWidget
from GUI.resultsWidget import resultsWidget
from GUI.setupDialog import setupDialog
from GUI.baseGui import baseGui
app=QtWidgets.QApplication(sys.argv)

#%%

class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1600,1024)
        #nazwa aplikacji
        
        self.base = baseGui()
        self.base.reset()
        self.soiImporter = soilImporterDialog()
        self.curveFit = curveFitWidget()
        self.coordsSet = latlonWidget()
        self.daysSelect = selectDaysWidget()
        self.results = resultsWidget()
        self.setup = setupDialog(self.base)
      
        inputLayout = QtWidgets.QHBoxLayout()
        inputLayout.addStretch()
        soilImporterButton = QtWidgets.QPushButton("&Add Soil")
        soilImporterButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Preferred)
        inputLayout.addWidget(soilImporterButton)
        inputLayout.addWidget(self.curveFit)
        inputLayout.addWidget(self.coordsSet)
        inputLayout.addWidget(self.daysSelect)
        runButton = QtWidgets.QPushButton("&RUN")
        runButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Preferred)
        inputLayout.addWidget(runButton)
        setButton = QtWidgets.QPushButton("&SETUP")
        setButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Preferred)
        inputLayout.addWidget(setButton)
        clsButton = QtWidgets.QPushButton("&CLOSE")
        clsButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Preferred)
        inputLayout.addWidget(clsButton)
        
        inputLayout.addStretch()
        
        #SIGNALS AND SLOTS
        soilImporterButton.clicked.connect(self.soilImporter_clicked)
        self.curveFit.coordSignal.connect(self.latlonWidgetSetCoords)
        self.coordsSet.setCoordinatesFromSoil(self.curveFit.coordinates())
        setButton.clicked.connect(self.setup_clicked)
        ##        
        runButton.clicked.connect(self.run)
        clsButton.clicked.connect(self.close)
        
        #output        
        outputLayout = QtWidgets.QHBoxLayout()
        outputLayout.addWidget(self.results)
        self.results.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Expanding)
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(outputLayout)
        mainLayout.addStretch()
        mainLayout.addLayout(inputLayout)
        
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        centralWidget.setLayout(mainLayout)
    
    def soilImporter_clicked(self):
        self.soiImporter.show()
        self.soiImporter.exec_()
        self.curveFit.refreshSoilCombo()
        
    def latlonWidgetSetCoords(self):
        self.coordsSet.setCoordinatesFromSoil(self.curveFit.coordinates())
        
    def setup_clicked(self):
        self.setup.show()
        self.setup.exec_()
        
        
    def run(self):
        if self.curveFit.getCurve() is None:
            self.curveFit.fitCurve()
        errors = self.daysSelect.getErrors()
        days = self.daysSelect.getDays()
        model = self.curveFit.getCurve()
        location = self.coordsSet.getCoordinates()
        soilParams = self.curveFit.getSoilParams()
        params = (location,model,days,errors,soilParams)
        for param in params:
            if type(param) == type(None):
                return

        self.results.runCalculation(*params)


if __name__ == '__main__':
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())
