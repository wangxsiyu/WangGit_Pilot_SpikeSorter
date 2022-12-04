from wangSpikeSorterWidgets import Dialog_plot, Dialog_getTextValue, Dialog_CombineChannel, MultiLine, Ui_MainWindow
from wangSpikeSorterCPU import SpikeSorterCPU
from wangChronicViewer import Ui_viewer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMainWindow, QDialog, QPushButton, QComboBox, QTextEdit, QMessageBox
from pyqtgraph import PlotWidget, GraphicsLayoutWidget, plot
import pyqtgraph as pg
import numpy as np
from scipy.io import loadmat
import matplotlib.path as mplPath
from intersect import intersection
import glob
from random import sample, randint
from sklearn import mixture
from PyQt5.QtGui import QKeyEvent
import sys
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class SW_MainWindow(QMainWindow, Ui_MainWindow, SpikeSorterCPU):
    data = None
    key_pressed = pyqtSignal(QKeyEvent)
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent = parent)
        self.setupUi(self)
        self.setup_SW()
        self.key_pressed.connect(self.onkeyPressEvent)
    def keyPressEvent(self, event):
        # print('key pressed')
        self.key_pressed.emit(event)
        return super().keyPressEvent(event)
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
        self.textBox_percentunits.textChanged.connect(self.sw_percentunits)
        self.textBox_percentunits.returnPressed.connect(self.sw_percentunitschanged)
        self.RemoveChannel.triggered.connect(self.sw_removechannel)
        self.CombineChannels.triggered.connect(self.sw_combinechannels)
        self.SqueezeChannels.triggered.connect(self.sw_squeezechannels)
        self.RemovefromChannel.triggered.connect(self.sw_removefromchannel)
        self.setnoisethreshold.triggered.connect(self.sw_setnoisethreshold)
        self.removeunitswithfewunits.triggered.connect(self.sw_removeunitswithfewunits)
        self.sortunitsbyrange.triggered.connect(self.sw_sortunitsbyrange)
        # self.seestatssinglecurve.triggered.connect(self.sw_singlecurvestats)
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
        self.comboBox_selectsession.activated.connect(self.sw_selectsessions)
    def setup_widget_viewall(self):
        self.widget_viewall = Ui_viewer()
        self.widget_viewall.setup_viewer(2, 8, self.color_unit, self.ratio)
    def setup_axes(self):
        self.setup_widget_viewall()
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
    def sw_combobox_pc(self):
        if self.is_loaddata:
            n1 = self.comboBox_PC1.currentText()
            n1 = int(n1[2]) - 1
            n2 = self.comboBox_PC2.currentText()
            n2 = int(n2[2]) - 1
            pc = self.pca[:, (n1, n2)]
            self.pc_now = pc
            self.pca_polygon_vertices = []
    def setup_reset(self):
        self.resetCPU()
        self.checkBox_usefordist.setChecked(True)
        self.comboBox_PC1.setCurrentIndex(0)
        self.comboBox_PC2.setCurrentIndex(1)
        self.comboBox_selectsession.setCurrentIndex(0)
        self.reset_selectiontool(0)
        self.model_GMM = None
        self.model_GMM_pred = None
    def sw_showunsorted(self):
        # print('show unsorted')
        self.plt_pca()
        self.plt_raw()
        self.plt_selectiontool()
    def sw_showallunits(self):
        self.get_randomsubsets()
        self.plt_all()
    def sw_combobox_pc_plt(self):
        self.sw_combobox_pc()
        self.plt_pca()
        self.plt_selectiontool()
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
        # self.toc(1)
        self.plt_noise()
    def plt_noise(self):
        waves = self.waves.copy()
        units = self.units.copy()

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
        units = self.units.copy()
        pc = self.pc_now
        if pc.shape[0] == 1:
            self.pca_scatter[units.__int__()].setData(x = pc[0], y= pc[1])
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
        waves = self.waves.copy()
        units = self.units.copy()
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
    def plt_locked(self):
        for i in range(self.n_maxunit):
            if self.is_locked[i]:
                str_L = 'Locked'
                self.units_axes[1,i].setTitle(str_L)
            else:
                str_L = ''
                self.units_axes[1,i].setTitle(str_L)
    def plt_units(self):
        waves = self.waves.copy()
        units = self.units.copy()
        if units.size == 1:
            return
        trg = np.array([np.infty, -np.infty])
        for i in range(self.n_maxunit):
            if i == self.unit_now:
                self.units_axes[0, i].getViewBox().setBackgroundColor("m")
            else:
                self.units_axes[0, i].getViewBox().setBackgroundColor("w")
            tid = (units == i).squeeze()
            ntotunit = np.sum(tid)
            str = f"{ntotunit:.0f}, {self.rating[i]}"
            tid = tid & self.idx_randomsubset
            n_uniti = np.sum(tid)
            n_unitall = len(units)
            # str = str + str_L
            self.units_axes[0, i].setTitle(str) # fake title
            self.units_axes[0, i].clear()
            self.units_axes[1, i].clear()
            self.units_axes[2, i].clear()
            self.units_axes[3, i].clear()
            if n_uniti > 2:
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
                st = self.spikeTimes.squeeze()
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
    
    @pyqtSlot(QKeyEvent)
    def onkeyPressEvent(self, event):
        key = event.key()
        print(f'key pressed: {key}')
        if self.is_loaddata == 0:
            return
        if key < 200: #ascii codes range
            str = chr(key)
            # print(key, str)
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
            if str == '=' or str == '[':
                if self.rating.dtype == 'int32':
                    self.rating[self.unit_now] =self.rating[self.unit_now] + 1
                else:
                    self.rating = np.array([int(x) for x in self.rating], dtype = 'int32')
                self.plt_units()
                self.autosave()
            if str == '-' or str == ']':
                if self.rating.dtype == 'int32':
                    self.rating[self.unit_now] = self.rating[self.unit_now] - 1
                else:
                    self.rating = np.array([int(x) for x in self.rating], dtype = 'int32')
                self.plt_units()
                self.autosave()
    def sw_sort_minimaldist(self):
        units_predict = []
        dlg = Dialog_getTextValue()
        dlg.setLabel('std', 'leave empty')
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
                    units = self.units.copy()
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
        dlg.setLabel('which unit', 'threshold')
        if dlg.exec():
            c, unow, thres = dlg.getInfo()
            unow = int(unow)
            thres = int(thres)
            if (c == 1) and (unow > 0) and (unow < self.n_maxunit):
                dists = self.dist_waves
                if not np.all(np.isnan(dists)):
                    tid = dists[:, unow] < thres
                    units_predict = self.units.copy()
                    units_predict[tid] = unow
        return(units_predict)

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
        waves = self.waves.copy()
        nl = waves.shape[0]
        npixel = self.n_pixel
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
    
    def sw_previouschannel(self):
        self.channelnow = self.channelnow - 1
        if self.channelnow < 0:
            self.channelnow = 0
        self.readfile(self.channelnow)
    def sw_nextchannel(self):
        self.channelnow = self.channelnow + 1
        if self.channelnow >= self.n_channel:
            self.channelnow = self.n_channel - 1
        self.readfile(self.channelnow)
    
    def sw_gotochannel(self):
        fnow = self.comboBox_channel.currentText()
        xx = [x in fnow for x in self.channels]
        cid = np.where(xx)[0][0]
        self.readfile(cid)
    
    
    def sw_removeunitswithfewunits(self):
        dlg = Dialog_getTextValue()
        dlg.setLabel('number threshold', '')
        dlg.setValue('1000','')
        if dlg.exec():
            c, nthres, dummy = dlg.getInfo()
            nthres = float(nthres)
            unitsnew = self.units.copy()
            for i in range(1, self.n_maxunit):
                for j in range(self.n_sessionnow):
                    tid = (self.units == i) & (self.sid == j)
                    if np.sum(tid) < nthres:
                        print(f'removing unit {i} from session {j}')
                        unitsnew[tid] = -1
            self.update_unit(unitsnew)


    def sw_sortunitsbyrange(self):
        unitsnew = self.units.copy()
        unitsnew[unitsnew > 0] = 0
        waves = self.waves.copy()
        rgwv = np.max(waves, axis = 1) - np.min(waves, axis=1)
        for j in range(self.n_sessionnow):
            trg = np.zeros(self.n_maxunit)
            trg[0] = np.Inf
            for i in range(1, self.n_maxunit):
                tid = (self.units == i) & (self.sid == j)
                if np.any(tid):
                    trg[i] = np.mean(rgwv[tid])
                else:
                    trg[i] = -np.Inf
            tod = np.argsort(-trg)
            for i in range(1, self.n_maxunit):
                tid = (self.units == i) & (self.sid == j)
                if np.any(tid):
                    unitsnew[tid] = tod[i]
        self.update_unit(unitsnew)


    def sw_sort_gmm(self):
        units_predict = []
        dlg = Dialog_getTextValue()
        dlg.setLabel('pca dim', 'threshold')
        if dlg.exec():
            c, npca, perc = dlg.getInfo()
            if len(npca) == 0:
                npca = 5
            else:
                npca = int(npca)
            units = self.units.copy()
            units_cluster = np.unique(units)
            units_cluster = units_cluster[units_cluster > 0]
            ncluster = len(units_cluster)
            if ncluster == 0:
                return
            # if self.model_GMM is None or self.model_GMM.n_components != ncluster:
            self.model_GMM = mixture.GaussianMixture(n_components=ncluster, covariance_type='diag', warm_start = True)
            pc = self.pca[:,:npca]
            if npca > 0:
                pc1 = pc[units >=0 & self.is_usefordist,:]
                self.model_GMM = self.model_GMM.fit(pc1)
                self.model_GMM_pred = self.model_GMM.predict_proba(pc)
                idreorder = [np.argmax(np.mean(self.model_GMM_pred[units == x, :], axis = 0)) for x in units_cluster]
                if len(np.unique(idreorder)) == len(idreorder):
                    self.model_GMM_pred = self.model_GMM_pred[:, idreorder]
            units_predict = units
            tunits = np.argmax(self.model_GMM_pred, axis = 1)
            tunits = np.array([units_cluster[x] for x in tunits])
            if perc != '':
                perc = float(perc)
                tpercs = np.max(self.model_GMM_pred, axis = 1)
                tid = (units >= 0) & (tpercs >= perc)
            else:
                tid = units >= 0
            units_predict[tid] = tunits[tid]
        return(units_predict)

    def sw_sortall(self):
        if self.comboBox_ClusterMethods.currentText() == "minimal distance":
            units = self.sw_sort_minimaldist()
        if self.comboBox_ClusterMethods.currentText() == "cut from histogram of distances":
            units = self.sw_sort_cutfromhistdist()
        if self.comboBox_ClusterMethods.currentText() == "Gaussian Mixture Model (unsupervised)":
            units = self.sw_sort_gmm()
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
        units = self.units.copy()
        self.idx_selected = units == 0
        self.idx_selected_temp = []
        self.addhistory()
        self.plt_pca()
        self.plt_raw()
        self.plt_selectiontool()
    def sw_undo(self):
        # print(f"undo - nlist:{len(self.history_units)}")
        if len(self.history_units) > 1:
            self.redo_units = self.units.copy()
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
        units = self.units.copy()
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
                    units = self.units.copy()
                    units[units == c2] = c1
                    islocked = self.is_locked.copy()
                    islocked[c2] = False
                    self.update_unit(units, islocked)
    def sw_squeezechannels(self):
        units = self.units.copy()
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
            units = self.units.copy()
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
            waves = self.waves.copy()
            tid = (np.max(waves, axis=1) > self.threshold_noise[1]) | (np.min(waves, axis=1) < self.threshold_noise[0])
            if np.any(tid):
                self.idx_selected = tid
                self.idx_selected_temp = []
                self.select_locked()
                self.addhistory()
    
    def sw_reset(self):
        # self.setup_reset()
        units = self.units.copy()
        units = np.zeros(units.shape)
        units = np.int64(units)
        islocked = np.zeros_like(self.is_locked) == 1
        self.update_unit(units, islocked)
    def sw_load_folder(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            folderName = dlg.selectedFiles()[0]
            if folderName:
                self.load_folder(folderName)
    def update_selectedunit(self, idx, unitnew):
        units = self.units.copy()
        # if len([unitnew]) == len(idx):
        #     units[idx] = unitnew[idx]
        # else:
        units[idx] = unitnew
        self.update_unit(units)
    
    def update_unit(self, units, locked = [], idselect = [], idtemp = [], isoverwrite = 0):
        oldunits = self.units.copy()
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
        self.units = units
        self.addhistory()
        self.comp_default()
        self.plt_all()
        self.autosave()
    
    def load_folder(self, folderName):
        self.setup_folder(folderName)
        self.comboBox_channel.clear()
        self.comboBox_channel.addItems(self.channels)
        self.readfile(0)
    
    def readfile(self, cid):
        self.choosefile(cid)        
        # add other default operations
        self.label_channel.setText(f'{cid+1} / {self.n_channel}: {self.channels[cid]}')
        self.comboBox_channel.setCurrentIndex(cid)
        # self.textEdit_channel.setText(f'{fid+1}')
        self.comboBox_activesessions.clear()
        self.comboBox_activesessions.addItems(self.filenow)
        
        self.comboBox_passivesessions.clear()
        self.comboBox_selectsession.setCurrentIndex(0)
        self.is_loaddata = True
        self.comp_setup()
        self.statusbar.showMessage(f"loaded channel: {self.channels[cid]}")

    def get_randomsubsets(self):
        units = self.units.copy()
        nu = units.size
        if (nu < 10000) or self.checkBox_showallunits.isChecked():
            self.idx_randomsubset = np.ones_like(units) == 1
        else:
            sids = np.unique(self.sid)
            tidx = np.empty(0, dtype = 'int64')
            for i in range(len(sids)):
                tid = np.where(sids[i] == self.sid)[0]
                tnsp = round(self.percentunits * len(tid))
                tidx = np.hstack((tidx, tid[sample(range(len(tid)), tnsp)]))
            self.idx_randomsubset = np.ones_like(units) == 0
            self.idx_randomsubset[tidx] = True
    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False
    def sw_percentunits(self):
        txt = self.textBox_percentunits.text()
        if self.isfloat(txt):
            self.percentunits = float(txt)
        else:
            self.default_percentunits()
    def sw_percentunitschanged(self):
        self.sw_percentunits()
        self.get_randomsubsets()
        self.plt_all()

    def default_percentunits(self):
        self.percentunits = 1.00
        if len(self.units) >= 10000:
            self.percentunits = round(10000/self.is_usefordist.size,2)
        self.textBox_percentunits.setText(str(self.percentunits))

    def comp_setup(self):
        self.setup_reset()
        self.is_usefordist = np.array(np.ones_like(self.units) == 1)        
        if len(self.units) >= 10000:
            self.checkBox_showallunits.setChecked(False)
        self.default_percentunits()
        self.textBox_percentunits.setText(str(self.percentunits))
        self.get_randomsubsets()

        # compute PCA
        # self.tic()
        waves = self.waves.copy()
        self.pca = self.PCA(waves)
        # self.toc()
        self.sw_combobox_pc()
        # self.toc()
        # self.n_phaseshift = int(waves.shape[1]*2/3)
        self.comp_default()
        # self.toc()
        self.check_threshold_noise()
        # self.toc()
        self.sw_combobox_pc()
        if self.units.size > 1:
            self.plt_all()
            self.addhistory()
        else:
            out = QMessageBox.warning(self, "Warning", "This channel is empty, move on to the next")
            if out:
                self.sw_nextchannel()
        


    def sw_selectsessions(self):
        txt = self.comboBox_selectsession.currentText()
        if txt == "select all":
            self.set_activesession(mode = "all")
        elif txt == "remove from active":
            atxt = self.comboBox_activesessions.currentText()
            aid = [i for i,x in enumerate(self.filenow) if x == atxt]
            self.set_activesession(aid, mode = "remove")
        elif txt == "add to active":
            atxt = self.comboBox_passivesessions.currentText()
            aid = [i for i,x in enumerate(self.filenow) if x == atxt]
            self.set_activesession(aid, mode = "add")
        elif txt == "select one (active)":
            atxt = self.comboBox_activesessions.currentText()
            aid = [i for i,x in enumerate(self.filenow) if x == atxt]
            self.set_activesession(aid, mode = "select")
        elif txt == "select one (passive)":
            atxt = self.comboBox_passivesessions.currentText()
            aid = [i for i,x in enumerate(self.filenow) if x == atxt]
            self.set_activesession(aid, mode = "select")
        elif txt == "view all":
            self.widget_viewall.show()
            self.widget_viewall.plot(self.dataall.copy(), self.color_unit, self.filenow)
        
        self.comboBox_activesessions.clear()
        if any(self.activesession == 1):
            tlst = [self.filenow[x] for x in np.where(self.activesession == 1)[0]]
            self.comboBox_activesessions.addItems(tlst)
        
        self.comboBox_passivesessions.clear()
        if any(self.activesession == 0):
            tlst = [self.filenow[x] for x in np.where(self.activesession == 0)[0]]
            self.comboBox_passivesessions.addItems(tlst)

        self.comp_setup()
    # def sw_singlecurvestats(self):
    #     idp = self.get_selected()
    #     if np.sum(idp) == 1:
    #         idp = np.where(idp)[0][0]
    #         dlg = Dialog_plot()
    #         dlg.fig.setBackground('w')
    #         waves = self.data['waves'].item().copy()
    #         nw = waves.shape[1]
    #         ns = self.n_phaseshift
    #         tcol = 0
    #         for i in range(self.n_maxunit):
    #             if len(self.dist_shift[i])>0:
    #                 tplt = dlg.fig.addPlot(row=0, col=tcol)
    #                 titem = pg.PlotCurveItem(self.dist_shift[i][idp], pen=pg.mkPen(self.color_unit[i]))
    #                 tplt.addItem(titem)
    #                 tplt.setXRange(ns-nw-0.5, nw * 2 - ns + 0.5,padding = 0)
    #                 tplt = dlg.fig.addPlot(row=1, col=tcol)
    #                 titem = pg.PlotCurveItem(list(range(nw))+ self.shifts[idp, i], self.av_waves[i,], pen=pg.mkPen(self.color_unit[i]))
    #                 tplt.addItem(titem)
    #                 titem = pg.PlotCurveItem(list(range(nw)), waves[idp,], pen=pg.mkPen('k'))
    #                 tplt.addItem(titem)
    #                 tplt.setXRange(ns-nw-0.5, nw * 2 - ns + 0.5,padding = 0)
    #                 tcol = tcol + 1
    #         dlg.exec()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = SW_MainWindow()

    ui.show()
    # ui.folderName = './'
    # ui.load_folder()
    sys.exit(app.exec_())
