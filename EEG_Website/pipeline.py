import pandas as pd
import numpy as np
from scipy import signal #bandpass filter
from edfreader import EDFreader #Read and Write of EDG data
from sklearn.cluster import KMeans #KMeans model
from tqdm.notebook import tqdm
from sklearn.metrics import confusion_matrix
import os
import pickle
from numpy import load

# To use file handler to get metris of the EDG file
def getFileMetrics(edg_hdl):
    sam_per_sec = edg_hdl.getSampleFrequency(0)           # num of samples/second
    file_dur = edg_hdl.getFileDuration()                  # units of 100 nanoSeconds
    sam_per_record = edg_hdl.getSampelsPerDataRecord(0)   # num of samples/data
    total_sam = edg_hdl.getTotalSamples(0)                # num of samples/signal
    num_records = edg_hdl.getNumDataRecords()
    return sam_per_sec, file_dur, sam_per_record, total_sam, num_records

# get the power of the wave in the range (minF, maxF)
def bandPower(f, Pxx, minF, maxF):
    ind_min = np.argmax(f>minF)
    ind_max = np.argmax(f>maxF)
    return np.trapz(Pxx[ind_min: ind_max], f[ind_min: ind_max])

# norm bool perform standardisation 
def getFeatures(edg_hdl, num_records, sam_per_record, sam_per_sec, num_signal = 6, norm = False):
    
    num_feat_per_signal = 16
    X = np.empty((num_records * num_signal, num_feat_per_signal))
    # set the file handler at the beginning of the signals
    for j in range(num_signal):    
        edg_hdl.fseek(j, 0, EDFreader.EDFSEEK_SET)

    buf = np.empty((num_signal, int(sam_per_record)))
    for i in range(num_records):
        # get all the signals
        for j in range(num_signal):
            edg_hdl.readSamples(j, buf[j], sam_per_record)
        buf_copy = buf.copy() # a copy of the buf used for average montage
        # get features from reference montage
        for j in range(num_signal):
            index = j*num_records + i
            # normalization if required
            if norm is True:
                mean = np.mean((buf[j]))
                std = np.std(buf[j])
                buf[j] = (buf[j] - mean)/std
            # feature extracting
            X[index][0] = np.mean(np.absolute(buf[j]))
            f, Pxx = signal.periodogram(buf[j], fs=sam_per_sec)
            X[index][1] = bandPower(f,Pxx,1,2)
            X[index][2] = bandPower(f,Pxx,3,4)
            X[index][3] = bandPower(f,Pxx,4,6)
            X[index][4] = bandPower(f,Pxx,6,9)
            X[index][5] = bandPower(f,Pxx,9,12)
            X[index][6] = bandPower(f,Pxx,12,30)
            X[index][7] = bandPower(f,Pxx,30,50)
        
        # calculate average montage
        buf = buf_copy
        avg = np.mean(buf, 0)
        buf -= avg
        # get features from average montage
        for j in range(num_signal):
            index = j*num_records + i
            # normalization if required
            if norm is True:
                mean = np.mean((buf[j]))
                std = np.std(buf[j])
                buf[j] = (buf[j] - mean)/std
            # feature extracting
            X[index][8] = np.mean(np.absolute(buf[j]))
            f, Pxx = signal.periodogram(buf[j], fs=sam_per_sec)
            X[index][9] = bandPower(f,Pxx,1,2)
            X[index][10] = bandPower(f,Pxx,3,4)
            X[index][11] = bandPower(f,Pxx,4,6)
            X[index][12] = bandPower(f,Pxx,6,9)
            X[index][13] = bandPower(f,Pxx,9,12)
            X[index][14] = bandPower(f,Pxx,12,30)
            X[index][15] = bandPower(f,Pxx,30,50)
            
    return X

# consolidate labels to 1 label for all channels 
# remove discrepencies in seizure events
# record the list of channels where seizure is happening
# return a DataFrame with this information
def createDataFrame(labels, num_signal, num_records):
    # reshape the labels from 1d to 2d
    labels = np.reshape(labels, (num_signal, num_records))
    d = {'onset':[], 'duration':[], 'label':[], 'list_of_channels':[]}

    onset = -1
    duration = -1
    label = "label_name_placeholder"
    set_of_channels = set()
    for i in range(num_records):
        # check if current second is seizure
        curr_set = set()
        for j in range(num_signal):
            if labels[i][j] == 1:
                curr_set.add(j)
        if len(curr_set) == 0: # current second is not seizure
            # if previous second is seizure, then check if next second is seizure
            if duration > 0 and i + 1 < num_records:
                for j in range(num_signal):
                    if labels[i+1][j] == 1:
                        curr_set.add(j)
                if len(curr_set) > 0: # next second is seizure
                    duration += 1
                    continue
            # if next second is not seizure and if previous second is seizure, then record this event
            if duration > 0:
                d['onset'].append(onset)
                onset = -1
                d['duration'].append(duration)
                duration = -1
                d['label'].append(label)
                d['list_of_channels'].append(list(set_of_channels))
                set_of_channels = set()
        else:
            # check if this is the first second
            if duration == -1:
                onset = i
                duration = 1
                set_of_channels = curr_set
            else:
                duration += 1
                set_of_channels.union(curr_set)
    # after iteration, check if there is an event at the end
    if duration > 0:
        d['onset'].append(onset)
        d['duration'].append(duration)
        d['label'].append(label)
        d['list_of_channels'].append(list(set_of_channels))

    # create the dataframe
    return pd.DataFrame(data=d)

# TODO
def generate_filename():
    return 'result.csv'

# this is the function called by the web app
# index_signal : the index of the first of signal in the file. Here assume all the signals are sequential 
def detect_seizure(edg_hdl, index_signal, num_signals = 6, model_filename = "KMean_model.sav", assignemnt_filename = "KMean_assignment.npy"):
    yield 'event: update\ndata: Process initiated\n\n'
    # get meta data of the signals
    sam_per_sec, file_dur, sam_per_record, total_sam, num_records = getFileMetrics(edg_hdl)
    # load the model
    model = pickle.load(open(model_filename, 'rb'))
    yield 'event: update\ndata: Model Loaded\n\n'
    # load the assignment
    pos_cluster_indices = (load(assignemnt_filename)).tolist()
    yield 'event: update\ndata: Assignment Loaded\n\n'
    # extract features
    X = getFeatures(edg_hdl, num_records, sam_per_record, sam_per_sec)
    yield 'event: update\ndata: Features extracted\n\n'
    # make prediction 
    predicted_raw_lables = model.predict(X) # (num_records * num_signals)
    # assign lables of seizures i.e. 1
    labels = np.zeros(num_records * num_signals)
    for i in range(num_records * num_signals):
        if predicted_raw_lables[i] in pos_cluster_indices:
            labels[i] = 1
    yield 'event: update\ndata: Labels assigned\n\n'
    # consolidate labels to 1 label for all channels 
    # remove discrepencies in seizure events
    # record the list of channels where seizure is happening
    # create a DataFrame with this information
    pd = createDataFrame(labels)
    result_filename = generate_filename()
    pd.to_csv(result_filename)
    yield 'event: close\ndata: Annotation file created\n\n'
    return pd, result_filename
