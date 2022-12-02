from wangSpikeSorterWidgets import Dialog_plot, Dialog_getTextValue, Dialog_CombineChannel, MultiLine
import numpy as np
from wangSpikeSorterIO import SpikeSorterIO
import time

class SpikeSorterCPU(SpikeSorterIO):
    is_usefordist = []
    def __init__(self) -> None:
        super().__init__()  

    def comp_default(self):
        # pc = self.pca
        units = self.units
        waves = self.waves
        npix = self.n_pixel
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
        self.dist_waves = dist
        # self.dist_waves_raw = dist

        # shifts = np.zeros((waves.shape[0], self.n_maxunit))
        # # compute phase-shift distance
        # if False:
        #     dist = np.zeros((waves.shape[0], self.n_maxunit))
        #     ns = self.n_phaseshift
        #     nw = waves.shape[1]
        #     nu = waves.shape[0]
        #     self.dist_shift = list()
        #     for i in range(self.n_maxunit):
        #         if not np.any(np.isnan(av[i,])):
        #             tdists = np.zeros((nu, 2*(nw - ns)+1))
        #             for j in range(2*(nw - ns)+1):
        #                 tx = j - (nw - ns)
        #                 trg1 = range(max(tx, 0), min(tx + nw, nw))
        #                 trg2 = range(max(nw - ns - j, 0), min(nw + nw - ns - j , nw))
        #                 twaves = waves.copy()
        #                 tav = av[i, trg2]
        #                 twaves = twaves[:, trg1]
        #                 twaves_av = np.mean(twaves, axis = 1)
        #                 twaves = (twaves.T - twaves_av).T + np.mean(tav)
        #                 tdists[:,j] = np.mean((twaves - tav)**2, axis = 1)
        #             self.dist_shift.append(tdists)
        #             shifts[:,i] = np.argmin(tdists, axis = 1) - (nw - ns)
        #             dist[:, i] = np.min(tdists, axis = 1)
        #         else:
        #             self.dist_shift.append([])
        #             shifts[:,i] = np.NaN
        #             dist[:, i] = np.NaN
        #     self.dist_waves_phase = dist
        #     self.shifts = shifts
        # self.dist_waves = self.dist_waves_raw
        return
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
    def tic(self):
        self.t_tic = time.perf_counter()
    def toc(self, option = 0):
        self.t_toc = time.perf_counter()
        print(f"Runtime: {self.t_toc - self.t_tic:0.4f} seconds")
        if (option == 1):
            self.t_tic = self.t_toc


    def refreshCPU(self):
        self.idx_selected = []
        self.idx_selected_temp = []
        self.history_units = []
        self.history_locked = []
        self.history_idx = []
        self.history_idxtemp = []
        self.redo_units = []
        self.redo_locked = []
        self.redo_idx = []
        self.redo_idxtemp = []

    def resetCPU(self):
        self.refreshCPU()
        self.unit_now = 0
        self.is_addhistory = True
        self.is_locked = np.zeros(self.n_maxunit) == 1
    
    def get_lockedlines(self):
        units = self.units.copy()
        out = np.zeros_like(units)
        for i in range(self.n_maxunit):
            if self.is_locked[i]:
                out[units == i] = 1
        out[units == -1] = 1 # for noise
        return(out == 1)
    def select_locked(self):
        idl = self.get_lockedlines()
        if len(self.idx_selected) > 0:
            self.idx_selected = self.idx_selected & ~idl
        if len(self.idx_selected_temp) > 0:
            self.idx_selected_temp = self.idx_selected_temp & ~idl
    
    def addhistory(self):
        if self.is_addhistory:
            self.history_units.append(self.units.copy())
            self.history_locked.append(self.is_locked.copy())
            self.history_idx.append(self.idx_selected.copy())
            self.history_idxtemp.append(self.idx_selected_temp.copy())
            
            # print(f"add history, {len(self.history_units)}")


    
