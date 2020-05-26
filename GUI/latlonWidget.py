#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 12:35:05 2020

@author: jarek
"""

from PyQt5 import QtGui, QtWidgets
import os
from GUI.baseGui import baseGui

class mapDialog(QtWidgets.QDialog,baseGui):
    def __init__(self):
        super().__init__()
        mainLayout = QtWidgets.QVBoxLayout()
        self.div = 2
        imagemap = 'world{}.png'.format(self.div)
        filepath = os.path.join("GUI",imagemap)
        image = QtGui.QImage(filepath)
        
        pixmap =  QtGui.QPixmap( QtGui.QPixmap.fromImage(image))
        mapArea = QtWidgets.QLabel()
        mapArea.setFrameStyle(1)
        mapArea.setPixmap(pixmap)
        mapArea.setFixedSize(pixmap.width(),pixmap.height())
        mapArea.mousePressEvent = self.getCoords #connect to mouse position
        mainLayout.addWidget(mapArea)
        self.setLayout(mainLayout)
        self.x = None
        self.y = None

    def getCoords(self,event):
        x = event.pos().x()
        y = event.pos().y()
        self.lon = x/self.div-180
        self.lat = 90-y/self.div
        self.accept()
        
class latlonWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        mainLayout = QtWidgets.QGridLayout()
        #LAT-LON
        self.latEdit = QtWidgets.QLineEdit()
        self.latEdit.setMaximumWidth(50)
        self.lonEdit = QtWidgets.QLineEdit()
        self.lonEdit.setMaximumWidth(50)
        label = QtWidgets.QLabel('latitude')
        label.setBuddy(self.latEdit)
        mainLayout.addWidget(label,1,0)
        label = QtWidgets.QLabel('longitude')
        label.setBuddy(self.lonEdit)
        mainLayout.addWidget(label,0,0)
        mainLayout.addWidget(self.lonEdit,0,1)
        mainLayout.addWidget(self.latEdit,1,1)
        #self.soilCombo_currentTextChanged() # wypełnienie watościami początkowymi
        
        self.blockCheck = QtWidgets.QCheckBox("&Block")
        self.blockCheck.setToolTip("Keep coordinates unchanged")
        mainLayout.addWidget(self.blockCheck,0,2)
        
        mapButton = QtWidgets.QPushButton("&MAP")
        mapButton.setToolTip("Select coordinages from map")
        mapButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        mainLayout.addWidget(mapButton,1,2)
        self.setLayout(mainLayout)
        mapButton.clicked.connect(self.mapButton_clicked)
    
    def setCoordinatesFromSoil(self,coords):
        if not self.blockCheck.isChecked:
            return # do nothin
        lon,lat=coords
        if lat is not None and lon is not None:
            self.latEdit.setText(str(lat))
            self.lonEdit.setText(str(lon))
    
    def mapButton_clicked(self):
        theMap = mapDialog()
        results = theMap.exec_()
        if not results:
            return
        if theMap.lat is not None:
            self.latEdit.setText(str(theMap.lat))
            self.lonEdit.setText(str(theMap.lon))
        del theMap
    
    def getCoordinates(self):
        try:
            lat = float(self.latEdit.text())
        except:
            self.warning("Wrong or missing latitude")
            return None
        try:    
            lon = float(self.lonEdit.text())
        except:
            self.warning("Wrong or missing longitude")
            return None
        return lat,lon
