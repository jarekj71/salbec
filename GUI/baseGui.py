#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 10:27:10 2020

@author: jarek
"""
from PyQt5 import QtWidgets
import os

class baseGui():
    
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
                print(value )
                extra = "{} must be between {} and {}".format(what,bottom,upper)
                self.warning("{} out of range".format(what),extra)
                le.setText(str(default))
                le.setFocus()
                return 
 
    def reset(self):
        baseGui.__inputDirectory = os.getcwd()
        baseGui.__outputDirectory = os.getcwd()
        assets = 'ASSETS'
        if os.path.isdir(assets):
            baseGui.__inputDirectory = os.path.join(os.getcwd(),assets)
   
    
    @property
    def inputDir(self):
        return baseGui.__inputDirectory
    
    @property
    def outputDir(self):
        return baseGui.__outputDirectory
    
    def setInputDir(self,directory):
        if self.isBase():
            baseGui.__inputDirectory = directory
        
    def setOutputDir(self,directory):
        if self.isBase():
            baseGui.__outputDirectory = directory
    
    def isBase(self):
        return self.__class__.__name__ == "baseGui"
    
