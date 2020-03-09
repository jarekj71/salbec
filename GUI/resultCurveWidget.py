#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 13:44:11 2020

@author: jarekj
"""
#%%
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
import os
import numpy as np
#%%


class resultCurveWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(5,4))
        self.canvas = FigureCanvas(self.figure)
        
        paramLayout = QtWidgets.QGridLayout()

        self.controls = {}
        params = ['Overaly1','Overlay2','Overaly3']
        self.param_values = {}
        for i,param in enumerate(params):
            lt = QtWidgets.QHBoxLayout()
            self.param_values[param] = 0
            self.controls[param] = QtWidgets.QCheckBox()
            self.controls[param].setChecked(False)
            self.controls[param].setText('&'+param)
            self.controls[param].stateChanged.connect(self.controlChange)
            lt.addWidget(self.controls[param])
            paramLayout.addLayout(lt,0,i)
        
        saveButton = QtWidgets.QPushButton('&Save')
        paramLayout.addWidget(saveButton,0,i+1)
        #saveButton.clicked.connect(self.savePlot)

        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.canvas)
        mainLayout.addLayout(paramLayout)
        self.setLayout(mainLayout)

    def controlChange(self):
        pass
