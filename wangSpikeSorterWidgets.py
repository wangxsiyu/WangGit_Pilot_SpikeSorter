from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMainWindow, QDialog, QPushButton, QComboBox, QTextEdit, QMessageBox
from pyqtgraph import PlotWidget, GraphicsLayoutWidget, plot
import pyqtgraph as pg
import numpy as np

class Dialog_plot(QDialog):  # Inheritance of the QDialog class
    def __init__(self, parent = None):
        super(Dialog_plot, self).__init__(parent)
        self.initUI()
    def initUI(self):
        self.setWindowTitle("Combine channels")  # Window Title
        self.setGeometry(100, 100, 2000, 1800)
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
        self.c3 = QtWidgets.QLabel()
        self.c4 = QtWidgets.QLabel()
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)  # window to create confirmation and cancellation buttons
        self.glayout = QtWidgets.QGridLayout()
        self.glayout.addWidget(self.c1, 0, 1)
        self.glayout.addWidget(self.c2, 1, 1)
        self.glayout.addWidget(self.c3, 0, 0)
        self.glayout.addWidget(self.c4, 1, 0)
        self.glayout.addWidget(self.buttons, 0, 2)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.accepted.connect(self.done_choose)
        self.rejected.connect(self.cancel_choose)
        self.setLayout(self.glayout)
    def setLabel(self, str1, str2):
        self.c3.setText(str(str1))
        self.c4.setText(str(str2))
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
    def __init__(self) -> None:
        dlg = Dialog_getTextValue()
        dlg.setLabel('screen ratio 1', 'leave empty')
        dlg.setValue('2', 'welcome')
        if dlg.exec():
            c, l1, l2 = dlg.getInfo()
            self.ratio = float(l1)
        else:
            self.ratio = 2
    def getwindowsizes(self):
        sz = {'mainwindow':(1410, 702),\
                'group_units':(780,0,621,591), \
                'graphicsView_units':(10, 30, 601, 551),\
                'group_PCA':(10, 10, 761, 431), \
                'comboBox_PC1':(10, 375, 71, 41),\
                'comboBox_PC2':(10, 400, 71, 41),\
                'checkBox_showallunits':(90, 385, 71, 20),\
                'textBox_percentunits':(90, 405, 71, 20),\
                'pushButton_Add':(250, 390, 81, 32),\
                'pushButton_Remove':(330, 390, 81, 32),\
                'pushButton_resettemp':(410, 390, 81, 32),\
                'pushButton_noise':(590, 390, 81, 32),\
                'pushButton_Confirm':(670, 390, 81, 32),\
                'checkBox_showunsorted':(485, 385, 130, 20),\
                'checkBox_usefordist':(485, 405, 130, 20),\
                'graphicsView_pca':(10, 30, 351, 351),\
                'graphicsView_raw':(370, 30, 381, 351),\
                'pushButton_reset':(170, 390, 81, 32),\
                'group_Methods':(10, 440, 261, 211),\
                'comboBox_ClusterMethods':(10, 40, 204, 26),\
                'checkBox_locked':(10, 70, 100, 20),\
                'pushButton_sortall':(10, 170, 113, 32),\
                'frame_Channel':(780, 600, 621, 51),\
                'label_channel':(10, 10, 171, 31),\
                'comboBox_activesessions':(70, 5, 320, 20),\
                'comboBox_passivesessions':(70, 25, 320, 20),\
                'comboBox_channel':(390, 5, 80, 20),\
                'comboBox_selectsession':(390, 25, 80, 20),\
                'pushButton_previouschannel':(470, 10, 73, 32),\
                'pushButton_nextchannel':(540, 10, 73, 32),\
                'groupBox_side':(280, 440, 491, 211),\
                'graphicsView_side1':(0, 20, 241, 191),\
                'graphicsView_side2':(240, 21, 251, 191),\
                'menubar':(0, 0, 1410, 24)}
        ratio = self.ratio
        for i, j in sz.items():
            sz[i] = [(ratio * k) for k in j]
        return sz
    def my_QtCore_QRect(self, x):
        return QtCore.QRect(x[0], x[1], x[2], x[3])
    def setupUi(self, MainWindow):
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
        self.group_PCA = QtWidgets.QGroupBox(self.centralwidget)
        self.group_PCA.setGeometry(self.my_QtCore_QRect(sz['group_PCA']))
        self.group_PCA.setObjectName("group_PCA")
        self.comboBox_PC1 = QtWidgets.QComboBox(self.group_PCA)
        self.comboBox_PC1.setGeometry(self.my_QtCore_QRect(sz['comboBox_PC1']))
        self.comboBox_PC1.setObjectName("comboBox_PC1")
        self.comboBox_PC1.addItem("")
        self.comboBox_PC1.addItem("")
        self.comboBox_PC1.addItem("")
        self.comboBox_PC1.addItem("")
        self.comboBox_PC2 = QtWidgets.QComboBox(self.group_PCA)
        self.comboBox_PC2.setGeometry(self.my_QtCore_QRect(sz['comboBox_PC2']))
        self.comboBox_PC2.setObjectName("comboBox_PC2")
        self.comboBox_PC2.addItem("")
        self.comboBox_PC2.addItem("")
        self.comboBox_PC2.addItem("")
        self.comboBox_PC2.addItem("")
        self.checkBox_showallunits = QtWidgets.QCheckBox(self.group_PCA)
        self.checkBox_showallunits.setGeometry(self.my_QtCore_QRect(sz['checkBox_showallunits']))
        self.checkBox_showallunits.setObjectName("checkBox_showallunits")
        self.textBox_percentunits = QtWidgets.QLineEdit(self.group_PCA)
        self.textBox_percentunits.setGeometry(self.my_QtCore_QRect(sz['textBox_percentunits']))
        self.textBox_percentunits.setObjectName("textBox_percentunits")
        self.pushButton_Add = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_Add.setGeometry(self.my_QtCore_QRect(sz['pushButton_Add']))
        self.pushButton_Add.setObjectName("pushButton_Add")
        self.pushButton_Remove = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_Remove.setGeometry(self.my_QtCore_QRect(sz['pushButton_Remove']))
        self.pushButton_Remove.setObjectName("pushButton_Remove")
        self.pushButton_resettemp = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_resettemp.setGeometry(self.my_QtCore_QRect(sz['pushButton_resettemp']))
        self.pushButton_resettemp.setObjectName("pushButton_resettemp")
        self.pushButton_noise = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_noise.setGeometry(self.my_QtCore_QRect(sz['pushButton_noise']))
        self.pushButton_noise.setObjectName("pushButton_noise")
        self.pushButton_Confirm = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_Confirm.setGeometry(self.my_QtCore_QRect(sz['pushButton_Confirm']))
        self.pushButton_Confirm.setObjectName("pushButton_Confirm")
        self.checkBox_showunsorted = QtWidgets.QCheckBox(self.group_PCA)
        self.checkBox_showunsorted.setGeometry(self.my_QtCore_QRect(sz['checkBox_showunsorted']))
        self.checkBox_showunsorted.setObjectName("checkBox_showunsorted")
        self.checkBox_usefordist = QtWidgets.QCheckBox(self.group_PCA)
        self.checkBox_usefordist.setGeometry(self.my_QtCore_QRect(sz['checkBox_usefordist']))
        self.checkBox_usefordist.setObjectName("checkBox_usefordist")
        # self.checkBox_useasmodel = QtWidgets.QCheckBox(self.group_PCA)
        # self.checkBox_useasmodel.setGeometry(self.my_QtCore_QRect(490, 400, 111, 20))
        # self.checkBox_useasmodel.setChecked(True)
        # self.checkBox_useasmodel.setObjectName("checkBox_useasmodel")
        self.graphicsView_pca = PlotWidget(self.group_PCA)
        self.graphicsView_pca.setGeometry(self.my_QtCore_QRect(sz['graphicsView_pca']))
        self.graphicsView_pca.setObjectName("graphicsView_pca")
        self.graphicsView_raw = PlotWidget(self.group_PCA)
        self.graphicsView_raw.setGeometry(self.my_QtCore_QRect(sz['graphicsView_raw']))
        self.graphicsView_raw.setObjectName("graphicsView_raw")
        self.pushButton_reset = QtWidgets.QPushButton(self.group_PCA)
        self.pushButton_reset.setGeometry(self.my_QtCore_QRect(sz['pushButton_reset']))
        self.pushButton_reset.setObjectName("pushButton_reset")
        self.group_Methods = QtWidgets.QGroupBox(self.centralwidget)
        self.group_Methods.setGeometry(self.my_QtCore_QRect(sz['group_Methods']))
        self.group_Methods.setObjectName("group_Methods")
        self.comboBox_ClusterMethods = QtWidgets.QComboBox(self.group_Methods)
        self.comboBox_ClusterMethods.setGeometry(self.my_QtCore_QRect(sz['comboBox_ClusterMethods']))
        self.comboBox_ClusterMethods.setObjectName("comboBox_ClusterMethods")
        self.comboBox_ClusterMethods.addItem("")
        self.comboBox_ClusterMethods.addItem("")
        self.comboBox_ClusterMethods.addItem("")
        self.checkBox_locked = QtWidgets.QCheckBox(self.group_Methods)
        self.checkBox_locked.setGeometry(self.my_QtCore_QRect(sz['checkBox_locked']))
        self.checkBox_locked.setObjectName("checkBox_locked")
        # self.pushButton_sortsafe = QtWidgets.QPushButton(self.group_Methods)
        # self.pushButton_sortsafe.setGeometry(self.my_QtCore_QRect(10, 140, 171, 32))
        # self.pushButton_sortsafe.setObjectName("pushButton_sortsafe")
        self.pushButton_sortall = QtWidgets.QPushButton(self.group_Methods)
        self.pushButton_sortall.setGeometry(self.my_QtCore_QRect(sz['pushButton_sortall']))
        self.pushButton_sortall.setObjectName("pushButton_sortall")
        # self.textEdit_sortsafe = QtWidgets.QTextEdit(self.group_Methods)
        # self.textEdit_sortsafe.setGeometry(self.my_QtCore_QRect(180, 140, 71, 31))
        # self.textEdit_sortsafe.setObjectName("textEdit_sortsafe")
        self.frame_Channel = QtWidgets.QFrame(self.centralwidget)
        self.frame_Channel.setGeometry(self.my_QtCore_QRect(sz['frame_Channel']))
        self.frame_Channel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Channel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Channel.setObjectName("frame_Channel")
        self.label_channel = QtWidgets.QLabel(self.frame_Channel)
        self.label_channel.setGeometry(self.my_QtCore_QRect(sz['label_channel']))
        self.label_channel.setObjectName("label_channel")
        # self.textEdit_channel = QtWidgets.QTextEdit(self.frame_Channel)
        # self.textEdit_channel.setGeometry(self.my_QtCore_QRect(190, 10, 81, 31))
        # self.textEdit_channel.setObjectName("textEdit_channel")
        self.comboBox_channel = QtWidgets.QComboBox(self.frame_Channel)
        self.comboBox_channel.setGeometry(self.my_QtCore_QRect(sz['comboBox_channel']))
        self.comboBox_channel.setObjectName("comboBox_channel")
        self.comboBox_activesessions = QtWidgets.QComboBox(self.frame_Channel)
        self.comboBox_activesessions.setGeometry(self.my_QtCore_QRect(sz['comboBox_activesessions']))
        self.comboBox_activesessions.setObjectName("comboBox_activesessions")
        self.comboBox_passivesessions = QtWidgets.QComboBox(self.frame_Channel)
        self.comboBox_passivesessions.setGeometry(self.my_QtCore_QRect(sz['comboBox_passivesessions']))
        self.comboBox_passivesessions.setObjectName("comboBox_passivesessions")
        self.comboBox_selectsession = QtWidgets.QComboBox(self.frame_Channel)
        self.comboBox_selectsession.setGeometry(self.my_QtCore_QRect(sz['comboBox_selectsession']))
        self.comboBox_selectsession.setObjectName("comboBox_selectsession")
        self.comboBox_selectsession.addItem("")
        self.comboBox_selectsession.addItem("")
        self.comboBox_selectsession.addItem("")
        self.comboBox_selectsession.addItem("")
        self.comboBox_selectsession.addItem("")
        self.comboBox_selectsession.addItem("")
        self.comboBox_selectsession.addItem("")
        # self.pushButton_gotochannel = QtWidgets.QPushButton(self.frame_Channel)
        # self.pushButton_gotochannel.setGeometry(self.my_QtCore_QRect(280, 10, 113, 32))
        # self.pushButton_gotochannel.setObjectName("pushButton_gotochannel")
        self.pushButton_previouschannel = QtWidgets.QPushButton(self.frame_Channel)
        self.pushButton_previouschannel.setGeometry(self.my_QtCore_QRect(sz['pushButton_previouschannel']))
        self.pushButton_previouschannel.setObjectName("pushButton_previouschannel")
        self.pushButton_nextchannel = QtWidgets.QPushButton(self.frame_Channel)
        self.pushButton_nextchannel.setGeometry(self.my_QtCore_QRect(sz['pushButton_nextchannel']))
        self.pushButton_nextchannel.setObjectName("pushButton_nextchannel")
        self.groupBox_side = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_side.setGeometry(self.my_QtCore_QRect(sz['groupBox_side']))
        self.groupBox_side.setObjectName("groupBox_side")
        self.graphicsView_side1 = PlotWidget(self.groupBox_side)
        self.graphicsView_side1.setGeometry(self.my_QtCore_QRect(sz['graphicsView_side1']))
        self.graphicsView_side1.setObjectName("graphicsView_side1")
        self.graphicsView_side2 = PlotWidget(self.groupBox_side)
        self.graphicsView_side2.setGeometry(self.my_QtCore_QRect(sz['graphicsView_side2']))
        self.graphicsView_side2.setObjectName("graphicsView_side2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(self.my_QtCore_QRect(sz['menubar']))
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
        self.removeunitswithfewunits = QtWidgets.QAction(MainWindow)
        self.removeunitswithfewunits.setObjectName("removeunitswithfewunits")
        self.menuFunction.addAction(self.removeunitswithfewunits)
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
        self.comboBox_ClusterMethods.setItemText(2, _translate("MainWindow", "Gaussian Mixture Model (unsupervised)"))
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
        self.removeunitswithfewunits.setText(_translate("MainWindow", "remove neurons with few units"))
        self.comboBox_selectsession.setItemText(0, _translate("MainWindow", "return"))
        self.comboBox_selectsession.setItemText(1, _translate("MainWindow", "select all"))
        self.comboBox_selectsession.setItemText(2, _translate("MainWindow", "remove from active"))
        self.comboBox_selectsession.setItemText(3, _translate("MainWindow", "add to active"))
        self.comboBox_selectsession.setItemText(4, _translate("MainWindow", "select one (active)"))
        self.comboBox_selectsession.setItemText(5, _translate("MainWindow", "select one (passive)"))
        self.comboBox_selectsession.setItemText(6, _translate("MainWindow", "view all"))