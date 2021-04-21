from edfreader import EDFreader
from flask import jsonify
import numpy as np
from datetime import datetime, timedelta
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
    if session['filter'] == '':
        session['filter'] = hdl.getSampleFrequency(0)

    # Reverse list of channels to appear in ascending order in chart later
    channels = session['selected_id'].copy()
    channels.reverse()
    # Get filter rate
    filter_rate = int(N / int(session['filter']))
    print("filter_rate:", filter_rate)

    data = []
    # for each chosen channel
    for count, s_id in enumerate(channels):
        # get signal id
        s_id = int(s_id)
        # If data requested is buffered
        if data_is_buffered:
            # Utilize Data_Handler
            # Load specified data (where rows are channels and columns are recorded
            buf = data_handler.data[s_id, offset: offset + N: filter_rate]
            map_val = int(session['data_offset'])
            # Add data to list, while also flipping data and mapping it to owns area for chart js
            data.append([hdl.getSignalLabel(s_id), list(map(lambda val: val * -1 + count * map_val, buf))])
        else:
            # Utilize edf_reader
            # set off set for sample
            hdl.fseek(s_id, offset, EDFreader.EDFSEEK_SET)
            # Get chart mping
            map_val = count * int(session['data_offset'])
            # read N samples for signal
            data_read = hdl.readSamples_IBRAIN(s_id, N, map_val, filter_rate)
            # Add data to list
            data.append([hdl.getSignalLabel(s_id), data_read])

    # Get time labels
    start_time = hdl.getStartDateTime()
    times = [str((start_time + timedelta(milliseconds=i)).time()) for i in range(offset, offset + N + 1, filter_rate)]
    times[0] = times[0][:-7] if len(times[0]) > 8 else times[0]
    times[-1] = times[-1][:-7] if len(times[-1]) > 8 else times[-1]

    # Increment offset by samples read
    new_offset = offset + N - 1
    map_val = int(session['data_offset'])
    return jsonify(time=times,
                   data=data,
                   sliderval=offset,
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
