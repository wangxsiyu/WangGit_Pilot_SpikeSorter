import os
import numpy as np
import scipy.io as sio

class SpikeSorterIO():
    n_pixel = 52
    n_maxunit = 6
    dataall = []
    rawall = []
    fullpathlist = sessionlist = filelist = channellist = []
    channels = sessions = []
    n_channel = n_sessionnow = None
    channelnow = idxnow = filenow = None
    waves = units = sid = spikeTimes = rawrating = activesession = None

    def __init__(self) -> None:
        pass
    
    def set_activesession(self, sid = None, mode = "exact"):
        self.autosave()
        if mode == "exact" and len(sid) > 0:
            self.activesession = sid
        elif mode == "all":
            self.activesession = np.ones(self.n_sessionnow)
        elif mode == "add" and len(sid) > 0:
            self.activesession[sid] = 1
        elif mode == "remove" and len(sid) > 0:
            self.activesession[sid] = 0
        elif mode == "select" and len(sid) == 1:
            self.activesession = np.zeros(self.n_sessionnow)
            self.activesession[sid] = 1
        else:
            print('sid is wrong, ignored')
            return
        self.combineall()

    def setup_folder(self, foldername):
        fs = os.listdir(foldername)
        fs.sort()
        fs = [x for x in fs if not x.startswith('.')]
        files = []
        folders = []
        fullfiles = []
        for i in range(len(fs)):
            tfd = os.path.join(foldername, fs[i])
            tfs = os.listdir(tfd)
            tfs.sort()
            tfs = [x for x in tfs if x.startswith('waveforms')]
            files.extend(tfs)
            folders.extend([fs[i]] * len(tfs))
            fullfiles.extend([os.path.join(tfd, x) for x in tfs])
        self.channellist = [x.removeprefix('waveforms_').removesuffix('.mat') for x in files]
        self.filelist = files
        self.fullpathlist = fullfiles
        self.sessionlist = folders
        self.channels = np.unique(self.channellist)
        self.sessions = np.unique(self.sessionlist)
        self.n_channel = len(self.channels)
        self.choosefile(0)
    
    def choosefile(self, cid):
        self.channelnow = cid
        self.idxnow = [i for i,x in enumerate(self.channellist) if x == self.channels[cid]]
        self.filenow = [self.fullpathlist[x] for x in self.idxnow]
        self.n_sessionnow = len(self.filenow)
        self.rawall = []
        self.dataall = []
        for i in range(self.n_sessionnow):
            self.loadfile(self.filenow[i])  # import the first file
        self.activesession = np.ones(self.n_sessionnow)
        self.combineall()

    def loadfile(self, fname):
        raw = sio.loadmat(fname)
        raw = self.format_raw(raw)
        self.rawall.append(raw)
        data = raw.get('waveforms')
        data = self.format_data(data)
        self.dataall.append(data)
    
    def combineall(self):
        self.units = np.empty(0)
        self.waves = np.empty((0, self.n_pixel))
        self.sid = np.empty(0)
        self.spikeTimes = np.empty(0)
        self.rawrating = np.empty((0, self.n_maxunit))
        if self.n_sessionnow is not None:
            for i in range(self.n_sessionnow):
                if self.activesession[i]:
                    tw = self.dataall[i]['waves'].item()
                    tu = self.dataall[i]['units'].item()
                    if tu.size < 5:
                        continue
                    trt = self.rawall[i]['rater_confidence'].squeeze()
                    trt = trt[:self.n_maxunit]
                    tsid = np.ones(len(tu)) * i
                    tst = self.dataall[i]['spikeTimes'].item().squeeze()
                    self.units = np.hstack((self.units, tu))
                    self.waves = np.vstack((self.waves, tw))
                    self.sid = np.hstack((self.sid, tsid))
                    self.spikeTimes = np.hstack((self.spikeTimes, tst))
                    self.rawrating = np.vstack((self.rawrating, trt))
        self.rating = np.mean(self.rawrating, axis = 0)

    def format_raw(self, raw):
        if 'rater_confidence' not in raw:
            print('initialize rater_confidence')
            raw['rater_confidence'] = np.zeros((self.n_maxunit))
            raw['rater_confidence'] = np.int64(raw['rater_confidence'])
        return raw

    def format_data(self, data):
        units = data['units'].item().copy()
        if (len(units) == 1):
            units = units[0]
        if (units.dtype != 'float'):
            units = np.float_(units)
        units = np.array(units)
        units[(units > self.n_maxunit) | (units < -1)] = 0
        data['units'].itemset(units)
        waves = data['waves'].item().copy()
        data['waves'].itemset(waves.T)
        if waves.shape[1] == self.n_pixel: # rotate when 52x52
            print(f'warning: {self.n_pixel} waves were loaded, confused on matrix rotation!!!')
        return data
    def autosave(self):
        self.autobackup()
        for i in range(self.n_sessionnow):
            if self.activesession[i]:               
                # reverse waves
                waves = self.dataall[i]['waves'].item().copy()
                self.dataall[i]['waves'].itemset(waves.T)
                mdict = self.rawall[i]
                mdict['waveforms'] = self.dataall[i]
                sio.savemat(self.filenow[i], mdict)
                self.dataall[i]['waves'].itemset(waves)
        print('saved successfully')
    def autobackup(self):
        if self.n_sessionnow is not None:
            for i in range(self.n_sessionnow):
                if self.activesession[i]:
                    tid = self.sid == i
                    self.dataall[i]['units'].itemset(self.units[tid]) 
                    if self.rating.dtype == 'int32':
                        self.rawall[i]['rater_confidence'] = self.rating
                    
# test = SpikeSorterIO()
# test.setup_folder("W:\\Wang_Projects\\2022_Wang_Averbeck_Attractor_Uncertainty\\SpikeSorting\\version_Siyu\\Voltaire")