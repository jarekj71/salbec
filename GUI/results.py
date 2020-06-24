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
class errorCurveDialog(QtWidgets.QDialog,baseGui):
    def __init__(self,albedo,plottitle,errorlist,description):
        super().__init__()
        
        self.setWindowTitle(plottitle)
        self.description = description
        self.record = None
        self.errorlist = errorlist
        self.plottitle = plottitle
        
        figure = Figure(figsize=(8,9))
        canvas = FigureCanvas(figure)
        
        pdfButton = QtWidgets.QPushButton("PLOT")
        pdfButton.setToolTip("plot diagram")
        copyButton = QtWidgets.QPushButton("COPY")
        copyButton.setToolTip("copy parameters to clipboard")
        closeButton = QtWidgets.QPushButton("CLOSE")
        self.headerCheck = QtWidgets.QCheckBox("Header")
        self.headerCheck.setToolTip("Copy also header data")    

        
        descLayout = QtWidgets.QHBoxLayout()
        for i,(name,value) in enumerate(description):
            if name =='a45':
                value = round(value,4)
            text = "{}:{}".format(name,value)
            descLayout.addWidget(QtWidgets.QLabel(text))
        
        
        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.headerCheck)
        buttonsLayout.addWidget(copyButton)
        buttonsLayout.addWidget(pdfButton)
        buttonsLayout.addWidget(closeButton)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(buttonsLayout)
        mainLayout.addWidget(canvas)
        mainLayout.addLayout(descLayout)
        self.setLayout(mainLayout)
        closeButton.clicked.connect(self.accept) 
        copyButton.clicked.connect(self.copyButton_clicked)
        
        figure.clear()
        self.albedo = albedo
        self.albedo.plot_time_curve(figure,self.plottitle,self.errorlist)
        canvas.draw()  
        
    
    def setRecord(self,index):
        self.record = self.albedo.get_record(index)

    
    def copyButton_clicked(self):
        if self.record is None:
            self._e.warning("No record selected","Nothing copied")
            return
        header = self.record.index.values.tolist()
        header = [str(b) for b in header]
        line = self.record.values.tolist()
        line = [str(b) for b in line]
        header = "\t".join(header)
        line = "\t".join(line)
        header = header+"latitude \t longitude"
        #line = line + "\t".join([str(b) for b in self.albedo.location])
        line = line + "\t".join([str(self.albedo.location.latitude),str(self.albedo.location.longitude)])
        
        text = line
        if self.headerCheck.isChecked():
            text = header + os.linesep + line
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text, mode=cb.Clipboard)
        return
        

    def drawButton_clicked(self):
        if self.albedo is None:
            self._e.warning("Nothing to plot",None)
            return
        filetypes = "pdf (*pdf);;png (*png);;svg (*svg)"
        fileName,fileType = QtWidgets.QFileDialog.\
            getSaveFileName(self,"File to plot results", self.inputDir,filetypes)
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
        self.soilParams = soilParams+list(zip(["latitude","longitude"],self.location))
        
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
        curvePlot = errorCurveDialog(self.a,"tytuł",self.errors,self.soilParams)
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
