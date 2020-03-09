#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 15:54:05 2020

@author: jarekj
"""
from PyQt5 import QtCore, QtGui, QtWidgets
import os
class mapWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        #map
        self.div = 2 # jaki rozmiar i jaka mapa?
        assetmap = 'mapa{}.png'.format(self.div)
        self.image = QtGui.QImage(os.path.join('ASSETS',assetmap))
        pixmap =  QtGui.QPixmap( QtGui.QPixmap.fromImage(self.image))
        mapArea = QtWidgets.QLabel()
        mapArea.setFrameStyle(1)
        mapArea.setPixmap(pixmap)
        mapArea.setFixedSize(pixmap.width(),pixmap.height())
        mapArea.mousePressEvent = self.getCoords #connect to mouse position
        
        #coordinate panel
        bottomPanel = QtWidgets.QHBoxLayout()
        
        self.lambdaEdit = QtWidgets.QLineEdit()
        lambdaLabel = QtWidgets.QLabel("&lambda (longitude)")
        lambdaLabel.setBuddy(self.lambdaEdit)
        bottomPanel.addWidget(lambdaLabel)
        bottomPanel.addWidget(self.lambdaEdit)
        
        self.phiEdit = QtWidgets.QLineEdit()
        phiLabel = QtWidgets.QLabel("&phi (latitude)")
        phiLabel.setBuddy(self.phiEdit)
        bottomPanel.addWidget(phiLabel)
        bottomPanel.addWidget(self.phiEdit)

        setCoordsButton=QtWidgets.QPushButton("&Set")
        bottomPanel.addWidget(setCoordsButton)
        bottomPanel.addStretch()
                
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(mapArea)
        mainLayout.addLayout(bottomPanel)
        self.setLayout(mainLayout)

    def getLocation(self):
        return float(self.phiEdit.text()),float(self.lambdaEdit.text())
    
    def getCoords(self,event):
        x = event.pos().x()
        y = event.pos().y()
        self.lambdaEdit.setText(str(x/self.div-180))
        self.phiEdit.setText(str(90-y/self.div))
        c = self.image.pixel(x,y)
        col =  QtGui.QColor(c).getRgb()
        #print(c,col)