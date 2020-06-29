#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 10:43:48 2020

@author: jarek
"""

#%%
import os, sys
from PyQt5 import QtWidgets

class setupDialog(QtWidgets.QDialog): 
    def __init__(self,base):
        super().__init__()
        self.setFixedSize(600,500)
        self.setWindowTitle("Setup Window")
        
        self.base = base
        self.current = os.getcwd()
        
        self.inputLabel = QtWidgets.QLabel(self.base.inputDir)
        inputSet = QtWidgets.QPushButton("SET")
        inputSet.clicked.connect(self.setInput)

        inputLayout = QtWidgets.QHBoxLayout()
        inputLayout.addWidget(self.inputLabel)
        inputLayout.addStretch()
        inputLayout.addWidget(inputSet)
        inputBox = QtWidgets.QGroupBox("Input directory")
        inputBox.setLayout(inputLayout)

        self.outputLabel = QtWidgets.QLabel(self.base.outputDir)
        outputSet = QtWidgets.QPushButton("SET")
        outputSet.clicked.connect(self.setOutput)
        
        outputLayout = QtWidgets.QHBoxLayout()
        outputLayout.addWidget(self.outputLabel)
        outputLayout.addStretch()
        outputLayout.addWidget(outputSet)    
        outputBox = QtWidgets.QGroupBox("Output directory")
        outputBox.setLayout(outputLayout)
              
        buttonLayout = QtWidgets.QHBoxLayout()
        resetButton = QtWidgets.QPushButton("RESET")
        resetButton.setToolTip("reset paths to defaults")
        closeButton = QtWidgets.QPushButton("&CLOSE")
        buttonLayout.addStretch()
        buttonLayout.addWidget(resetButton)
        buttonLayout.addWidget(closeButton)
        
        resetButton.clicked.connect(self.reset_clicked)
        closeButton.clicked.connect(self.accept)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(inputBox)
        mainLayout.addWidget(outputBox)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addStretch()
        self.setLayout(mainLayout)
        
    def setInput(self):
        dirName = QtWidgets.QFileDialog.\
            getExistingDirectory(self,"Select directory",self.current) #2B        
        self.base.setInputDir(dirName)
        self.inputLabel.setText(self.base.inputDir)
        
    def setOutput(self):
        dirName = QtWidgets.QFileDialog.\
            getExistingDirectory(self,"Select directory",self.current) #2B        
        self.base.setOutputDir(dirName)
        self.outputLabel.setText(self.base.outputDir)
        
    def reset_clicked(self):
        self.base.reset()
        self.inputLabel.setText(self.base.inputDir)
        self.outputLabel.setText(self.base.outputDir)
