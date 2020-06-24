#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 15:55:55 2020

@author: jarekj
"""
#%%
from PyQt5 import QtWidgets
from PyQt5.QtCore import (pyqtSignal)
import pickle, os, sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

from soil import soilCurve, soilDatabase
from GUI.baseGui import baseGui

#%%
class curvePlot(QtWidgets.QDialog,baseGui):
    def __init__(self,curve=None):
        super().__init__()
        
        if curve is None:
            return
        
        #self.setFixedSize(600,500)
        self.setWindowTitle("Fitted curve")
        figure = Figure(figsize=(8,6))
        canvas = FigureCanvas(figure)
        mainLayout = QtWidgets.QVBoxLayout()
        imageLayout = QtWidgets.QHBoxLayout()
        descLayout = QtWidgets.QHBoxLayout()
        self.curve = curve

        #button Layout
        buttonLayout = QtWidgets.QHBoxLayout()
        self.headerCheck = QtWidgets.QCheckBox("Header")
        self.headerCheck.setToolTip("Copy also header data")        
        copyButton = QtWidgets.QPushButton("&COPY")
        plotButton = QtWidgets.QPushButton("&PLOT")
        closeButton = QtWidgets.QPushButton("&CLOSE")
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.headerCheck)
        buttonLayout.addWidget(copyButton)
        buttonLayout.addWidget(plotButton)
        buttonLayout.addWidget(closeButton)

        #image layout
        imageLayout.addWidget(canvas)

        #paramslayout
        self.soilParams = curve.get_soil_params()
        descLayout = QtWidgets.QVBoxLayout()
        text = ""
        for name,value in self.soilParams:
            if name =='a45':
                value = round(value,6)
            text += "   {}: {}".format(name,value)
        descLayout.addWidget(QtWidgets.QLabel(text))
            
        self.soilModel = curve.get_curve_model()
        text = ""
        for name,value in zip(['a','b','c','d'],self.soilModel):
            text += "   {}: {}".format(name,round(value,8))
        descLayout.addWidget(QtWidgets.QLabel(text))

        #main layout
        mainLayout.addLayout(buttonLayout)
        mainLayout.addLayout(imageLayout)
        mainLayout.addLayout(descLayout)
        self.setLayout(mainLayout)
        
        plotButton.clicked.connect(self.plotButton_clicked)
        closeButton.clicked.connect(self.reject)
        copyButton.clicked.connect(self.copyButton_clicked)

        figure.clear()
        ax = figure.add_subplot(111)
        self.curve.drawFitted(ax)
        canvas.draw()
    
    def plotButton_clicked(self):
        if self.curve is None:
            self._e.warning("Nothing to plot",None)
            return        
        filetypes = "pdf (*pdf);;png (*png);;svg (*svg)"
        fileName,fileType = QtWidgets.QFileDialog.\
            getSaveFileName(self,"File to plot results", self.outputDir,filetypes)
        if fileName=="":
            return
        
        file,ext = os.path.splitext(fileName)
        if ext not in ['.pdf','.png','.svg']:
            fileName = fileName+"."+fileType[:3]
        
        fig,ax = matplotlib.pyplot.subplots(1,1,figsize=(8,4),dpi=150)
        self.curve.drawFitted(ax)
        fig.savefig(fileName)
        
    def copyButton_clicked(self):
        line = ""
        header = ""
        for name,value in self.soilParams:
            if name =='a45':
                value = round(value,6)
            line += "{}\t".format(value)
            header+="{}\t".format(name)
        for value in self.soilModel:
            line += "{}\t".format(value)        
        
        header+="\t".join(['a','b','c','d'])
        text = line 
        if self.headerCheck.isChecked():
            text = header + os.linesep + line
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text, mode=cb.Clipboard)
       


class curveFitWidget(QtWidgets.QWidget):
    coordSignal = pyqtSignal()
    def __init__(self,collections):
        super().__init__()

        gridLayout = QtWidgets.QGridLayout()
        mainLayout = QtWidgets.QHBoxLayout()
        self._collections = collections
        self.curve = None
        self.modify = True
        self._soil = None
        
        #SOIL
        self.soilCombo = QtWidgets.QComboBox()
        self.soilCombo.setMinimumWidth(150)
        self.soilCombo.setModel(self._collections.selectionModel)
        self.soilCombo.currentTextChanged.connect(self.soilCombo_currentTextChanged)
        soilLabel = QtWidgets.QLabel('&Soil')
        soilLabel.setBuddy(self.soilCombo)
        
        gridLayout.addWidget(soilLabel,0,0)
        gridLayout.addWidget(self.soilCombo,1,0)
        
        #PARANS
        self.T3DEdit = QtWidgets.QLineEdit('1.5')
        self.T3DEdit.setMaximumWidth(40)
        label = QtWidgets.QLabel('&T3D')
        label.setBuddy(self.T3DEdit)
        gridLayout.addWidget(label,0,1)
        gridLayout.addWidget(self.T3DEdit,0,2)       
        
        self.HSDEdit = QtWidgets.QLineEdit('25')
        self.HSDEdit.setMaximumWidth(40)
        label = QtWidgets.QLabel('&HSD')
        label.setBuddy(self.HSDEdit)  
        gridLayout.addWidget(label,1,1)
        gridLayout.addWidget(self.HSDEdit,1,2)   
        
        pltButton = QtWidgets.QPushButton("&SHOW")
        pltButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Preferred)
        pltButton.setToolTip("Show fitted soil curve")
        pltButton.clicked.connect(self.plotCurve)
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(pltButton)
         
        self.setLayout(mainLayout)
        self.soilCombo_currentTextChanged()

       
    def coordinates(self):
        if self._soil is not None:
            return self._soil['coords']
        return None,None
        
    def soilCombo_currentTextChanged(self):
        soilName = self.soilCombo.currentText()
        if soilName =='':
            return
        soilPath = self._collections.getSoilsDatabase().getPath(soilName)
        self._soil = pickle.load(open(soilPath,"rb"))
        self.coordSignal.emit()
        self.curve = None

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
        self.curve.fit(self._soil['a45'],T3D,HSD,self._soil['name'])
        if self.modify:
            self.curve.modify_curve_parameters(b=-2/200)
        
    def plotCurve(self):
        self.fitCurve()
        curvePlotDialog = curvePlot(self.curve)
        curvePlotDialog.show()
        curvePlotDialog.exec_()
   
    def getCurve(self):
        if self.curve is None:
            return None
        return self.curve.get_curve_model()


    def getSoilParams(self):
        return self.curve.get_soil_params()     
