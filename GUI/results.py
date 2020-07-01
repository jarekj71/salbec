#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 09:24:22 2020

@author: jarek
"""

#%%
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QAbstractTableModel
import os

from albedo import albedo
from GUI.baseGui import baseGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

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
#%%
class timeSliderWidget(QtWidgets.QWidget,baseGui):
    def __init__(self,albedo):
        super().__init__()
        
        self.results = albedo.calculate_for_time_slider()
        minSlider = 0
        maxSlider = len(self.results['albedo'])-1
        center = int(maxSlider/2)
                
        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setMinimumWidth(300)
        self.slider.setMinimum(minSlider)
        self.slider.setMaximum(maxSlider)
        self.slider.setValue(center)
        
        copyButton = QtWidgets.QPushButton("COPY {} VALUES".format(os.linesep))
        
        self.slider.valueChanged.connect(self.slider_valueChanged)
        copyButton.clicked.connect(self.copyButton_clicked)

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
        mainLayout.addWidget(copyButton)
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
            
    def copyButton_clicked(self):
        text = "UTM,SLT,albedo"+os.linesep
        for utm,slt,albedo in zip(self.results["tUTM"],self.results["tSLT"],self.results["albedo"]):
            text += "{},{},{:0.5}{}".format(utm.strftime("%H:%M"),slt.strftime("%H:%M"),albedo,os.linesep)
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text, mode=cb.Clipboard)
#%%
class errorCurveDialog(QtWidgets.QDialog,baseGui):
    def __init__(self,albedo,plottitle,errorlist,description):
        super().__init__()
        
        self.setWindowTitle(plottitle)
        self.description = description
        self.record = None
        self.errorlist = errorlist
        self.plottitle = plottitle
        self.albedo = albedo
        
        figure = Figure(figsize=(8,9))
        canvas = FigureCanvas(figure)
        
        pdfButton = QtWidgets.QPushButton("PLOT")
        pdfButton.setToolTip("plot diagram")
        copyButton = QtWidgets.QPushButton("COPY")
        copyButton.setToolTip("copy parameters to clipboard")
        closeButton = QtWidgets.QPushButton("CLOSE")
        self.headerCheck = QtWidgets.QCheckBox("Header")
        self.headerCheck.setToolTip("Copy also header data")    

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
        buttonsLayout.addWidget(self.headerCheck)
        buttonsLayout.addWidget(copyButton)
        buttonsLayout.addWidget(pdfButton)
        buttonsLayout.addWidget(closeButton)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(buttonsLayout)
        mainLayout.addWidget(canvas)
        mainLayout.addLayout(sliderLayout)
        mainLayout.addLayout(descLayout)
        self.setLayout(mainLayout)
        closeButton.clicked.connect(self.accept) 
        copyButton.clicked.connect(self.copyButton_clicked)
        pdfButton.clicked.connect(self.pdfButton_clicked)
        
        figure.clear()
        self.albedo.plot_time_curve(figure,self.plottitle,self.errorlist)
        canvas.draw()  
        
    
    def setRecord(self,index):
        self.record = self.albedo.get_record(index)
    
    def copyButton_clicked(self):
        if self.record is None:
            self.warning("No record selected","Nothing copied")
            return
        header = self.record.index.values.tolist()
        header = [str(b) for b in header]
        line = self.record.values.tolist()
        line = [str(b) for b in line]
        header = "\t".join(header)
        line = "\t".join(line)
        header = header+"latitude \t longitude"
        line = line + "\t".join([str(self.albedo.location.latitude),str(self.albedo.location.longitude)])
        
        text = line
        if self.headerCheck.isChecked():
            text = header + os.linesep + line
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text, mode=cb.Clipboard)
        return

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
        self.albedo.plot_time_curve(figure=fileName,plottitle=self.plottitle,errorlist=self.errorlist)
        return
        
#%%

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
        self.errors = errors
        self.soilParams = soilParams+list(zip(["lat","lon"],self.location))
        
        self.a = albedo()
        self.a.load_parameters(soil_model,self.location)
        self.a.batch_mean_albedo_time(start_day=start_day,end_day=end_day,
                                                  interval=interval,errors=self.errors)
        
        self.data = self.a.get_data()
        dataModel  = pandasModel(self.data)
        self.resultsTable.setModel(dataModel)
        if self.data is not None:
            self.saveResultsButton.setEnabled(True)
            
     
    def viewClicked(self, index):
        if self.a is None:
            return
        row=index.row()
        day_of_year = self.data.iloc[row,0].item()
        self.a.store_current_date()
        self.a.set_date_by_day(day_of_year)
        curvePlot = errorCurveDialog(self.a,None,self.errors,self.soilParams)
        curvePlot.setRecord(row)
        curvePlot.show()
        curvePlot.exec_()
        self.a.restore_current_date()
  

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
