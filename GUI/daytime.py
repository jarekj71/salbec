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
        
        self.day = QtWidgets.QSpinBox()
        self.day.setRange(0,365)
        # recalculate date into day of year
        self.__day_of_year = self.date.date().dayOfYear()
        self.day.setValue(self.dayOfYear)
        self.day.valueChanged.connect(self.dayChange)
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(this_label)
        mainLayout.addWidget(self.date)
        mainLayout.addWidget(self.day)
        self.setLayout(mainLayout)

    def dayChange(self):
        tmp_day = self.day.value()
        delta = tmp_day - self.__day_of_year
        tmp_date = self.date.date()
        tmp_date = tmp_date.addDays(delta)
        self.__day_of_year = tmp_day
        self.date.setDate(tmp_date)
        
    def setDay(self,day):
        #self.__day_of_year = day
        self.day.setValue(day)
    
    def dateChange(self):
        self.__day_of_year = self.date.date().dayOfYear()
        self.day.setValue(self.__day_of_year)
    
    @property
    def dayOfYear(self):
        return self.__day_of_year
    

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
        self.startDay.setDay(1)
        self.endDay.setDay(365)
        
    def dayButton_clicked(self):
        day = self.startDay.dayOfYear
        self.endDay.setDay(day)

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
        start = self.startDay.dayOfYear
        stop = self.endDay.dayOfYear
        if start>stop:
            self.warning("Start day cannot be later than end day")
            return None
        return start,stop,interval
