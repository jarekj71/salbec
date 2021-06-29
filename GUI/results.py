#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 09:24:22 2020

@author: jarek
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QAbstractTableModel
import os
import pandas as pd

from diurnalalbedo import albedo, batch_albedo_main_times
from GUI.baseGui import baseGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

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

class timeSliderWidget(QtWidgets.QWidget,baseGui):
    def __init__(self,albedo):
        super().__init__()
        
        self.results = albedo.time_slider()
        self.albedo = albedo
        minSlider = 0
        maxSlider = len(self.results['albedo'])-1
        center = int(maxSlider/2)
                
        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setMinimumWidth(300)
        self.slider.setMinimum(minSlider)
        self.slider.setMaximum(maxSlider)
        self.slider.setValue(center)
        
        self.slider.valueChanged.connect(self.slider_valueChanged)

        sunriseUTM = QtWidgets.QLabel(self.results['utc_sunrise_time'].strftime("%H:%M"))
        sunsetUTM = QtWidgets.QLabel(self.results['utc_sunset_time'].strftime("%H:%M"))
        
        sunriseSLT = QtWidgets.QLabel(self.results['slt_sunrise_time'].strftime("%H:%M"))
        sunsetSLT = QtWidgets.QLabel(self.results['slt_sunset_time'].strftime("%H:%M"))
        
        self.currentAlbedoText = "Albedo: {:0.5}".format(self.results['albedo'][center])
        self.currentUTMText = "UTM: {}".format(self.results['tUTM'][center].strftime("%H:%M"))
        self.currentSLTText = "SLT: {}".format(self.results['tSLT'][center].strftime("%H:%M"))
        
        self.currentAlbedoLabel = QtWidgets.QLabel(self.currentAlbedoText)
        self.currentUTMLabel = QtWidgets.QLabel(self.currentUTMText)
        self.currentSLTLabel = QtWidgets.QLabel(self.currentSLTText)
        
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.addWidget(self.currentAlbedoLabel,0,1,alignment=Qt.AlignCenter)
                
        gridLayout.addWidget(QtWidgets.QLabel("Sunrise"),1,0)
        gridLayout.addWidget(self.slider,1,1)
        gridLayout.addWidget(QtWidgets.QLabel("Sunset"),1,2)
        
        gridLayout.addWidget(sunriseUTM,2,0)
        gridLayout.addWidget(self.currentUTMLabel,2,1,alignment=Qt.AlignCenter)
        gridLayout.addWidget(sunsetUTM,2,2)
        
        gridLayout.addWidget(sunriseSLT,3,0)
        gridLayout.addWidget(self.currentSLTLabel,3,1,alignment=Qt.AlignCenter)
        gridLayout.addWidget(sunsetSLT,3,2)
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(gridLayout)
        mainLayout.addStretch()
        self.setLayout(mainLayout)
        
    def slider_valueChanged(self):
        position = self.slider.value()
        self.currentAlbedoText = "Albedo: {:0.5}".format(self.results['albedo'][position])
        self.currentUTMText = "UTM: {}".format(self.results['tUTM'][position].strftime("%H:%M"))
        self.currentSLTText = "SLT: {}".format(self.results['tSLT'][position].strftime("%H:%M"))
        self.currentAlbedoLabel.setText(self.currentAlbedoText)
        self.currentUTMLabel.setText(self.currentUTMText)
        self.currentSLTLabel.setText(self.currentSLTText)        

class errorCurveDialog(QtWidgets.QDialog,baseGui):
    def __init__(self,albedo,plottitle,description):
        super().__init__()
        
        self.setWindowTitle(plottitle)
        self.description = description
        self.plottitle = plottitle
        self.albedo = albedo
        
        figure = Figure(figsize=(8,9))
        canvas = FigureCanvas(figure)
        
        pdfButton = QtWidgets.QPushButton("PLOT")
        pdfButton.setToolTip("plot diagram")
        exportButton = QtWidgets.QPushButton("EXPORT")
        exportButton.setToolTip("export curve values to excel")
        closeButton = QtWidgets.QPushButton("CLOSE")

        sliderWidget = timeSliderWidget(self.albedo)
        sliderLayout = QtWidgets.QHBoxLayout()
        sliderLayout.addWidget(sliderWidget)
        
        descLayout = QtWidgets.QHBoxLayout()
        
        for i,(name,value) in enumerate(description):
            if name =='\u03b145':
                value = round(value,4)
            text = "{}: {}".format(name,value)
            descLayout.addWidget(QtWidgets.QLabel(text))
           
        if self.plottitle is None:
            titleText = "{}:{}  {}:{}  {}:{:0.3}  {}:{:0.3}  {}:{:0.3}".format(*sum(description[1:],())) #trick unpack nested tuple
            self.plottitle = titleText
 

        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(exportButton)
        buttonsLayout.addWidget(pdfButton)
        buttonsLayout.addWidget(closeButton)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(buttonsLayout)
        mainLayout.addWidget(canvas)
        mainLayout.addLayout(sliderLayout)
        mainLayout.addLayout(descLayout)
        self.setLayout(mainLayout)
        closeButton.clicked.connect(self.accept) 
        pdfButton.clicked.connect(self.pdfButton_clicked)
        exportButton.clicked.connect(self.exportButton_clicked)
        
        figure.clear()
        self.albedo.plot_time_curve(figure,self.plottitle)
        canvas.draw()  
    
    def exportButton_clicked(self):
        times = self.albedo.times_DataFrame()
        parameters = self.albedo.get_record(header=True)
       
        filetypes = "Excel (*.xlsx)"
        fileName,_ = QtWidgets.QFileDialog.\
            getSaveFileName(self,"File to save results", self.outputDir,filetypes) 
 
        if fileName=="":
            return
        file,ext = os.path.splitext(fileName)
   
        if ext != '.xlsx':
            fileName = fileName+'.xlsx'

        writer = pd.ExcelWriter(fileName)
        times.to_excel(writer,sheet_name='curve')   
        parameters.to_excel(writer,sheet_name='parameters')
        writer.save()
        self.message("File {} exported".format(os.path.basename(fileName)))

    def pdfButton_clicked(self):
        if self.albedo is None:
            self.warning("Nothing to plot",None)
            return
        filetypes = "pdf (*pdf);;png (*png);;svg (*svg)"
        fileName,fileType = QtWidgets.QFileDialog.\
            getSaveFileName(self,"File to plot results", self.outputDir,filetypes)
        if fileName=="":
            return
        file,ext = os.path.splitext(fileName)
        
        if ext not in ['.pdf','.png','.svg']:
            fileName = fileName+"."+fileType[:3]
        self.albedo.plot_time_curve(fileName,self.plottitle)
        self.message("File {} plotted".format(os.path.basename(fileName)))
        return

class resultsWidget(QtWidgets.QWidget,baseGui):
    def __init__(self):
        super().__init__()
       
        self.resultsTable = QtWidgets.QTableView()
        self.resultsTable.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resultsTable.setMinimumHeight(820)
        self.resultsTable.clicked.connect(self.viewClicked)
       
        self.saveResultsButton = QtWidgets.QPushButton("EXPORT")
        titleResultsLabel = QtWidgets.QLabel("Results of processing")
        
        ButtonsLayout = QtWidgets.QHBoxLayout()
        ButtonsLayout.addStretch()
        ButtonsLayout.addWidget(titleResultsLabel)
        ButtonsLayout.addWidget(self.saveResultsButton)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(ButtonsLayout)
        mainLayout.addWidget(self.resultsTable)
        self.setLayout(mainLayout)
        self.data = None
        if self.data is None:
            self.saveResultsButton.setEnabled(False)
        self.saveResultsButton.clicked.connect(self.exportExcel_clicked)    
    

    def runCalculation(self,location,model,days,errors,soilParams):
        self.location = location
        soil_model = model
        start_day,end_day,interval = days
        self.soilParams = soilParams+list(zip(["lat","lon"],self.location))
        
        self.albedo = albedo()
        self.albedo.load_parameters(soil_model,self.location,errors)
        self.data = batch_albedo_main_times(self.albedo,start_day=start_day,end_day=end_day,
                                                  interval=interval)
        if self.data is None:
            self.warning("No days with sunrise and sunset")
            return
        dataModel  = pandasModel(self.data)
        self.resultsTable.setModel(dataModel)
        if self.data is not None:
            self.saveResultsButton.setEnabled(True)
       
     
    def viewClicked(self, index):
        if self.albedo is None:
            return
        row=index.row()
        dayOfYear = self.data.iloc[row,0].item()
        self.albedo.set_date_by_day(dayOfYear)
        #print(row)
        #record = self.data.iloc[row].copy()
        curvePlot = errorCurveDialog(self.albedo,None,self.soilParams)
        curvePlot.show()
        curvePlot.exec_()

    def exportExcel_clicked(self):
        if self.data is None:
            self.warning("There is no data to export","Run analysis first")
        
        filetypes = "Excel (*.xlsx)"
        fileName,_ = QtWidgets.QFileDialog.\
            getSaveFileName(self,"File to save results", self.outputDir,filetypes) 
        if fileName=="":
            return
        file,ext = os.path.splitext(fileName)
   
        if ext != '.xlsx':
            fileName = fileName+'.xlsx'
        self.data.to_excel(fileName)
        self.message("{} Exported".format(os.path.basename(fileName)))
