from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMainWindow, QDialog, QPushButton, QComboBox, QTextEdit, QMessageBox
from pyqtgraph import PlotWidget, GraphicsLayoutWidget, plot
import pyqtgraph as pg
import numpy as np
import scipy.io as sio
from scipy.io import loadmat
import matplotlib.path as mplPath
from intersect import intersection
import glob
from random import sample, randint
import time
import os

class Dialog_plot(QDialog):  # Inheritance of the QDialog class
    def __init__(self, parent = None):
        super(Dialog_plot, self).__init__(parent)
        self.initUI()
    def initUI(self):
        self.setWindowTitle("Combine channels")  # Window Title
        self.setGeometry(100, 100, 800, 600)
        self.fig = GraphicsLayoutWidget(self) #
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)  # window to create confirmation and cancellation buttons
        self.buttons.accepted.connect(self.accept)
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.fig)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)
class Dialog_getTextValue(QDialog):  # Inheritance of the QDialog class
    def __init__(self, parent = None):
        super(Dialog_getTextValue, self).__init__(parent)
        self.initUI()
    def initUI(self):
        self.setWindowTitle("Combine channels")  # Window Title
        self.setGeometry(400, 400, 200, 200)
        self.c1 = QTextEdit()  # Create a drop-down list box
        self.c2 = QTextEdit()
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)  # window to create confirmation and cancellation buttons
        self.glayout = QtWidgets.QGridLayout()
        self.glayout.addWidget(self.c1, 0, 0)
        self.glayout.addWidget(self.c2, 1, 0)
        self.glayout.addWidget(self.buttons, 1, 1)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.accepted.connect(self.done_choose)
        self.rejected.connect(self.cancel_choose)
        self.setLayout(self.glayout)
    def setValue(self, str1, str2):
        self.c1.setText(str(str1))
        self.c2.setText(str(str2))
    def done_choose(self):
        self.choice = 1
    def cancel_choose(self):
        self.choice = 0
    def getInfo(self):  # Defines the method of obtaining user input data
        return  self.choice, self.c1.toPlainText(), self.c2.toPlainText()
class Dialog_CombineChannel(QDialog):  # Inheritance of the QDialog class
    def __init__(self, parent = None):
        super(Dialog_CombineChannel, self).__init__(parent)
        self.initUI()
    def setupComboBox(self, nmax):
        self.c1.addItems([str(x) for x in range(nmax)])
        self.c1.setCurrentIndex(1)
        self.c2.addItems([str(x) for x in range(nmax)])
        self.c2.setCurrentIndex(2)
    def initUI(self):
        self.setWindowTitle("Combine channels")  # Window Title
        self.setGeometry(400, 400, 200, 200)
        self.c1 = QComboBox()  # Create a drop-down list box
        self.c2 = QComboBox()
        # for g in get_games():  # Add a selection to the drop-down list box (retrieved from a database query)
        # self.game_item.addItem(g.name, g.id)
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)  # window to create confirmation and cancellation buttons
        self.glayout = QtWidgets.QGridLayout()
        self.glayout.addWidget(self.c1, 0, 0)
        self.glayout.addWidget(self.c2, 1, 0)
        self.glayout.addWidget(self.buttons, 1, 1)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.accepted.connect(self.done_choose)
        self.rejected.connect(self.cancel_choose)
        self.setLayout(self.glayout)
    def done_choose(self):
        self.choice = 1
    def cancel_choose(self):
        self.choice = 0
    def getInfo(self):  # Defines the method of obtaining user input data
        return  self.choice, self.c1.currentText(), self.c2.currentText()
class MultiLine(pg.QtGui.QGraphicsPathItem):
    def __init__(self):
        self.path = QtGui.QPainterPath()
        pg.QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.setPen(pg.mkPen('k'))
    def mysetData(self, y = [], x = []):
        """x and y are 2D arrays of shape (Nplots, Nsamples)"""
        if (len(y) > 0):
            if (len(x) == 0):
                x = np.empty(y.shape)
                x[:] = np.arange(y.shape[1])[np.newaxis, :]
            connect = np.ones(y.shape, dtype=bool)
            connect[:, -1] = 0  # don't draw the segment between each trace
            x = x.flatten()
            y = y.flatten()
            connect = connect.flatten()
            self.path = pg.arrayToQPath(x, y, connect)
            self.setPath(self.path)
        else:
            self.path = QtGui.QPainterPath()
            self.setPath(self.path)

    def setcolor(self, col):
        self.setPen(pg.mkPen(col))
    def shape(self): # override because QGraphicsPathItem.shape is too expensive.
        return pg.QtGui.QGraphicsItem.shape(self)
    def boundingRect(self):
        return self.path.boundingRect()
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1410, 702)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.group_Units = QtWidgets.QGroupBox(self.centralwidget)
        self.group_Units.setGeometry(QtCore.QRect(780, 0, 621, 591))
        self.group_Units.setObjectName("group_Units")
        self.graphicsView_units = GraphicsLayoutWidget(self.group_Units)
        self.graphicsView_units.setGeometry(QtCore.QRect(10, 30, 601, 551))
        self.graphicsView_units.setObjectName("graphicsView_units")
        self.group_PCA = QtWidgets.QGroupBox(self.centralwidget)
        self.group_PCA.setGeometry(QtCore.QRect(10, 10, 761, 431))
        self.group_PCA.setObjectName("group_PCA")
        self.comboBox_PC1 = QtWidgets.QComboBox(self.group_PCA)
        self.comboBox_PC1.setGeometry(QtCore.QRect(10, 375, 71, 41))
        self.comboBox_PC1.setObjectName("comboBox_PC1")
        self.comboBox_PC1.addItem("")
        self.comboBox_PC1.addItem("")
        self.comboBox_PC1.addItem("")
        self.comboBox_PC1.addItem("")
        self.comboBox_PC2 = QtWidgets.QComboBox(self.group_PCA)
        self.comboBox_PC2.setGeometry(QtCore.QRect(10, 400, 71, 41))
        self.comboBox_PC2.setObjectName("comboBox_PC2")
        self.comboBox_PC2.addItem("")
        self.comboBox_PC2.addItem("")
        self.comboBox_PC2.addItem("")
        self.comboBox_PC2.addItem("")
        self.checkBox_showallunits = QtWidgets.QCheckBox(self.group_PCA)
        self.checkBox_showallunits.setGeometry(QtCore.QRect(90, 385, 71, 41))
        self.checkBox_showallunits.setObjectName("checkBox_showallunits")
        self.pushButton_Add = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_Add.setGeometry(QtCore.QRect(250, 390, 81, 32))
        self.pushButton_Add.setObjectName("pushButton_Add")
        self.pushButton_Remove = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_Remove.setGeometry(QtCore.QRect(330, 390, 81, 32))
        self.pushButton_Remove.setObjectName("pushButton_Remove")
        self.pushButton_resettemp = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_resettemp.setGeometry(QtCore.QRect(410, 390, 81, 32))
        self.pushButton_resettemp.setObjectName("pushButton_resettemp")
        self.pushButton_noise = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_noise.setGeometry(QtCore.QRect(590, 390, 81, 32))
        self.pushButton_noise.setObjectName("pushButton_noise")
        self.pushButton_Confirm = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_Confirm.setGeometry(QtCore.QRect(670, 390, 81, 32))
        self.pushButton_Confirm.setObjectName("pushButton_Confirm")
        self.checkBox_showunsorted = QtWidgets.QCheckBox(self.group_PCA)
        self.checkBox_showunsorted.setGeometry(QtCore.QRect(485, 385, 130, 20))
        self.checkBox_showunsorted.setObjectName("checkBox_showunsorted")
        self.checkBox_usefordist = QtWidgets.QCheckBox(self.group_PCA)
        self.checkBox_usefordist.setGeometry(QtCore.QRect(485, 405, 130, 20))
        self.checkBox_usefordist.setObjectName("checkBox_usefordist")
        # self.checkBox_useasmodel = QtWidgets.QCheckBox(self.group_PCA)
        # self.checkBox_useasmodel.setGeometry(QtCore.QRect(490, 400, 111, 20))
        # self.checkBox_useasmodel.setChecked(True)
        # self.checkBox_useasmodel.setObjectName("checkBox_useasmodel")
        self.graphicsView_pca = PlotWidget(self.group_PCA)
        self.graphicsView_pca.setGeometry(QtCore.QRect(10, 30, 351, 351))
        self.graphicsView_pca.setObjectName("graphicsView_pca")
        self.graphicsView_raw = PlotWidget(self.group_PCA)
        self.graphicsView_raw.setGeometry(QtCore.QRect(370, 30, 381, 351))
        self.graphicsView_raw.setObjectName("graphicsView_raw")
        self.pushButton_reset = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_reset.setGeometry(QtCore.QRect(170, 390, 81, 32))
        self.pushButton_reset.setObjectName("pushButton_reset")
        self.group_Methods = QtWidgets.QGroupBox(self.centralwidget)
        self.group_Methods.setGeometry(QtCore.QRect(10, 440, 261, 211))
        self.group_Methods.setObjectName("group_Methods")
        self.comboBox_ClusterMethods = QtWidgets.QComboBox(self.group_Methods)
        self.comboBox_ClusterMethods.setGeometry(QtCore.QRect(10, 40, 204, 26))
        self.comboBox_ClusterMethods.setObjectName("comboBox_ClusterMethods")
        self.comboBox_ClusterMethods.addItem("")
        self.comboBox_ClusterMethods.addItem("")
        self.comboBox_ClusterMethods.addItem("")
        self.checkBox_locked = QtWidgets.QCheckBox(self.group_Methods)
        self.checkBox_locked.setGeometry(QtCore.QRect(10, 70, 100, 20))
        self.checkBox_locked.setObjectName("checkBox_locked")
        # self.pushButton_sortsafe = QtWidgets.QPushButton(self.group_Methods)
        # self.pushButton_sortsafe.setGeometry(QtCore.QRect(10, 140, 171, 32))
        # self.pushButton_sortsafe.setObjectName("pushButton_sortsafe")
        self.pushButton_sortall = QtWidgets.QPushButton(self.group_Methods)
        self.pushButton_sortall.setGeometry(QtCore.QRect(10, 170, 113, 32))
        self.pushButton_sortall.setObjectName("pushButton_sortall")
        # self.textEdit_sortsafe = QtWidgets.QTextEdit(self.group_Methods)
        # self.textEdit_sortsafe.setGeometry(QtCore.QRect(180, 140, 71, 31))
        # self.textEdit_sortsafe.setObjectName("textEdit_sortsafe")
        self.frame_Channel = QtWidgets.QFrame(self.centralwidget)
        self.frame_Channel.setGeometry(QtCore.QRect(780, 600, 621, 51))
        self.frame_Channel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Channel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Channel.setObjectName("frame_Channel")
        self.label_channel = QtWidgets.QLabel(self.frame_Channel)
        self.label_channel.setGeometry(QtCore.QRect(10, 10, 171, 31))
        self.label_channel.setObjectName("label_channel")
        # self.textEdit_channel = QtWidgets.QTextEdit(self.frame_Channel)
        # self.textEdit_channel.setGeometry(QtCore.QRect(190, 10, 81, 31))
        # self.textEdit_channel.setObjectName("textEdit_channel")
        self.comboBox_channel = QtWidgets.QComboBox(self.frame_Channel)
        self.comboBox_channel.setGeometry(QtCore.QRect(310, 10, 81, 31))
        self.comboBox_channel.setObjectName("comboBox_channel")
        # self.pushButton_gotochannel = QtWidgets.QPushButton(self.frame_Channel)
        # self.pushButton_gotochannel.setGeometry(QtCore.QRect(280, 10, 113, 32))
        # self.pushButton_gotochannel.setObjectName("pushButton_gotochannel")
        self.pushButton_previouschannel = QtWidgets.QPushButton(self.frame_Channel)
        self.pushButton_previouschannel.setGeometry(QtCore.QRect(390, 10, 113, 32))
        self.pushButton_previouschannel.setObjectName("pushButton_previouschannel")
        self.pushButton_nextchannel = QtWidgets.QPushButton(self.frame_Channel)
        self.pushButton_nextchannel.setGeometry(QtCore.QRect(500, 10, 113, 32))
        self.pushButton_nextchannel.setObjectName("pushButton_nextchannel")
        self.groupBox_side = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_side.setGeometry(QtCore.QRect(280, 440, 491, 211))
        self.groupBox_side.setObjectName("groupBox_side")
        self.graphicsView_side1 = PlotWidget(self.groupBox_side)
        self.graphicsView_side1.setGeometry(QtCore.QRect(0, 20, 241, 191))
        self.graphicsView_side1.setObjectName("graphicsView_side1")
        self.graphicsView_side2 = PlotWidget(self.groupBox_side)
        self.graphicsView_side2.setGeometry(QtCore.QRect(240, 21, 251, 191))
        self.graphicsView_side2.setObjectName("graphicsView_side2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1410, 24))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuFunction = QtWidgets.QMenu(self.menubar)
        self.menuFunction.setObjectName("menuFunction")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoadFolder = QtWidgets.QAction(MainWindow)
        self.actionLoadFolder.setObjectName("actionLoadFolder")
        self.menuFile.addAction(self.actionLoadFolder)
        self.actionUndo = QtWidgets.QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.menuEdit.addAction(self.actionUndo)
        self.actionRedo = QtWidgets.QAction(MainWindow)
        self.actionRedo.setObjectName("actionRedo")
        self.menuEdit.addAction(self.actionRedo)
        self.actionSelectAll = QtWidgets.QAction(MainWindow)
        self.actionSelectAll.setObjectName("actionSelectAll")
        self.menuEdit.addAction(self.actionSelectAll)
        self.RemoveChannel = QtWidgets.QAction(MainWindow)
        self.RemoveChannel.setObjectName("RemoveChannel")
        self.menuFunction.addAction(self.RemoveChannel)
        self.CombineChannels = QtWidgets.QAction(MainWindow)
        self.CombineChannels.setObjectName("CombineChannels")
        self.menuFunction.addAction(self.CombineChannels)
        self.SqueezeChannels = QtWidgets.QAction(MainWindow)
        self.SqueezeChannels.setObjectName("SqueezeChannels")
        self.menuFunction.addAction(self.SqueezeChannels)
        self.RemovefromChannel = QtWidgets.QAction(MainWindow)
        self.RemovefromChannel.setObjectName("RemovefromChannel")
        self.menuFunction.addAction(self.RemovefromChannel)
        self.setnoisethreshold = QtWidgets.QAction(MainWindow)
        self.setnoisethreshold.setObjectName("setnoisethreshold")
        self.menuFunction.addAction(self.setnoisethreshold)
        self.seestatssinglecurve = QtWidgets.QAction(MainWindow)
        self.seestatssinglecurve.setObjectName("seestatssinglecurve")
        self.menuFunction.addAction(self.seestatssinglecurve)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuFunction.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.group_Units.setTitle(_translate("MainWindow", "Neurons"))
        self.group_PCA.setTitle(_translate("MainWindow", "PCA and Raw Signals"))
        self.comboBox_PC1.setItemText(0, _translate("MainWindow", "PC1"))
        self.comboBox_PC1.setItemText(1, _translate("MainWindow", "PC2"))
        self.comboBox_PC1.setItemText(2, _translate("MainWindow", "PC3"))
        self.comboBox_PC1.setItemText(3, _translate("MainWindow", "PC4"))
        self.comboBox_PC2.setItemText(0, _translate("MainWindow", "PC1"))
        self.comboBox_PC2.setItemText(1, _translate("MainWindow", "PC2"))
        self.comboBox_PC2.setItemText(2, _translate("MainWindow", "PC3"))
        self.comboBox_PC2.setItemText(3, _translate("MainWindow", "PC4"))
        self.pushButton_Add.setText(_translate("MainWindow", "add point"))
        self.pushButton_Remove.setText(_translate("MainWindow", "remove"))
        self.pushButton_resettemp.setText(_translate("MainWindow", "clear"))
        self.pushButton_Confirm.setText(_translate("MainWindow", "Confirm"))
        self.pushButton_noise.setText(_translate("MainWindow", "Noise"))
        self.checkBox_showunsorted.setText(_translate("MainWindow", "show unsorted"))
        self.checkBox_usefordist.setText(_translate("MainWindow", "use for dist"))
        # self.checkBox_useasmodel.setText(_translate("MainWindow", "use as model"))
        self.pushButton_reset.setText(_translate("MainWindow", "Reset"))
        self.group_Methods.setTitle(_translate("MainWindow", "Clustering"))
        # self.pushButton_sortsafe.setText(_translate("MainWindow", "Cluster with confidence"))
        self.checkBox_locked.setText(_translate("MainWindow", "lock existing channels"))
        self.checkBox_locked.setChecked(True)
        self.checkBox_showallunits.setText(_translate("MainWindow", "all units"))
        self.checkBox_showallunits.setChecked(True)
        self.pushButton_sortall.setText(_translate("MainWindow", "Cluster all"))
        self.comboBox_ClusterMethods.setItemText(0, _translate("MainWindow", "minimal distance"))
        self.comboBox_ClusterMethods.setItemText(1, _translate("MainWindow", "cut from histogram of distances"))
        self.label_channel.setText(_translate("MainWindow", "Load data first"))
        # self.pushButton_gotochannel.setText(_translate("MainWindow", "Go to Channel"))
        self.pushButton_previouschannel.setText(_translate("MainWindow", "Previous"))
        self.pushButton_nextchannel.setText(_translate("MainWindow", "Next Channel"))
        self.groupBox_side.setTitle(_translate("MainWindow", "Side Plots"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuFunction.setTitle(_translate("MainWindow", "Function"))
        self.actionLoadFolder.setText(_translate("MainWindow", "Load folder"))
        self.actionLoadFolder.setStatusTip(_translate("MainWindow", "Load a folder"))
        self.actionLoadFolder.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionUndo.setText(_translate("MainWindow", "Undo"))
        self.actionUndo.setStatusTip(_translate("MainWindow", "Undo"))
        self.actionUndo.setShortcut(_translate("MainWindow", "Ctrl+Z"))
        self.actionSelectAll.setText(_translate("MainWindow", "Select All"))
        self.actionSelectAll.setStatusTip(_translate("MainWindow", "Select All"))
        self.actionSelectAll.setShortcut(_translate("MainWindow", "Ctrl+A"))
        self.actionRedo.setText(_translate("MainWindow", "Redo"))
        self.actionRedo.setStatusTip(_translate("MainWindow", "Redo"))
        self.actionRedo.setShortcut(_translate("MainWindow", "Ctrl+Shift+Z"))
        self.RemoveChannel.setText(_translate("MainWindow", "Remove Channel"))
        self.CombineChannels.setText(_translate("MainWindow", "Combine Channels"))
        self.SqueezeChannels.setText(_translate("MainWindow", "Squeeze Channels"))
        self.RemovefromChannel.setText(_translate("MainWindow", "Remove from Channel"))
        self.setnoisethreshold.setText(_translate("MainWindow", "Set noise threshold"))
        self.seestatssinglecurve.setText(_translate("MainWindow", "Single curve stats"))
class SW_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent = parent)
        self.setupUi(self)
        self.setup_SW()
    def tic(self):
        self.t_tic = time.perf_counter()
    def toc(self, option = 0):
        self.t_toc = time.perf_counter()
        print(f"Runtime: {self.t_toc - self.t_tic:0.4f} seconds")
        if (option == 1):
            self.t_tic = self.t_toc
    def setup_SW(self):
        # set up colors
        self.color_unit = ["k","r","b","g","c","y"]
        self.n_maxunit = len(self.color_unit)
        self.is_loaddata = False
        self.dlg_noisethreshold = Dialog_getTextValue(self)
        self.dlg_noisethreshold.setValue(-500, 500)
        self.threshold_noise = np.array([])
        self.setup_reset()
        self.setup_axes()
        self.setup_connect()
    def setup_connect(self):
        self.actionLoadFolder.triggered.connect(self.sw_load_folder)
        self.actionUndo.triggered.connect(self.sw_undo)
        self.actionRedo.triggered.connect(self.sw_redo)
        self.actionSelectAll.triggered.connect(self.sw_selectall)
        self.checkBox_showunsorted.clicked.connect(self.sw_showunsorted)
        self.checkBox_showallunits.clicked.connect(self.sw_showallunits)
        self.RemoveChannel.triggered.connect(self.sw_removechannel)
        self.CombineChannels.triggered.connect(self.sw_combinechannels)
        self.SqueezeChannels.triggered.connect(self.sw_squeezechannels)
        self.RemovefromChannel.triggered.connect(self.sw_removefromchannel)
        self.setnoisethreshold.triggered.connect(self.sw_setnoisethreshold)
        self.seestatssinglecurve.triggered.connect(self.sw_singlecurvestats)
        self.pushButton_reset.clicked.connect(self.sw_reset)
        self.pushButton_Add.clicked.connect(self.sw_addpoint)
        self.pushButton_Remove.clicked.connect(self.sw_removepoint)
        self.pushButton_resettemp.clicked.connect(self.sw_cleartemp)
        self.pushButton_Confirm.clicked.connect(self.sw_confirm)
        self.pushButton_noise.clicked.connect(self.sw_noise)
        self.pushButton_nextchannel.clicked.connect(self.sw_nextchannel)
        self.pushButton_previouschannel.clicked.connect(self.sw_previouschannel)
        self.pushButton_sortall.clicked.connect(self.sw_sortall)
        self.pca_emptyplot.scene().sigMouseClicked.connect(self.mouse_clicked_pca)
        self.raw_emptyplot.scene().sigMouseClicked.connect(self.mouse_clicked_raw)
        self.comboBox_PC1.activated.connect(self.sw_combobox_pc_plt)
        self.comboBox_PC2.activated.connect(self.sw_combobox_pc_plt)
        self.comboBox_channel.activated.connect(self.sw_gotochannel)
    def setup_axes(self):
        # set up graphics view background
        self.graphicsView_pca.setBackground('w')
        self.graphicsView_raw.setBackground('w')
        self.graphicsView_units.setBackground('w')
        self.graphicsView_side1.setBackground('w')
        self.graphicsView_side2.setBackground('w')
        self.graphicsView_pca.setMenuEnabled(False)
        self.graphicsView_raw.setMenuEnabled(False)
        self.graphicsView_side1.setMenuEnabled(False)
        self.graphicsView_side2.setMenuEnabled(False)
        # set up lines
        # -- raw
        self.raw_emptyplot = self.graphicsView_raw.plot(x=[], y=[], pen=pg.mkPen("m"))
        self.raw_lines = []
        for ui in range(self.n_maxunit):
            lines = MultiLine()
            lines.setcolor(self.color_unit[ui])
            self.raw_lines.append(lines)
            self.graphicsView_raw.addItem(lines)
        lines = MultiLine()
        lines.setcolor("m")
        self.lines_selected = lines
        self.graphicsView_raw.addItem(lines)
        te = pg.PlotCurveItem(pen=pg.mkPen("m"))  # this color needs to be changed
        self.raw_path = te
        self.graphicsView_raw.addItem(te)
        # -- pca
        self.pca_emptyplot = self.graphicsView_pca.plot(x=[], y=[], pen=pg.mkPen("m"))
        self.pca_scatter = []
        for ui in range(self.n_maxunit):
            te = pg.ScatterPlotItem(brush=pg.mkBrush(self.color_unit[ui]))
            te.setSize(2)
            self.pca_scatter.append(te)
            self.graphicsView_pca.addItem(te)
        te = pg.ScatterPlotItem(brush=pg.mkBrush("m"))
        te.setSize(5)
        self.points_selected = te
        self.graphicsView_pca.addItem(te)
        te = pg.PlotCurveItem(pen=pg.mkPen("m"))  # this color needs to be changed
        self.pca_path = te
        self.graphicsView_pca.addItem(te)
        # -- units
        self.units_axes = []
        for uj in range(5):
            for ui in range(self.n_maxunit):
                te = self.graphicsView_units.addPlot(row = uj, col = ui)
                # te.setAspectLocked(lock=False)
                # self.graphicsView_units.addViewBox(row = uj, col = ui)
                self.units_axes.append(te)
        self.units_axes = np.reshape(self.units_axes, (-1,self.n_maxunit))
    def sw_showunsorted(self):
        # print('show unsorted')
        self.plt_pca()
        self.plt_raw()
        self.plt_selectiontool()
    def sw_showallunits(self):
        self.get_randomsubsets()
        self.plt_all()
    def get_randomsubsets(self):
        units = self.data['units'].item().copy()
        nu = units.size
        if (nu < 10000) or self.checkBox_showallunits.isChecked():
            self.idx_randomsubset = np.ones_like(units) == 1
        else:
            tidx = sample(range(nu), 10000)
            self.idx_randomsubset = np.ones_like(units) == 0
            self.idx_randomsubset[tidx] = True
    def setup_reset(self):
        self.checkBox_usefordist.setChecked(True)
        self.comboBox_PC1.setCurrentIndex(0)
        self.comboBox_PC2.setCurrentIndex(1)
        self.sw_combobox_pc()
        self.idx_selected = []
        self.idx_selected_temp = []
        self.reset_selectiontool(0)
        self.unit_now = 0
        self.history_units = []
        self.history_locked = []
        self.history_idx = []
        self.history_idxtemp = []
        self.redo_units = []
        self.redo_locked = []
        self.redo_idx = []
        self.redo_idxtemp = []
        self.is_addhistory = True
        self.is_locked = np.zeros(self.n_maxunit) == 1
    def set_addpoint(self, pt):
        self.is_addpoint = pt
        if pt == 0:
            cursor = QtCore.Qt.ArrowCursor
        else:
            if pt == 1:
                cursor = QtCore.Qt.CrossCursor  # QCursor
            else:
                cursor = QtCore.Qt.IBeamCursor # QCursor
        self.graphicsView_pca.setCursor(cursor)
        self.graphicsView_raw.setCursor(cursor)
    def file_loadfile(self):
        self.setup_reset()
        self.is_loaddata = True
        filename = self.filenow
        td = sio.loadmat(filename)
        self.rawmat = td
        self.data = td.get('waveforms')
        self.initial_dataformat()
        self.is_usefordist = np.array(np.ones_like(self.data['units'].item()) == 1)
        if self.is_usefordist.size >= 10000:
            self.checkBox_showallunits.setChecked(False)
        self.get_randomsubsets()
        self.comp_setup()
        self.statusbar.showMessage(f"loaded file: {filename}")
    def initial_dataformat(self):
        n_pixel = 52
        units = self.data['units'].item().copy()
        if (len(units) == 1):
            units = units[0]
        if (units.dtype != 'float'):
            units = np.float_(units)
        units = np.array(units)
        units[(units > self.n_maxunit) | (units < -1)] = 0
        self.data['units'].itemset(units)
        waves = self.data['waves'].item().copy()
        if waves.shape[0] == n_pixel: # rotate when 52x52
            self.data['waves'].itemset(waves.T)
        self.addhistory()
    def comp_setup(self):
        # compute PCA
        # self.tic()
        waves = self.data['waves'].item().copy()
        self.pca = self.PCA(waves)
        # self.toc()
        self.sw_combobox_pc()
        # self.toc()
        self.n_phaseshift = int(waves.shape[1]*2/3)
        self.comp_default()
        # self.toc()
        self.check_threshold_noise()
        # self.toc()
        if self.data['units'].item().size > 1:
            self.plt_all()
        else:
            out = QMessageBox.warning(self, "Warning", "This channel is empty, move on to the next")
            if out:
                self.sw_nextchannel()
        # self.toc()
    def comp_default(self):
        # pc = self.pca
        units = self.data['units'].item().copy()
        waves = self.data['waves'].item().copy()
        npix = waves.shape[1]
        av = np.ones((self.n_maxunit, npix)) * np.NaN
        sd = np.ones((self.n_maxunit, npix)) * np.NaN
        for i in range(self.n_maxunit):
            if i == 0:
                tid = (units == -1).squeeze()
            else:
                tid = (units == i).squeeze()
            tid = tid & self.is_usefordist
            if np.any(tid):
                av[i,] = np.mean(waves[tid,], axis = 0)
                sd[i,] = np.std(waves[tid,], axis = 0)#/np.sqrt(np.sum(tid))
        self.av_waves = av
        self.sd_waves = sd

        # compute Raw distance
        dist = np.zeros((waves.shape[0], self.n_maxunit))
        for i in range(self.n_maxunit):
            dist[:,i] = np.mean((waves - av[i,])**2, axis = 1)
        self.dist_waves_raw = dist

        shifts = np.zeros((waves.shape[0], self.n_maxunit))
        # compute phase-shift distance
        if False:
            dist = np.zeros((waves.shape[0], self.n_maxunit))
            ns = self.n_phaseshift
            nw = waves.shape[1]
            nu = waves.shape[0]
            self.dist_shift = list()
            for i in range(self.n_maxunit):
                if not np.any(np.isnan(av[i,])):
                    tdists = np.zeros((nu, 2*(nw - ns)+1))
                    for j in range(2*(nw - ns)+1):
                        tx = j - (nw - ns)
                        trg1 = range(max(tx, 0), min(tx + nw, nw))
                        trg2 = range(max(nw - ns - j, 0), min(nw + nw - ns - j , nw))
                        twaves = waves.copy()
                        tav = av[i, trg2]
                        twaves = twaves[:, trg1]
                        twaves_av = np.mean(twaves, axis = 1)
                        twaves = (twaves.T - twaves_av).T + np.mean(tav)
                        tdists[:,j] = np.mean((twaves - tav)**2, axis = 1)
                    self.dist_shift.append(tdists)
                    shifts[:,i] = np.argmin(tdists, axis = 1) - (nw - ns)
                    dist[:, i] = np.min(tdists, axis = 1)
                else:
                    self.dist_shift.append([])
                    shifts[:,i] = np.NaN
                    dist[:, i] = np.NaN
            self.dist_waves_phase = dist
            self.shifts = shifts
        self.dist_waves = self.dist_waves_raw
    def PCA(self, X, num_components=[]):
        if len(num_components) == 0:
            num_components = X.shape[1]
        # Step-1
        X_meaned = X - np.mean(X, axis=0)

        if X.shape[0] == 1:
            return X_meaned
        # Step-2
        cov_mat = np.cov(X_meaned, rowvar=False)

        # Step-3
        eigen_values, eigen_vectors = np.linalg.eigh(cov_mat)

        # Step-4
        sorted_index = np.argsort(eigen_values)[::-1]
        sorted_eigenvalue = eigen_values[sorted_index]
        sorted_eigenvectors = eigen_vectors[:, sorted_index]

        # Step-5
        eigenvector_subset = sorted_eigenvectors[:, 0:num_components]

        # Step-6
        X_reduced = np.dot(eigenvector_subset.transpose(), X_meaned.transpose()).transpose()

        return X_reduced
    def sw_combobox_pc_plt(self):
        self.sw_combobox_pc()
        self.plt_pca()
        self.plt_selectiontool()
    def sw_combobox_pc(self):
        if self.is_loaddata:
            n1 = self.comboBox_PC1.currentText()
            n1 = int(n1[2]) - 1
            n2 = self.comboBox_PC2.currentText()
            n2 = int(n2[2]) - 1
            pc = self.pca[:, (n1, n2)]
            self.pc_now = pc
            self.pca_polygon_vertices = []
            # self.idx_selected_temp = []
    def sw_reset(self):
        # self.setup_reset()
        units = self.data['units'].item().copy()
        units = np.zeros(units.shape)
        units = np.int64(units)
        islocked = np.zeros_like(self.is_locked) == 1
        self.update_unit(units, islocked)
    def plt_all(self):
        print('plt_all')
        self.tic()
        self.plt_pca()
        self.toc(1)
        self.plt_raw()
        self.toc(1)
        self.plt_selectiontool()
        # self.toc(1)
        self.plt_units()
        self.toc(1)
        self.plt_locked()
        # self.toc()
        self.plt_noise()
        # self.toc(1)
    def plt_noise(self):
        waves = self.data['waves'].item().copy()
        units = self.data['units'].item().copy()

        self.graphicsView_side1.clear()
        self.graphicsView_side1.setLabel('left', 'Voltage')
        self.graphicsView_side1.setLabel('bottom', 'Time')
        # print(self.av_waves[1,:])
        # print(self.av_waves[:,0])
        for i in range(self.n_maxunit):
            if i > 0:
                # special plot - average
                cv1 = pg.PlotCurveItem(self.av_waves[i,] + self.sd_waves[i,])
                cv2 = pg.PlotCurveItem(self.av_waves[i,] - self.sd_waves[i,])
                tl = pg.FillBetweenItem(curve1=cv1, curve2=cv2, brush=pg.mkBrush(self.color_unit[i]))
                # tl = pg.PlotCurveItem(self.av_waves[i,], fill = -0.3, ,  pen=pg.mkPen(self.color_unit[i]))
                self.graphicsView_side1.addItem(tl)
                str = f"sorted: {np.mean(units > 0) * 100:.2f}%, {np.sum(units > 0)}/{len(units)}"
                self.graphicsView_side1.setTitle(str)

        self.graphicsView_side2.clear()
        str = f"noise: {np.mean(units == -1)*100:.2f}%, {np.sum(units == -1)}/{len(units)}"
        self.graphicsView_side2.setTitle(str)
        self.graphicsView_side2.setLabel('left', 'Voltage')
        self.graphicsView_side2.setLabel('bottom', 'Time')
        tid = (units == -1).squeeze()
        if (any(tid)):
            tl = MultiLine()
            tl.mysetData(waves[tid,])
            tl.setcolor(pg.mkPen('k'))
            self.graphicsView_side2.addItem(tl)
    def plt_pca(self):
        units = self.data['units'].item().copy()
        pc = self.pc_now
        if pc.shape[0] == 1:
            self.pca_scatter[units.__int__()].setData(x = pc[0], y= pc[0])
            return
        idp = self.get_selected()
        for ui in range(self.n_maxunit):
            if (ui > 0) and (self.checkBox_showunsorted.isChecked()):
                self.pca_scatter[ui].setData(x = [], y = [])
                continue
            tid = (units == ui).squeeze()
            tid = tid & self.idx_randomsubset
            if len(idp) > 0:
                tid = tid & ~idp
            if np.any(tid):
                self.pca_scatter[ui].setData(x = pc[tid,0], y = pc[tid,1])
            else:
                self.pca_scatter[ui].setData(x=[], y=[])

        if (len(idp) > 0) and np.any(idp):
            idp = idp & self.idx_randomsubset
            self.points_selected.setData(x=pc[idp, 0], y=pc[idp, 1])
        else:
            self.points_selected.setData(x=[], y=[])

        self.graphicsView_pca.setLabel('bottom',f'{self.comboBox_PC1.currentText()}')
        self.graphicsView_pca.setLabel('left',f'{self.comboBox_PC2.currentText()}')
    def plt_raw(self):
        # print('plt_raw')
        idp = self.get_selected()
        waves = self.data['waves'].item().copy()
        units = self.data['units'].item().copy()
        self.graphicsView_raw.setLabel('left','Voltage')
        self.graphicsView_raw.setLabel('bottom','Time')
        for ui in range(self.n_maxunit):
            if (ui > 0) and (self.checkBox_showunsorted.isChecked()):
                self.raw_lines[ui].mysetData()
                continue
            tid = (units == ui).squeeze()
            tid = tid & self.idx_randomsubset
            if len(idp) > 0:
                tid = tid & ~idp
            if np.any(tid):
                self.raw_lines[ui].mysetData(waves[tid,])
            else:
                self.raw_lines[ui].mysetData()

        if (len(idp) > 0) and np.any(idp):
            idp = idp & self.idx_randomsubset
            self.lines_selected.mysetData(waves[idp,])
        else:
            self.lines_selected.mysetData()
    def plt_selectiontool(self):
        if len(self.pca_polygon_vertices) > 0:
            pts = np.reshape(self.pca_polygon_vertices, [-1, 2])
            pts = np.append(pts, [pts[0,]], axis=0)
            self.pca_path.setData(x=pts[:, 0], y=pts[:, 1])
        else:
            self.pca_path.setData(x = [], y = [])
        if len(self.raw_line_vertices) > 0:
            pts = np.reshape(self.raw_line_vertices, [-1, 2])
            pts = np.append(pts, [pts[0,]], axis=0)
            self.raw_path.setData(x=pts[:, 0], y=pts[:, 1])
        else:
            self.raw_path.setData(x = [], y = [])
    def reset_selectiontool(self, option = None):
        self.pca_polygon_vertices = []
        self.raw_line_vertices = []
        if not (option is None):
            self.set_addpoint(option)
    def plt_locked(self):
        for i in range(self.n_maxunit):
            if self.is_locked[i]:
                str_L = 'Locked'
                self.units_axes[1,i].setTitle(str_L)
            else:
                str_L = ''
                self.units_axes[1,i].setTitle(str_L)
    def plt_units(self):
        waves = self.data['waves'].item().copy()
        units = self.data['units'].item().copy()
        if units.size == 1:
            return
        trg = np.array([np.infty, -np.infty])
        for i in range(self.n_maxunit):
            if i == self.unit_now:
                self.units_axes[0, i].getViewBox().setBackgroundColor("m")
            else:
                self.units_axes[0, i].getViewBox().setBackgroundColor("w")
            tid = (units == i).squeeze()
            n_uniti = np.sum(tid)
            n_unitall = len(units)
            str = f"{n_uniti/n_unitall*100:.1f}%"
            # str = str + str_L
            self.units_axes[0, i].setTitle(str) # fake title
            self.units_axes[0, i].clear()
            self.units_axes[1, i].clear()
            self.units_axes[2, i].clear()
            self.units_axes[3, i].clear()
            if n_uniti > 0:
                tid = tid & self.idx_randomsubset
                # lines
                lines = MultiLine()
                lines.mysetData(waves[tid,])
                lines.setcolor(self.color_unit[i])
                self.units_axes[0, i].addItem(lines)
                self.units_axes[0, i].autoRange()
                te = self.units_axes[0, i].getAxis('left').range
                if te[1] > trg[1]:
                    trg[1] = te[1]
                if te[0] < trg[0]:
                    trg[0] = te[0]
                # ITI
                st = self.data['spikeTimes'].item().squeeze()
                iti = np.diff(st[tid])
                hst_y, hst_x = np.histogram(iti, bins=np.arange(0, np.max(iti), 2))
                thst = pg.PlotCurveItem(hst_x, hst_y, stepMode=True, fillLevel=0, brush=pg.mkBrush(self.color_unit[i]))
                self.units_axes[1, i].addItem(thst)
                self.units_axes[1, i].autoRange()
                self.units_axes[1, i].setXRange(0, 30, padding = 0)
                # timing vs firing rate
                ty, tx = np.histogram(st[tid]/np.max(st), bins=np.linspace(0, 1, 100))
                tx = (tx[1:] + tx[:-1]) / 2
                thst = pg.PlotCurveItem(tx, ty, pen=pg.mkPen(self.color_unit[i]))
                self.units_axes[2, i].addItem(thst)
                self.units_axes[2, i].autoRange()
                # distance from clusters
                dst = self.dist_waves
                if not np.all(np.isnan(dst[:, i])):
                    bin = np.arange(0, np.nanmax(dst[:,i]), np.nanmean(dst[tid,i])/100)
                    ldsts = np.zeros((self.n_maxunit, len(bin)-1))
                    for j in range(self.n_maxunit):
                        ty, tx = np.histogram(dst[units == j, i], bins = bin)
                        tx = (tx[1:] + tx[:-1])/2
                        tl = pg.PlotCurveItem(tx, ty, pen=pg.mkPen(self.color_unit[j]))
                        self.units_axes[3, i].addItem(tl)
                    self.units_axes[3, i].autoRange()
                    self.units_axes[3, i].setXRange(0, np.mean(dst[tid,i] * 2), padding = 0)

        for i in range(self.n_maxunit):
            if np.any(units == i):
                self.units_axes[0, i].setYRange(trg[0], trg[1])
    def keyPressEvent(self, event):
        key = event.key()
        if self.is_loaddata == 0:
            return
        if key < 200: #ascii codes range
            str = chr(key)
            if str.isdigit():
                keyint = np.int64(str)
                if (keyint >=0) and (keyint <self.n_maxunit):
                    self.unit_now = keyint
                    self.plt_units()
            if str.isalpha():
                if str == 'L':
                    self.is_locked[self.unit_now] = ~self.is_locked[self.unit_now]
                    self.select_locked()
                    self.plt_pca()
                    self.plt_raw()
                    self.plt_locked()
                    self.plt_selectiontool()
                if str == 'A':
                    self.update_selected()
                    self.set_addpoint(0)
    def get_lockedlines(self):
        units = self.data['units'].item()
        out = np.zeros_like(units)
        for i in range(self.n_maxunit):
            if self.is_locked[i]:
                out[units == i] = 1
        out[units == -1] = 1 # for noise
        return(out == 1)
    def addhistory(self):
        if self.is_addhistory:
            self.history_units.append(self.data['units'].item().copy())
            self.history_locked.append(self.is_locked.copy())
            self.history_idx.append(self.idx_selected.copy())
            self.history_idxtemp.append(self.idx_selected_temp.copy())
            # print(f"add history, {len(self.history_units)}")
    def update_unit(self, units, locked = [], idselect = [], idtemp = [], isoverwrite = 0):
        oldunits = self.data['units'].item().copy()
        if len(locked) == 0:
            idx = self.get_lockedlines()
            units[idx] = oldunits[idx]
        else:
            self.is_locked = locked
        if (len(idselect) > 0) or (isoverwrite == 1):
            # print(idselect)
            self.idx_selected = idselect
        if (len(idtemp) > 0) or (isoverwrite == 1):
            # print(idtemp)
            self.idx_selected_temp = idtemp
        if (len(idselect) > 0) or (len(idtemp) > 0):
            self.reset_selectiontool(0)
        idx_sig20 = (oldunits != 0) & (units == 0)
        self.is_usefordist[idx_sig20] = True
        if not self.checkBox_usefordist.isChecked():
            idx_02sig = (oldunits == 0) & (units != 0)
            self.is_usefordist[idx_02sig] = False
        self.data['units'].itemset(units)
        self.addhistory()
        self.comp_default()
        self.plt_all()
        self.autosave()
    def update_selectedunit(self, idx, unitnew):
        units = self.data['units'].item().copy()
        # if len([unitnew]) == len(idx):
        #     units[idx] = unitnew[idx]
        # else:
        units[idx] = unitnew
        self.update_unit(units)
    def autosave(self):
        # reverse waves
        waves = self.data['waves'].item().copy()
        self.data['waves'].itemset(waves.T)
        mdict = self.rawmat
        mdict['waveforms'] = self.data
        sio.savemat(self.filenow, mdict)
        self.data['waves'].itemset(waves)
    def sw_cleartemp(self):
        if len(self.idx_selected_temp) > 0:
            self.idx_selected_temp = []
            self.addhistory()
        else:
            if len(self.idx_selected) > 0:
                self.idx_selected = []
                self.addhistory()
        self.reset_selectiontool(0)
        self.plt_raw()
        self.plt_pca()
        self.plt_selectiontool()
    def sw_addpoint(self):
        self.idx_selected_temp = []
        self.reset_selectiontool(1)
    def sw_removepoint(self):
        self.idx_selected_temp = []
        self.reset_selectiontool(-1)
    def sw_confirm(self):
        self.update_selected()
        idp = self.idx_selected.copy()
        self.idx_selected = []
        self.idx_selected_temp = []
        self.reset_selectiontool(0)
        if (len(idp) > 0) and np.any(idp):
            self.update_selectedunit(idp, self.unit_now)
    def sw_noise(self):
        self.update_selected()
        idp = self.idx_selected.copy()
        self.idx_selected = []
        self.idx_selected_temp = []
        self.reset_selectiontool(0)
        if (len(idp) > 0) and np.any(idp):
            self.update_selectedunit(idp, -1)
    def select_locked(self):
        idl = self.get_lockedlines()
        if len(self.idx_selected) > 0:
            self.idx_selected = self.idx_selected & ~idl
        if len(self.idx_selected_temp) > 0:
            self.idx_selected_temp = self.idx_selected_temp & ~idl
    def update_selected(self):
        tmp = self.idx_selected_temp.copy()
        isadd = 0
        if (len(tmp) > 0):
            if len(self.idx_selected) > 0:
                if self.is_addpoint == 1:
                    self.idx_selected = (self.idx_selected | tmp)
                    isadd = 1
                else:
                    self.idx_selected = (self.idx_selected & ~tmp)
                    isadd = 1
            else:
                if self.is_addpoint == 1:
                    self.idx_selected = tmp
                    isadd = 1
                else:
                    self.idx_selected = []
        self.idx_selected_temp = []
        if isadd:
            self.addhistory()
        self.plt_pca()
        self.plt_raw()
        self.plt_selectiontool()
    def get_selected(self):
        idp = self.idx_selected.copy()
        if len(self.idx_selected_temp) > 0:
            if len(idp) > 0:
                if self.is_addpoint == 1:
                    idp = idp | self.idx_selected_temp
                else:
                    idp = idp & ~self.idx_selected_temp
            else:
                if self.is_addpoint == 1:
                    idp = self.idx_selected_temp
                else:
                    idp = []
        return(idp)
    def mouse_clicked_raw(self, event):
        if self.is_addpoint != 0:
            p = self.graphicsView_raw.plotItem.vb.mapSceneToView(event.scenePos())
            self.raw_line_vertices.append([p.x(), p.y()])
            while len(self.raw_line_vertices) > 2:
                self.raw_line_vertices.reverse()
                self.raw_line_vertices.pop()
                self.raw_line_vertices.reverse()
            if len(self.raw_line_vertices) == 2:
                pts = np.reshape(self.raw_line_vertices, [-1, 2])
                self.assist_addpointsinline(pts)
            if event.button() == 2:
                self.update_selected()
                self.set_addpoint(0)
    def mouse_clicked_pca(self, event):
        if self.is_addpoint != 0:
            p = self.graphicsView_pca.plotItem.vb.mapSceneToView(event.scenePos())
            self.pca_polygon_vertices.append([p.x(), p.y()])
            pts = np.reshape(self.pca_polygon_vertices, [-1, 2])
            pts = np.append(pts, [pts[0,]], axis=0)
            self.assist_addpointsinpolygon(pts)
            if event.button() == 2:
                self.update_selected()
                self.set_addpoint(0)
    def assist_addpointsinpolygon(self, pts):
        poly_path = mplPath.Path(pts)
        pc = self.pc_now
        idp = poly_path.contains_points(pc)
        self.idx_selected_temp = idp
        self.select_locked()
        self.plt_pca()
        self.plt_raw()
        self.plt_selectiontool()
    def assist_addpointsinline(self, pts):
        waves = self.data['waves'].item().copy()
        nl = waves.shape[0]
        npixel = waves.shape[1]
        idp = np.repeat(False, nl)
        # for i in range(nl):
        #     te = intersection(pts[:, 0], pts[:, 1], list(range(npixel)),waves[i,])
        #     idp[i] = (te[0].shape[0] > 0)
        x_coords, y_coords = zip(*pts)
        xx = np.sort(x_coords)
        yy = np.sort(y_coords)
        if np.diff(xx) == 0:
            xx = np.unique(xx)[0]
            if (xx >= 1) and (xx <= waves.shape[1]):
                t1 = int(np.floor(xx))
                t2 = int(np.ceil(xx))
                if t1 == t2:
                    y2 = waves[:, t1 - 1]
                else:
                    tr = (xx - t1) / (t2 - t1)
                    y2 = waves[:, t1] * (1 - tr) + waves[:, t2] * tr
                idp = (y2 >= yy[0]) & (y2 <= yy[1])
            else:
                idp = []
        else:
            A = np.vstack([x_coords, np.ones(len(x_coords))]).T
            m, c = np.linalg.lstsq(A, y_coords, rcond = None)[0]
            xs = range(int(np.floor(xx[1])- np.ceil(xx[0]))) + np.ceil(xx[0])
            if len(xs) == 0:
                xs = xx
            else:
                if xs[0] != xx[0]:
                    xs = np.append(xx[0],xs)
                if xs[-1] != xx[1]:
                    xs = np.append(xs, xx[1])
            xs = xs[(xs >= 1) & (xs <= waves.shape[1])]
            ys = xs * m + c
            if len(xs) > 0:
                y2 = np.zeros((waves.shape[0], len(xs)))
                for i in range(len(xs)):
                    t1 = int(np.floor(xs[i]))
                    t2 = int(np.ceil(xs[i]))
                    if t1 == t2:
                        y2[:, i] = waves[:, t1 - 1]
                    else:
                        tr = (xs[i] - t1)/(t2-t1)
                        y2[:, i] = waves[:, t1 - 1] * (1-tr) + waves[:, t2 - 1] * tr
                dy = y2 - ys
                idp = np.any(dy > 0, axis=1) & np.any(dy < 0, axis = 1)
        self.idx_selected_temp = idp
        self.select_locked()
        self.plt_pca()
        self.plt_raw()
        self.plt_selectiontool()
    def choosefile(self, fid):
        self.fileid = fid
        self.filenow = os.path.join(self.folderName, self.filelists[fid])
        self.label_channel.setText(f'channel {fid+1} / {self.n_file}')
        self.comboBox_channel.setCurrentIndex(fid)
        # self.textEdit_channel.setText(f'{fid+1}')
        self.file_loadfile()  # import the first file
    def sw_gotochannel(self, fid):
        fnow = self.comboBox_channel.currentText()
        xx = [x in fnow for x in self.filelists]
        fid = np.where(xx)[0][0]
        self.choosefile(fid)
    def load_folder(self):
        fs = os.listdir(self.folderName)
        fs.sort()
        self.filelists = [x for x in fs if x.startswith('waveforms')]
        self.comboBox_channel.clear()
        self.comboBox_channel.addItems(self.filelists)
        self.n_file = len(self.filelists)
        self.choosefile(0)
    def sw_load_folder(self):
        dlg = QFileDialog()
        if dlg.exec_():
            self.folderName = dlg.selectedFiles()[0]
            if self.folderName:
                self.load_folder()
    def sw_previouschannel(self):
        self.fileid = self.fileid - 1
        if self.fileid < 0:
            self.fileid = 0
        self.choosefile(self.fileid)
    def sw_nextchannel(self):
        self.fileid = self.fileid + 1
        if self.fileid >= self.n_file:
            self.fileid = self.n_file - 1
        self.choosefile(self.fileid)
    def sw_sortall(self):
        if self.comboBox_ClusterMethods.currentText() == "minimal distance":
            units = self.sw_sort_minimaldist()
        if self.comboBox_ClusterMethods.currentText() == "cut from histogram of distances":
            units = self.sw_sort_cutfromhistdist()
        if len(units) > 0:
            if self.checkBox_locked.isChecked():
                locked = self.is_locked.copy()
                self.is_locked = np.ones_like(locked) == 1
                self.is_locked[0] = False
            self.update_unit(units)
            if self.checkBox_locked.isChecked():
                self.is_locked = locked
                self.plt_locked()
    def sw_selectall(self):
        units = self.data['units'].item().copy()
        self.idx_selected = units == 0
        self.idx_selected_temp = []
        self.addhistory()
        self.plt_pca()
        self.plt_raw()
        self.plt_selectiontool()
    def sw_undo(self):
        # print(f"undo - nlist:{len(self.history_units)}")
        if len(self.history_units) > 1:
            self.redo_units = self.data['units'].item().copy()
            self.redo_locked = self.is_locked.copy()
            self.redo_idx = self.idx_selected.copy()
            self.redo_idxtemp = self.idx_selected_temp.copy()
            self.history_units.pop()
            self.history_locked.pop()
            self.history_idx.pop()
            self.history_idxtemp.pop()
            units = self.history_units[-1].copy()
            locked = self.history_locked[-1].copy()
            idx = self.history_idx[-1].copy()
            idxtemp = self.history_idxtemp[-1].copy()
            self.is_addhistory = False
            self.update_unit(units, locked, idx, idxtemp, 1)
            self.is_addhistory = True
    def sw_redo(self):
        # print(f"redo - nlist:{len(self.history_units)}")
        if len(self.redo_units) > 0:
            self.update_unit(self.redo_units.copy(), self.redo_locked.copy(), self.redo_idx.copy(), self.redo_idxtemp.copy(), 1)
            self.redo_units = []
            self.redo_locked = []
            self.redo_idx = []
            self.redo_idxtemp = []
    def sw_removechannel(self):
        unow = self.unit_now
        self.is_locked[unow] = False
        units = self.data['units'].item().copy()
        units[units == unow] = 0
        self.update_unit(units)
    def sw_combinechannels(self):
        dlg = Dialog_CombineChannel(self)
        dlg.setupComboBox(self.n_maxunit)
        if dlg.exec():
            c, c1, c2 = dlg.getInfo()
            if c == 1:
                c1 = int(c1)
                c2 = int(c2)
                if c1 != c2:
                    units = self.data['units'].item().copy()
                    units[units == c2] = c1
                    islocked = self.is_locked.copy()
                    islocked[c2] = False
                    self.update_unit(units, islocked)
    def sw_squeezechannels(self):
        units = self.data['units'].item().copy()
        ct = np.zeros(self.n_maxunit)
        for i in range(self.n_maxunit):
            ct[i] = np.sum(units == i)
        us = np.nonzero(ct > 0)[0]
        nu = len(us)
        islocked = self.is_locked.copy()
        if nu < np.max(us)+1:
            for i in range(self.n_maxunit):
                if i < nu:
                    if i != us[i]:
                        units[units == us[i]] = i
                        islocked[i] = islocked[us[i]]
                else:
                    islocked[i] = False
            self.update_unit(units, islocked)
    def sw_removefromchannel(self):
        unow = self.unit_now
        if unow > 0:
            units = self.data['units'].item().copy()
            idx_selected = units == unow
            idx_selected_temp = []
            units[idx_selected] = 0
            locked = self.is_locked.copy()
            locked[unow] = False
            self.update_unit(units, locked, idx_selected, idx_selected_temp, 1)
    def sw_setnoisethreshold(self):
        if self.dlg_noisethreshold.exec():
            c, c1, c2 = self.dlg_noisethreshold.getInfo()
            if c == 1:
                if (c1 == '') or (c2 == ''):
                    self.threshold_noise = np.array([])
                else:
                    c1 = int(c1)
                    c2 = int(c2)
                    self.dlg_noisethreshold.setValue(c1, c2)
                    self.threshold_noise = np.array([c1,c2])
                    self.check_threshold_noise()
                    self.plt_all()
    def check_threshold_noise(self):
        if (len(self.threshold_noise) == 2):
            waves = self.data['waves'].item().copy()
            tid = (np.max(waves, axis=1) > self.threshold_noise[1]) | (np.min(waves, axis=1) < self.threshold_noise[0])
            if np.any(tid):
                self.idx_selected = tid
                self.idx_selected_temp = []
                self.select_locked()
                self.addhistory()
    def sw_sort_minimaldist(self):
        units_predict = []
        dlg = Dialog_getTextValue()
        if dlg.exec():
            c, a_std, dummy = dlg.getInfo()
            if len(a_std) == 0:
                a_std = np.infty
            else:
                a_std = int(a_std)
            if c == 1:
                dists = self.dist_waves
                if not np.all(np.isnan(dists)):
                    units_predict = np.nanargmin(dists, axis=1)
                    units = self.data['units'].item().copy()
                    units_predict[units_predict == 0] = -1
                    for i in range(self.n_maxunit):
                        if i == 0:
                            tu = units == -1
                            tupred = units_predict == -1
                        else:
                            tu = units == i
                            tupred = units_predict == i
                        if np.any(tupred):# & (~np.any(np.isnan(dists[tu, i]))): # distance
                            t_thres = a_std * np.std(dists[tu, i]) + np.mean(dists[tu, i])
                            units_predict[tupred] = units_predict[tupred] * (dists[tupred, i] < t_thres)
        return(units_predict)
    def sw_sort_cutfromhistdist(self):
        units_predict = []
        dlg = Dialog_getTextValue()
        if dlg.exec():
            c, unow, thres = dlg.getInfo()
            unow = int(unow)
            thres = int(thres)
            if (c == 1) and (unow > 0) and (unow < self.n_maxunit):
                dists = self.dist_waves
                if not np.all(np.isnan(dists)):
                    tid = dists[:, unow] < thres
                    units_predict = self.data['units'].item().copy()
                    units_predict[tid] = unow
        return(units_predict)
    def sw_singlecurvestats(self):
        idp = self.get_selected()
        if np.sum(idp) == 1:
            idp = np.where(idp)[0][0]
            dlg = Dialog_plot()
            dlg.fig.setBackground('w')
            waves = self.data['waves'].item().copy()
            nw = waves.shape[1]
            ns = self.n_phaseshift
            tcol = 0
            for i in range(self.n_maxunit):
                if len(self.dist_shift[i])>0:
                    tplt = dlg.fig.addPlot(row=0, col=tcol)
                    titem = pg.PlotCurveItem(self.dist_shift[i][idp], pen=pg.mkPen(self.color_unit[i]))
                    tplt.addItem(titem)
                    tplt.setXRange(ns-nw-0.5, nw * 2 - ns + 0.5,padding = 0)
                    tplt = dlg.fig.addPlot(row=1, col=tcol)
                    titem = pg.PlotCurveItem(list(range(nw))+ self.shifts[idp, i], self.av_waves[i,], pen=pg.mkPen(self.color_unit[i]))
                    tplt.addItem(titem)
                    titem = pg.PlotCurveItem(list(range(nw)), waves[idp,], pen=pg.mkPen('k'))
                    tplt.addItem(titem)
                    tplt.setXRange(ns-nw-0.5, nw * 2 - ns + 0.5,padding = 0)
                    tcol = tcol + 1
            dlg.exec()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = SW_MainWindow()

    ui.show()
    # ui.folderName = './'
    # ui.load_folder()
    sys.exit(app.exec_())
