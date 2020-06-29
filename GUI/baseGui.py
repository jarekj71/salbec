#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 10:27:10 2020

@author: jarek
"""
from PyQt5 import QtWidgets
import os

class baseGui():
    '''
    contains different functions and properties used across the program
    '''
    __inputDirectory = ""
    __outputDirectory = ""
 
    def __init__(self):
        pass
    
    def warning(self,message="",instruction=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        if instruction is not None:
            msg.setInformativeText(instruction)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
    
    def error(self,message=""):
        pass
    
    def message(self,message=""):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
        
    def validate_textEdit(self,bottom,upper,default,what=""):
        le = self.sender()
        if isinstance(le, QtWidgets.QLineEdit):
            try:
                value = float(le.text())
            except:
                self.warning("Wrong or missing {}".format(what))
                le.setText(str(default))
                le.setFocus()
                return
            if value < bottom or value > upper:
                extra = "{} must be between {} and {}".format(what,bottom,upper)
                self.warning("{} out of range".format(what),extra)
                le.setText(str(default))
                le.setFocus()
                return 
 
    def initIO(self):
        if self.isBase():
            self.setupfile = os.path.join(os.getcwd(),".SOILS","setup")
            self.readIO()
 
    def reset(self):
        if not self.isBase():
            return
        baseGui.__inputDirectory = os.getcwd()
        baseGui.__outputDirectory = os.getcwd()
        assets = 'ASSETS'
        if os.path.isdir(assets):
            baseGui.__inputDirectory = os.path.join(os.getcwd(),assets)
        self.writeIO(inputDir=True,outputDir=True)    

    def writeIO(self,inputDir=False,outputDir=False):
        if not self.isBase():
            return
        with open(self.setupfile,"r") as s:
            file_inputDirectory = s.readline()
            file_outputDirectory = s.readline()
        
        with open(self.setupfile,"w") as s:
            file_inputDirectory =  baseGui.__inputDirectory+"\n" if inputDir  else file_inputDirectory
            file_outputDirectory =   baseGui.__outputDirectory+"\n" if outputDir  else file_outputDirectory
            s.write(file_inputDirectory)
            s.write(file_outputDirectory)
    
    def readIO(self):
        if not self.isBase():
            return
        with open(self.setupfile,"r") as s:
            baseGui.__inputDirectory = s.readline().split("\n")[0] # remove sep
            baseGui.__outputDirectory = s.readline().split("\n")[0]
        if any(x=="" for x in (baseGui.__inputDirectory,baseGui.__outputDirectory)):
            self.reset()
        if not all(os.path.isdir(x) for x in (baseGui.__inputDirectory,baseGui.__outputDirectory)):
             self.reset()
                
    @property
    def inputDir(self):
        return baseGui.__inputDirectory
    
    @property
    def outputDir(self):
        return baseGui.__outputDirectory
    
    def setInputDir(self,directory):
        if self.isBase():
            baseGui.__inputDirectory = directory
            self.writeIO(inputDir=True)
        
    def setOutputDir(self,directory):
        if self.isBase():
            baseGui.__outputDirectory = directory
            self.writeIO(outputDir=True)
    
    def isBase(self):
        return self.__class__.__name__ == "baseGui"
    
