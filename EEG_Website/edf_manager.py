from edfreader import EDFreader
from flask import jsonify
import numpy as np
from datetime import datetime, timedelta
from scipy import signal
import threading
import sys


# GET DATA
def get_data(session, data_handler):
    # Check if data is buffered by seeing if records asked for is within records loaded
    data_is_buffered = (int(session['offset']) + int(session['duration']) * 1000) < data_handler.records_loaded
    # Configure EDFReader for either style of data retrieval
    if not data_is_buffered:
        hdl = EDFreader(session['filename'])
    else:
        hdl = data_handler.edf_reader
    # Declare the area of data the user is requesting
    offset = int(session['offset'])
    N = int(session['duration']) * 1000 + 1

    # Ask for all channels if user hasn't specificed which channels to look for
    if session['selected_count'] == '0':
        session['selected_id'] = list(map(str, range(0, hdl.getNumSignals())))
        session['selected_count'] = hdl.getNumSignals()

    # Reverse list of channels to appear in ascending order in chart later
    channels = session['selected_id'].copy()
    channels.reverse()
    # Get filter bounds
    frequency = hdl.getSampleFrequency(0)
    max_bound = frequency / 2
    filter_lower = float(session['filter-lower'])
    filter_lower = filter_lower if filter_lower < max_bound else -1
    filter_upper = float(session['filter-upper'])
    filter_upper = filter_upper if filter_upper < max_bound else -1

    data = []
    # for each chosen channel
    for count, s_id in enumerate(channels):
        # get signal id
        s_id = int(s_id)
        # If data requested is buffered
        if data_is_buffered:
            # Utilize Data_Handler
            # Load specified data (where rows are channels and columns are recorded
            buf = data_handler.data[s_id, offset: offset + N]
            # Get filtered data
            filtered_buf = applyBandpassFilter(buf, filter_lower, filter_upper, 1000)

            map_val = int(session['data_offset'])
            # Add data to list, while also flipping data and mapping it to owns area for chart js
            data.append([hdl.getSignalLabel(s_id), list(map(lambda val: val * -1 + count * map_val, filtered_buf))])
        else:
            # Utilize edf_reader
            # set off set for sample
            hdl.fseek(s_id, offset, EDFreader.EDFSEEK_SET)
            # Get chart mping
            map_val = int(session['data_offset'])
            # read N samples for signal
            buf = np.empty(N)
            hdl.readSamples(s_id, buf, N)
            # Get filtered data
            filtered_buf = applyBandpassFilter(buf, filter_lower, filter_upper, 1000)

            # Add data to list
            data.append([hdl.getSignalLabel(s_id), list(map(lambda val: val * -1 + count * map_val, filtered_buf))])

    # Get time labels
    start_time = hdl.getStartDateTime()
    times = [str((start_time + timedelta(milliseconds=i)).time()) for i in range(offset, offset + N + 1)]
    times[0] = times[0][:-7] if len(times[0]) > 8 else times[0]
    times[-1] = times[-1][:-7] if len(times[-1]) > 8 else times[-1]

    # Increment offset by samples read
    new_offset = offset + N - 1
    map_val = int(session['data_offset'])
    amplitude = ''.join([str(session['amplitude']), '/-', str(session['amplitude'])])
    print('freq:', frequency)

    update_vals = {'sliderval': offset, 'duration': session['duration'], 'upper': filter_upper,
                   'lower': filter_lower, 'frequency': frequency, 'amplitude': amplitude
                   }
    return jsonify(time=times,
                   data=data,
                   update=update_vals,
                   offset=new_offset,
                   dataOffset=map_val,
                   duration=session['duration'])


def get_average(session, data_handler):
    # Check if data is buffered by seeing if records asked for is within records loaded
    data_is_buffered = (int(session['offset']) + int(session['duration']) * 1000) < data_handler.records_loaded
    # Configure EDFReader for either style of data retrieval
    if not data_is_buffered:
        hdl = EDFreader(session['filename'])
    else:
        hdl = data_handler.edf_reader
    # Declare the area of data the user is requesting
    offset = int(session['offset'])
    N = int(session['duration']) * 1000 + 1
    numLabels = hdl.getNumSignals()
    # Ask for all channels if user hasn't specificed which channels to look for
    if session['selected_count'] == '0':
        session['selected_id'] = list(map(str, range(0, hdl.getNumSignals())))
        session['selected_count'] = hdl.getNumSignals()

    # Reverse list of channels to appear in ascending order in chart later
    channels = session['selected_id'].copy()
    channels.reverse()
    # Get filter bounds
    frequency = hdl.getSampleFrequency(0)
    max_bound = frequency / 2
    filter_lower = float(session['filter-lower'])
    filter_lower = filter_lower if filter_lower < max_bound else -1
    filter_upper = float(session['filter-upper'])
    filter_upper = filter_upper if filter_upper < max_bound else -1

    data = []
    # for each chosen channel
    for count, s_id in enumerate(channels):
        # get signal id
        s_id = int(s_id)
        # If data requested is buffered
        if data_is_buffered:
            # Utilize Data_Handler
            # Load specified data (where rows are channels and columns are recorded
            buf = data_handler.data[s_id, offset: offset + N]
            # Get filtered data
            filtered_buf = applyBandpassFilter(buf, filter_lower, filter_upper, 1000)

            map_val = int(session['data_offset'])
            # Add data to list, while also flipping data and mapping it to owns area for chart js
            data.append(list(filtered_buf))
        else:
            # Utilize edf_reader
            # set off set for sample
            hdl.fseek(s_id, offset, EDFreader.EDFSEEK_SET)
            # Get chart mping
            map_val = int(session['data_offset'])
            # read N samples for signal
            buf = np.empty(N)
            hdl.readSamples(s_id, buf, N)
            # Get filtered data
            filtered_buf = applyBandpassFilter(buf, filter_lower, filter_upper, 1000)

            # Add data to list
            data.append(list(filtered_buf))

    start_time = hdl.getStartDateTime()
    times = [str((start_time + timedelta(milliseconds=i)).time()) for i in range(offset, offset + N + 1)]
    times[0] = times[0][:-7] if len(times[0]) > 8 else times[0]
    times[-1] = times[-1][:-7] if len(times[-1]) > 8 else times[-1]

    # Increment offset by samples read
    new_offset = offset + N - 1
    map_val = int(session['data_offset'])
    amplitude = ''.join([str(session['amplitude']), '/-', str(session['amplitude'])])
    print('freq:', frequency)

    update_vals = {'sliderval': offset, 'duration': session['duration'], 'upper': filter_upper,
                   'lower': filter_lower, 'frequency': frequency, 'amplitude': amplitude
                   }
    # calculate means
    means = [None] * (
            int(session['duration']) * 1000 + 1)
    for i in range(int(session['duration']) * 1000 + 1):
        sum = 0.0
        for j in range(len(channels)):
            sum += float(data[j][i])
        mean = sum // int(len(channels))  # int for simplicity, change to float for accuracy
        means[i] = mean

    # data - data - refMeans
    for i in range(int(session['duration']) * 1000 + 1):
        for j in range(len(channels)):
            data[j][i] = data[j][i] - means[i]

    avg = []
    for count, s_id in enumerate(channels):
        # print(type(s_id))
        avg.append([hdl.getSignalLabel(int(s_id)), list(map(lambda val: val * -1 + count * map_val, data[count]))])

    return jsonify(time=times,
                   data=avg,
                   update=update_vals,
                   offset=new_offset,
                   dataOffset=map_val,
                   duration=session['duration'])


# PARSE AVAILABLE ELECTRODES AND RETURN DICTIONARY => INDEX : ELECTRODE NAME
def get_electrodes(session):
    hdl = EDFreader(session['filename'])
    n_elec = hdl.getNumSignals()
    e_dict = {}
    for i in range(0, n_elec):
        e_dict[i] = hdl.getSignalLabel(i)
    return jsonify(amount=len(e_dict.keys()),
                   values=e_dict)


# GET SELECT ELECTRODE NAMES
def get_selected_electrodes(session):
    hdl = EDFreader(session['filename'])
    selected = []
    if session['selected_count'] == '0':
        session['selected_id'] = list(map(str, range(0, hdl.getNumSignals())))
    # for each signal in edf file
    for s_id in session['selected_id']:
        signal = int(s_id)
        selected.append(hdl.getSignalLabel(signal))

    return jsonify(data=selected)


def get_file_start(session):
    hdl = EDFreader(session['filename'])
    return hdl.getStartDateTime()


def get_time_data(session):
    hdl = EDFreader(session['filename'])
    end = hdl.getFileDuration() / 10000
    start_time = str(hdl.getStartDateTime().time()).split(':')
    start_time.append(session['offset'])
    return jsonify(min=0,
                   max=end,
                   start=start_time)


def get_amplitude(session):
    new_max = len(list(session['selected_id'])) * int(session['data_offset'])
    new_min = -1 * int(session['data_offset'])
    return jsonify(amplitude=session['data_offset'],
                   newMax=new_max,
                   newMin=new_min)


def get_references(session):
    hdl = EDFreader(session['filename'])
    references = [{'label': hdl.getSignalLabel(i).strip()[-4:], 'id': i} for i in range(0, hdl.getNumSignals(), 6)]
    print(references)
    return jsonify(references=references)


class DataHandler:

    # Constructor feel free to add attributes as needed
    def __init__(self):
        self.f_name = ""
        self.edf_reader = None
        self.records_loaded = 0
        self.num_channels = 0
        self.data = None
        self.record_start = None
        self.status = False

    # Initialize attributes based on session
    def start(self, session):
        self.f_name = session['filename']
        self.edf_reader = EDFreader(self.f_name)
        self.records_loaded = 0
        self.num_channels = self.edf_reader.getNumSignals()
        self.data = None
        self.record_start = self.edf_reader.getStartDateTime()
        self.status = True
        self.regulate_buffering()

    # Sorry for all the functions, easier to keep straight but this one just gets more information, and monitors the
    # buffering process
    def regulate_buffering(self):
        # Maximum number of records available in the file
        num_records = int(self.edf_reader.getFileDuration() / 10000)
        # Number of channels
        num_channels = self.num_channels
        # NP array (channels x records)
        self.data = np.zeros((num_channels, num_records))

        # How many records to load before update handler
        data_per_epoch = 10000

        for record_start in range(0, num_records, data_per_epoch):
            # Update records loaded
            self.records_loaded += self.load_data(record_start, data_per_epoch)

            if self.records_loaded % (data_per_epoch * 100) == 0:
                print("Loaded %d records" % self.records_loaded, flush=True)
                print("==>", self.data[:, record_start], flush=True)

    # Utilize edf reader to load data
    def load_data(self, record_start, N):
        for signal in range(0, self.edf_reader.getNumSignals()):
            # get buffer for current epoch
            buf = self.data[signal, record_start: record_start + N]
            # Load data
            self.edf_reader.readSamples(signal, buf, N)
        # Return values loaded
        return N


def applyBandpassFilter(x, l_bound, u_bound, samp_rate, order=2):
    if l_bound < 0 or u_bound < 0:
        return x
    sos = signal.butter(order, [2 * l_bound / samp_rate, 2 * u_bound / samp_rate], "bandpass", False, "sos")
    filtered_x = signal.sosfilt(sos, x)
    return filtered_x
