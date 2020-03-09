#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 18:06:59 2020

@author: jarekj
"""
#%%
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QAbstractTableModel
import pandas as pd
import numpy as np
from PROC.albedo import albedo
#%%
class pandasModel(QAbstractTableModel):
    def __init__(self, pData, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = pData

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]
    
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                v = self._data.iloc[index.row()][index.column()]
                #v = np.round(v,3) if index.column() == 2 else v
                return str(v)
        return None    

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None    


class selectDayWidget(QtWidgets.QWidget):
    def __init__(self,label):
        super().__init__()
        
        self.a = None
        self.plot = None
        
        self.date = QtWidgets.QDateEdit()
        self.date.setDateTime(QtCore.QDateTime.currentDateTime())
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setCalendarPopup(True)
        this_label = QtWidgets.QLabel("&"+label)
        this_label.setBuddy(self.date)
        self.date.dateChanged.connect(self.date_change)
        
        self.day = QtWidgets.QSpinBox()
        self.day.setRange(0,366)
        # recalculate date into day of year
        self.__day_of_year = self.date.date().dayOfYear()
        self.day.setValue(self.day_of_year)
        self.day.valueChanged.connect(self.day_change)
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(this_label)
        mainLayout.addWidget(self.date)
        mainLayout.addWidget(self.day)
        self.setLayout(mainLayout)

    
    def day_change(self):
        tmp_day = self.day.value()
        delta = tmp_day - self.day_of_year
        tmp_date = self.date.date()
        tmp_date = tmp_date.addDays(delta)
        self.__day_of_year = tmp_day
        self.date.setDate(tmp_date)
        
    def date_change(self):
        self.__day_of_year = self.date.date().dayOfYear()
        self.day.setValue(self.day_of_year)
    
    @property
    def day_of_year(self):
        return self.__day_of_year

class resultsWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.results = QtWidgets.QTableView()
        self.results.clicked.connect(self.viewClicked)

        self.startDay = selectDayWidget("Start day")
       
        self.batchDatesBox = QtWidgets.QCheckBox('&Range')
        self.batchDatesBox.setChecked(False)
        self.batchDatesBox.stateChanged.connect(self.batchDates)
        
        self.entireYearBox = QtWidgets.QCheckBox('&Year')
        self.entireYearBox.setChecked(False)
        self.entireYearBox.stateChanged.connect(self.entireYear)
        

        self.errors = QtWidgets.QLineEdit()
        self.errors.setText('0.01,0.02,0.05')
        
        errorsLabel = QtWidgets.QLabel("&Errors")
        errorsLabel.setBuddy(self.errors)
        
        calcButton = QtWidgets.QPushButton('Ru&n')
        calcButton.clicked.connect(self.runCalculation)

       #Build layout
        mainLayout = QtWidgets.QVBoxLayout()
        lt = QtWidgets.QHBoxLayout()

        lt.addWidget(self.startDay)
        lt.addWidget(self.batchDatesBox)
        lt.addWidget(self.entireYearBox)
        
        lt.addWidget(errorsLabel)
        lt.addWidget(self.errors)
        lt.addWidget(calcButton)
        
        
        mainLayout.addLayout(lt)
        mainLayout.addWidget(self.results)
        self.setLayout(mainLayout)
    
    def parseErrors(self):
        errors = self.errors.text().split(",")
        return [float(error) for error in errors]

    def batchDates(self):
        pass
    
    def entireYear(self):
        pass
    
    def connect(self,locationWidget,curveWidget):
        self.location = locationWidget
        self.soil_curve = curveWidget
        
    def viewClicked(self, index):
        if self.a is None or self.plot is None:
            return
        row=index.row()
        day_of_year = self.data.iloc[row,0].item()
        self.plot.figure.clear()
        ax = self.plot.figure.add_subplot(111)
        self.a.plot_curve(ax,day_of_year)
        self.plot.canvas.draw()

    def connect_plot(self,plotWidget):
        self.plot = plotWidget
    
    def runCalculation(self):
        start_day = end_day = int(self.startDay.day_of_year)
        location = self.location.getLocation()
        soil_curve = self.soil_curve.getCurve()
        self.errors = self.parseErrors()
        self.a = albedo()
        self.a.load_parameters(soil_curve,location)
        self.data = self.a.batch_mean_albedo_time(start_day=start_day,end_day=end_day,interval=1,errors=self.errors)
        model  = pandasModel(self.data)
        self.results.setModel(model)
    

