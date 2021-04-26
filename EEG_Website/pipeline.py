import pandas as pd
import numpy as np
from scipy import signal  # bandpass filter
from edfreader import EDFreader  # Read and Write of EDG data
from sklearn.cluster import KMeans  # KMeans model
from tqdm.notebook import tqdm
from sklearn.metrics import confusion_matrix
import os
import pickle
from numpy import load


# To use file handler to get metris of the EDG file
def getFileMetrics(edg_hdl):
    sam_per_sec = edg_hdl.getSampleFrequency(0)  # num of samples/second
    file_dur = edg_hdl.getFileDuration()  # units of 100 nanoSeconds
    sam_per_record = edg_hdl.getSampelsPerDataRecord(0)  # num of samples/data
    total_sam = edg_hdl.getTotalSamples(0)  # num of samples/signal
    num_records = edg_hdl.getNumDataRecords()
    return sam_per_sec, file_dur, sam_per_record, total_sam, num_records


# get the power of the wave in the range (minF, maxF)
def bandPower(f, Pxx, minF, maxF):
    ind_min = np.argmax(f > minF)
    ind_max = np.argmax(f > maxF)
    return np.trapz(Pxx[ind_min: ind_max], f[ind_min: ind_max])


# norm bool perform standardisation
def getFeatures(X, edg_hdl, num_records, sam_per_record, sam_per_sec, num_signal=6, norm=False):
    num_feat_per_signal = 16
    # X = np.empty((num_records * num_signal, num_feat_per_signal))
    # set the file handler at the beginning of the signals
    for j in range(num_signal):
        edg_hdl.fseek(j, 0, EDFreader.EDFSEEK_SET)


    buf = np.empty((num_signal, int(sam_per_record)))
    for i in range(num_records):
        if i % 5000 == 0:
            print(i, "features extracted")
            # yield 'event: update\ndata:' + str(i) + 'featured extracted\n\n'
        # get all the signals
        for j in range(num_signal):
            edg_hdl.readSamples(j, buf[j], sam_per_record)
        buf_copy = buf.copy()  # a copy of the buf used for average montage
        # get features from reference montage
        for j in range(num_signal):
            index = j * num_records + i
            # normalization if required
            if norm is True:
                mean = np.mean((buf[j]))
                std = np.std(buf[j])
                buf[j] = (buf[j] - mean) / std
            # feature extracting
            X[index][0] = np.mean(np.absolute(buf[j]))
            f, Pxx = signal.periodogram(buf[j], fs=sam_per_sec)
            X[index][1] = bandPower(f, Pxx, 1, 2)
            X[index][2] = bandPower(f, Pxx, 3, 4)
            X[index][3] = bandPower(f, Pxx, 4, 6)
            X[index][4] = bandPower(f, Pxx, 6, 9)
            X[index][5] = bandPower(f, Pxx, 9, 12)
            X[index][6] = bandPower(f, Pxx, 12, 30)
            X[index][7] = bandPower(f, Pxx, 30, 50)

        # calculate average montage
        buf = buf_copy
        avg = np.mean(buf, 0)
        buf -= avg
        # get features from average montage
        for j in range(num_signal):
            index = j * num_records + i
            # normalization if required
            if norm is True:
                mean = np.mean((buf[j]))
                std = np.std(buf[j])
                buf[j] = (buf[j] - mean) / std
            # feature extracting
            X[index][8] = np.mean(np.absolute(buf[j]))
            f, Pxx = signal.periodogram(buf[j], fs=sam_per_sec)
            X[index][9] = bandPower(f, Pxx, 1, 2)
            X[index][10] = bandPower(f, Pxx, 3, 4)
            X[index][11] = bandPower(f, Pxx, 4, 6)
            X[index][12] = bandPower(f, Pxx, 6, 9)
            X[index][13] = bandPower(f, Pxx, 9, 12)
            X[index][14] = bandPower(f, Pxx, 12, 30)
            X[index][15] = bandPower(f, Pxx, 30, 50)

    return X


# consolidate labels to 1 label for all channels
# remove discrepencies in seizure events
# record the list of channels where seizure is happening
# return a DataFrame with this information
def createDataFrame(labels, num_signal, num_records):
    d = {'Onset': [], 'Duration': [], 'Label': [], 'List_of_channels': []}
    onset = -1
    duration = -1
    label = "label_name_placeholder"
    set_of_channels = set()
    for i in range(num_records):
        # check if current second is seizure
        curr_set = set()
        for j in range(num_signal):
            if labels[j][i] == 1:
                curr_set.add(j)
        if len(curr_set) == 0:  # current second is not seizure
            # if previous second is seizure, then check if next second is seizure
            if duration > 0 and i + 1 < num_records:
                for j in range(num_signal):
                    if labels[j][i + 1] == 1:
                        curr_set.add(j)
                if len(curr_set) > 0:  # next second is seizure
                    duration += 1
                    continue
            # if next second is not seizure and if previous second is seizure, then record this event
            if duration > 0:
                d['Onset'].append(onset)
                onset = -1
                d['Duration'].append(duration)
                duration = -1
                d['Label'].append(label)
                d['List_of_channels'].append(list(set_of_channels))
                set_of_channels = set()
        else:
            # check if this is the first second
            if duration == -1:
                onset = i
                duration = 1
                set_of_channels = curr_set
            else:
                duration += 1
                set_of_channels = set_of_channels | curr_set
    # after iteration, check if there is an event at the end
    if duration > 0:
        d['Onset'].append(onset)
        d['Duration'].append(duration)
        d['Label'].append(label)
        d['List_of_channels'].append(list(set_of_channels))
    # create the dataframe
    return pd.DataFrame(data=d)


# TODO
# filename + index_signal
def generate_filename(filename, index_signal):
    filename = filename[:-4]
    return filename + "_" + str(index_signal) + ".csv"


# this is the function called by the web app
# index_signal : the index of the first of signal in the file. Here assume all the signals are sequential
def detect_seizure(filename, edg_hdl, index_signal, num_signal=6, model_filename="finalized_model.sav",
                   assignemnt_filename="data.npy"):
    print('in detecting siezures')
    yield 'event: update\ndata: Process initiated\n\n'
    # get meta data of the signals
    sam_per_sec, file_dur, sam_per_record, total_sam, num_records = getFileMetrics(edg_hdl)
    # load the model
    model = pickle.load(open(model_filename, 'rb'))
    print(model)
    yield 'event: update\ndata: Model Loaded\n\n'
    # load the assignment
    pos_cluster_indices = (load(assignemnt_filename)).tolist()
    print('Assignment loaded')
    yield 'event: update\ndata: Assignment Loaded\n\n'
    # extract features
    num_feat_per_signal = 16
    X = np.empty((num_records * num_signal, num_feat_per_signal))
    X = getFeatures(X, edg_hdl, num_records, sam_per_record, sam_per_sec)
    print(X)
    yield 'event: update\ndata: Features extracted\n\n'
    print('Features extracted')
    # make prediction
    predicted_raw_lables = model.predict(X)  # (num_records * num_signal)
    print('Labels predicted')
    # assign lables of seizures i.e. 1
    labels = np.zeros(num_records * num_signal)
    for i in range(num_records * num_signal):
        if predicted_raw_lables[i] in pos_cluster_indices:
            labels[i] = 1
    # reshape the labels from 1d to 2d
    labels = np.reshape(labels, (num_signal, num_records))
    # consolidate labels to 1 label for all channels
    # remove discrepencies in seizure events
    # record the list of channels where seizure is happening
    # create a DataFrame with this information
    df = createDataFrame(labels, num_signal, num_records)
    result_filename = generate_filename(filename, index_signal)
    df.to_csv(result_filename, index=False)
    yield 'event: close\ndata: Annotation file created\n\n'
    return df, result_filename

# test
# edg_file_path = './REP 12 13 SAH 2 1  2016-11-22 16H09M.rec'
# edg_hdl = EDFreader(edg_file_path)
# detect_seizure(edg_hdl, 0, 6, 'finalized_model.sav', 'data.npy')