#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 15:55:55 2020

@author: jarekj
"""
#%%
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
import pickle, os, matplotlib
import numpy as np
from PROC.soil import soilCurve

#https://stackoverflow.com/questions/32636362/pyqt-and-embedding-matplotlib-graph-not-showing

#%%
class curveWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.figure = Figure(figsize=(6,4))
        self.canvas = FigureCanvas(self.figure)
        self.load_models()
        self.curve = None
        
        #abcd modifiers
        paramLayout = QtWidgets.QGridLayout()
        
        
        self.controls = {}
        params = ['a','b','c','d']
        self.param_values = {}
        for i,param in enumerate(params):
            lt = QtWidgets.QHBoxLayout()
            self.param_values[param] = 0
            #self.controls[param] = QtWidgets.QDoubleSpinBox()
            self.controls[param] = QtWidgets.QSlider(Qt.Horizontal)
            
            self.controls[param].setRange(-50,50)
            self.controls[param].setValue(0)
            self.controls[param].setEnabled(False)
            self.controls[param].valueChanged.connect(self.controlChange)
            label = QtWidgets.QLabel('&'+param)
            label.setBuddy(self.controls[param])
            lt.addWidget(label)
            lt.addWidget(self.controls[param])
            paramLayout.addLayout(lt,i,0)
        
        resetButton = QtWidgets.QPushButton('&Reset')
        paramLayout.addWidget(resetButton,i+1,0)    
        resetButton.clicked.connect(self.resetParams)
        # abcd modifiers
        
        #model curve
        modelCurveLayout = QtWidgets.QGridLayout()
        
        #soil combo box
        self.soilCombo = QtWidgets.QComboBox()
        self.soilCombo.addItems(self.GL.keys())
        label = QtWidgets.QLabel('&Soil')
        label.setBuddy(self.soilCombo)
        lt = QtWidgets.QHBoxLayout()
        lt.addWidget(label)
        lt.addWidget(self.soilCombo)
        modelCurveLayout.addLayout(lt,0,0)
        
        #T3D
        self.T3DEdit = QtWidgets.QLineEdit('1.5')
        label = QtWidgets.QLabel('&T3D')
        label.setBuddy(self.T3DEdit)
        lt = QtWidgets.QHBoxLayout()
        lt.addWidget(label)
        lt.addWidget(self.T3DEdit)
        modelCurveLayout.addLayout(lt,0,1)
        
        #HSD
        self.HSDEdit = QtWidgets.QLineEdit('25')
        label = QtWidgets.QLabel('&HSD')
        label.setBuddy(self.HSDEdit)
        lt = QtWidgets.QHBoxLayout()
        lt.addWidget(label)
        lt.addWidget(self.HSDEdit)
        modelCurveLayout.addLayout(lt,0,2)
        
        #draw curve
        fitButton = QtWidgets.QPushButton('&Fit')
        fitButton.clicked.connect(self.fitCurve)
        modelCurveLayout.addWidget(fitButton,0,3)
        
        
        curveLayout = QtWidgets.QVBoxLayout()
        curveLayout.addWidget(self.canvas)
        curveLayout.addLayout(modelCurveLayout)
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(curveLayout)
        mainLayout.addLayout(paramLayout)
        self.setLayout(mainLayout)
        
            
    def controlChange(self):
        max_val = np.exp(np.sqrt(50))
        for param,control in self.controls.items():
            value = control.value()
            self.param_values[param] = np.sign(value)*np.exp(np.sqrt(np.abs(value)))/max_val
        self.__plotFigure()
        
    
    def resetParams(self):
        if self.curve is None:
            return
        for param,control in self.controls.items():
            control.setEnabled(True)
            control.setValue(0)
            self.param_values[param] = 0
    
    def fitCurve(self):
        try:
            T3D = float(self.T3DEdit.text())
        except ValueError:
            self.T3DEdit.clear()
            return
        
        try:
            HSD = float(self.HSDEdit.text())
        except ValueError:
            self.HSDEdit.clear()
            return
        
        self.curve = soilCurve()
        soil = self.soilCombo.currentText()
        self.curve.fit(self.GL[soil],T3D,HSD)
        self.__plotFigure()
        self.resetParams()
        
    def __plotFigure(self):
        if self.curve is None:
            return
               
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.curve.modify_curve_parameters(**self.param_values)
        self.curve.plot(ax)
        self.canvas.draw()
        
    def getCurve(self):
        return self.curve.get_curve_model()
    
    def load_models(self):
        self.GL = pickle.load(open(os.path.join("ASSETS","a45.p"),"rb"))
                