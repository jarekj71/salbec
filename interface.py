#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 19:28:02 2020

@author: jarek
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
os.chdir('/home/jarekj/Dropbox/PROJEKTY/albedo')
from GUI.mapWidget import mapWidget
from GUI.curveWidget import curveWidget
from GUI.resultsWidget import resultsWidget
from GUI.resultCurveWidget import resultCurveWidget


app=QtWidgets.QApplication(sys.argv)

#%%
class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1600,1024)
        
        mapAreaWidget = mapWidget()
        curveAreaWidget = curveWidget()
        resultsAreaWidget = resultsWidget()
        resultCurveAreaWidget = resultCurveWidget()
        resultsAreaWidget.connect(mapAreaWidget,curveAreaWidget)
        resultsAreaWidget.connect_plot(resultCurveAreaWidget)
        
        inputLayout = QtWidgets.QHBoxLayout()
        inputLayout.addWidget(mapAreaWidget)
        inputLayout.addWidget(curveAreaWidget)
        
        outputLayout = QtWidgets.QHBoxLayout()
        outputLayout.addWidget(resultsAreaWidget)
        outputLayout.addWidget(resultCurveAreaWidget)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(outputLayout)
        mainLayout.addLayout(inputLayout)
        
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        centralWidget.setLayout(mainLayout)
    
window = mainWindow()
window.show()
sys.exit(app.exec_())
