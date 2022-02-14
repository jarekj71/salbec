#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 10:45:45 2020

@author: jarek
"""


from PyQt5 import QtWidgets, QtCore
from GUI.baseGui import baseGui

class selectDayWidget(QtWidgets.QWidget,baseGui):
    def __init__(self,label=""):
        super().__init__()
       
        self.date = QtWidgets.QDateEdit()
        self.date.setDateTime(QtCore.QDateTime.currentDateTime())
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setCalendarPopup(True)
        this_label = QtWidgets.QLabel("&"+label)
        this_label.setBuddy(self.date)
        self.date.dateChanged.connect(self.dateChange)
        self.__day_of_year = self.date.date().dayOfYear()
        self.dayofyearLabel = QtWidgets.QLabel(self.dayDOI)
        
        # recalculate date into day of year
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(this_label)
        mainLayout.addWidget(self.date)
        mainLayout.addWidget(self.dayofyearLabel)
        self.setLayout(mainLayout)
      
    def dateChange(self):
        self.__day_of_year = self.date.date().dayOfYear()
        self.dayofyearLabel.setText(self.dayDOI)
    
    def setDate(self,date):
        self.date.setDate(date)
        
    def getDate(self):
        return self.date.date()
    
    @property
    def dayDOI(self):
        return str(self.__day_of_year)+" DOI"
    
    @property
    def dayOfYear(self):
        return self.__day_of_year
    
    @property 
    def year(self):
        return self.date.date().year()
    

class selectDaysWidget(QtWidgets.QWidget,baseGui):
    def __init__(self):
        super().__init__()
        
        mainLayout = QtWidgets.QGridLayout()
        self.startDay = selectDayWidget("Start day")
        self.endDay = selectDayWidget("End day")
        mainLayout.addWidget(self.startDay,0,0)
        mainLayout.addWidget(self.endDay,1,0)
        
        yearButton = QtWidgets.QPushButton("&YEAR")
        yearButton.setToolTip("Entire year")
        yearButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        yearButton.clicked.connect(self.yearButton_clicked)
        mainLayout.addWidget(yearButton,0,1)
        
        dayButton = QtWidgets.QPushButton("&DAY")
        dayButton.setToolTip("Reset to one (start) day")
        dayButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        dayButton.clicked.connect(self.dayButton_clicked)
        mainLayout.addWidget(dayButton,1,1)

        self.breakEdit = QtWidgets.QSpinBox()
        self.breakEdit.setRange(1,14)
        label = QtWidgets.QLabel('break')
        label.setBuddy(self.breakEdit)
        mainLayout.addWidget(label,0,2)
        mainLayout.addWidget(self.breakEdit,0,3)
        
        self.errorsBox = QtWidgets.QLineEdit()
        self.errorsBox.setMaximumWidth(70)
        self.errorsBox.setText('2,3,5')
        label = QtWidgets.QLabel('Errors (%)')
        label.setBuddy(self.errorsBox)
        mainLayout.addWidget(label,1,2)
        mainLayout.addWidget(self.errorsBox,1,3)

        self.setLayout(mainLayout)

    def yearButton_clicked(self):
        year = self.startDay.year 
        startDay = QtCore.QDate(year,1,1)
        self.startDay.setDate(startDay)
        endDay = QtCore.QDate(year,12,31)
        self.endDay.setDate(endDay)
        
        
    def dayButton_clicked(self):
        date = self.startDay.getDate()
        self.endDay.setDate(date)

    def getErrors(self):
        if self.errorsBox.text() == "":
            return []
        errors = self.errorsBox.text().split(",")
        try:
            errors = [float(error)/100 for error in errors]
            errors.sort()
        except:
            self.warning("Wrong values of errors")
            return None
        return errors

    def getDays(self):
        interval = self.breakEdit.value()
        #start = self.startDay.dayOfYear
        #stop = self.endDay.dayOfYear
        start = self.startDay.getDate()
        stop = self.endDay.getDate()
        
        if start>stop:
            self.warning("Start day cannot be later than end day")
            return None
        return start.toPyDate(),stop.toPyDate(),interval
