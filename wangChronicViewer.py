from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMainWindow, QDialog, QPushButton, QComboBox, QTextEdit, QMessageBox
from pyqtgraph import PlotWidget, GraphicsLayoutWidget, plot
import pyqtgraph as pg
import numpy as np
from wangSpikeSorterWidgets import Dialog_plot, Dialog_getTextValue, Dialog_CombineChannel, MultiLine, Ui_MainWindow
from wangSpikeSorterCPU import SpikeSorterCPU
from random import sample, randint
from sys import platform

class Ui_viewer(QMainWindow):
    n_maxunit = 6
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent = parent)
        self.cpu = SpikeSorterCPU()
    def getwindowsizes(self):
        sz = {'mainwindow':(1250, 850), \
            'group_units': (10,10,1220,820),\
            'graphicsView_units':(10,10,1200,800)}
        ratio = self.ratio
        for i, j in sz.items():
            sz[i] = [(ratio * k) for k in j]
        return sz
    def my_QtCore_QRect(self, x):
        return QtCore.QRect(x[0], x[1], x[2], x[3])
    def setup_UI(self):
        MainWindow = self
        sz = self.getwindowsizes()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(sz['mainwindow'][0],sz['mainwindow'][1])
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.group_Units = QtWidgets.QGroupBox(self.centralwidget)
        self.group_Units.setGeometry(self.my_QtCore_QRect(sz['group_units']))
        self.group_Units.setObjectName("group_Units")
        self.graphicsView_units = GraphicsLayoutWidget(self.group_Units)
        self.graphicsView_units.setGeometry(self.my_QtCore_QRect(sz['graphicsView_units']))
        self.graphicsView_units.setObjectName("graphicsView_units")
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.group_Units.setTitle(_translate("MainWindow", "Neurons"))
    def setup_viewer(self, nrow, nfig, color_unit, ratio = 2):
        self.ratio = ratio
        self.nrow = nrow
        self.setup_UI()
        self.graphicsView_units.setBackground('w')
        ncol = int(np.ceil(nfig/nrow))
        self.ncol = ncol
        self.units_axes = []
        for uj in range(2*nrow):
            for ui in range(ncol):
                te = self.graphicsView_units.addPlot(row = uj, col = ui)
                # te.setAspectLocked(lock=False)
                # self.graphicsView_units.addViewBox(row = uj, col = ui)
                self.units_axes.append(te)
        self.units_axes = np.reshape(self.units_axes, (2*nrow,ncol))

        self.pca_scatter = []
        for i in range(nfig):
            icol = i % self.ncol
            irow0 = int(np.floor(i/self.ncol))
            irow = irow0 * 2
            self.units_axes[irow, icol].clear()
            for j in range(self.n_maxunit):
                ui = j
                te = pg.ScatterPlotItem(brush=pg.mkBrush(color_unit[ui]))
                te.setSize(2)
                self.pca_scatter.append(te) 
                self.units_axes[irow, icol].addItem(te)
        self.pca_scatter = np.reshape(self.pca_scatter, (-1, self.n_maxunit))
    def plot(self, dataall, color_unit, file):
        print('viewer')
        self.cpu.tic()
        nd = len(dataall)
        for i in range(nd):
            units = dataall[i]['units'].item().copy()
            waves = dataall[i]['waves'].item().copy()
            pc = self.cpu.PCA(waves)
            pc = pc[:,0:2]
            icol = i % self.ncol
            irow0 = int(np.floor(i/self.ncol))
            tu = np.unique(units)
            tu = tu[tu >= 0]
            if len(units) < 10000:
                tidrand = np.ones_like(units) == 1
            else:
                tidx = sample(range(len(units)), 10000)
                tidrand = np.ones_like(units) == 0
                tidrand[tidx] = True
            for j in range(self.n_maxunit):
                self.pca_scatter[i,j].setData(x = [], y = [])
            irow = irow0 * 2
            # self.units_axes[irow, icol].clear()

            if platform == "darwin":
                tfile = file[i].split('/')
                tfile = tfile[len(tfile)-2]
            elif platform == "win32":
                tfile = file[i].split('\\')[1]
            self.units_axes[irow, icol].setTitle(str(tfile)) 
            if len(tu) > 0:
                for j in range(len(tu)):
                    ui = int(tu[j])
                    t1 = units == tu[j]
                    if np.any(t1 & tidrand):
                        self.pca_scatter[i,ui].setData(x = pc[t1 & tidrand,0], y = pc[t1 & tidrand,1])
                        self.units_axes[irow, icol].autoRange()
                    # lines = MultiLine()
                    # lines.mysetData(waves[t1 & tidrand,])
                    # lines.setcolor(color_unit[int(tu[j])])
            irow = irow0 * 2 + 1
            self.units_axes[irow, icol].clear()
            self.units_axes[irow, icol].setLabel('left', 'Voltage')
            self.units_axes[irow, icol].setLabel('bottom', 'Time')
            if len(tu) > 0:    
                ttotu = [np.sum(x == units) for x in range(int(np.max(tu))+1)]
                self.units_axes[irow, icol].setTitle(str(ttotu)) 
                for j in range(len(tu)):
                    ui = int(tu[j])
                    if tu[j] == 0:
                        continue
                    t1 = units == tu[j]
                    av_waves = np.mean(waves[t1,], axis = 0)
                    sd_waves = np.std(waves[t1,], axis = 0)
                    cv1 = pg.PlotCurveItem(av_waves + sd_waves)
                    cv2 = pg.PlotCurveItem(av_waves - sd_waves)
                    tl = pg.FillBetweenItem(curve1=cv1, curve2=cv2, brush=pg.mkBrush(color_unit[ui]))
                    self.units_axes[irow, icol].addItem(tl)
            else:
                self.units_axes[irow, icol].setTitle(str('no signal')) 
        self.cpu.toc()

                

# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     ui = Ui_viewer()

#     ui.show()
#     ui.setup_viewer(2, 8)
#     # ui.folderName = './'
#     # ui.load_folder()
#     sys.exit(app.exec_())