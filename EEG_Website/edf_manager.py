from edfreader import EDFreader
from flask import jsonify
import numpy as np
from datetime import datetime, timedelta
import threading
import sys


# GET DATA
def get_data(session, data_handler):
    if int(session['offset']) < data_handler.records_loaded:
        print("using data_handler")
        offset = int(session['offset'])
        N = int(session['duration']) * 1000 + 1

        data = []

        if session['selected_count'] == '0':
            session['selected_id'] = list(map(str, range(0, data_handler.num_channels)))
            session['selected_count'] = data_handler.num_channels()

        channels = session['selected_id']
        channels.reverse()
        # for each signal in edf file
        for count, s_id in enumerate(channels):
            s_id = int(s_id)
            buf = data_handler.data[s_id, offset: offset + N]
            map_val = int(session['data_offset'])
            # Add data to list
            data.append([data_handler.edf_reader.getSignalLabel(s_id), list(map(lambda val: val * -1 + count * map_val, buf))])

        # Get time labels
        start_time = data_handler.record_start
        times = [str((start_time + timedelta(milliseconds=i)).time()) for i in range(offset, offset + N + 1)]
        times[0] = times[0][:-7] if len(times[0]) > 8 else times[0]
        times[-1] = times[-1][:-7] if len(times[-1]) > 8 else times[-1]

        # Increment offset by samples read
        new_offset = offset + N - 1
        amplitude = session['amplitude']
        map_val = int(session['data_offset'])
        return jsonify(time=times,
                       data=data,
                       sliderval=offset,
                       offset=new_offset,
                       dataOffset=map_val,
                       duration=session['duration'])
    else:
        return get_electrode_data(session)


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


def get_electrode_date(session):
    hdl = EDFreader(session['filename'])
    # Convert seconds to milliseconds
    offset = int(session['offset'])
    N = int(session['duration']) * 1000 + 1

    data = []

    if session['selected_count'] == '0':
        session['selected_id'] = list(map(str, range(0, hdl.getNumSignals())))
        session['selected_count'] = hdl.getNumSignals()

    # for each signal in edf file
    for count, s_id in enumerate(session['selected_id']):
        signal = int(s_id)
        # buffer to hold samples for single signal
        buf = np.zeros(N)
        # set off set for sample
        hdl.fseek(signal, offset, EDFreader.EDFSEEK_SET)
        # read N samples for signal
        hdl.readSamples(signal, buf, N)
        # invert data
        buf = buf * (-1)
        map_val = int(session['data_offset'])
        # Add data to list
        data.append([hdl.getSignalLabel(signal), list(map(lambda val: val + count * map_val, buf))])

    # Get time labels
    start_time = hdl.getStartDateTime()
    times = [str((start_time + timedelta(milliseconds=i)).time()) for i in range(offset, offset + N + 1)]
    times[0] = times[0][:-7] if len(times[0]) > 8 else times[0]
    times[-1] = times[-1][:-7] if len(times[-1]) > 8 else times[-1]

    # Increment offset by samples read
    new_offset = offset + N - 1
    amplitude = session['amplitude']
    map_val = int(session['data_offset'])
    return jsonify(time=times,
                   data=data,
                   sliderval=offset,
                   offset=new_offset,
                   dataOffset=map_val,
                   duration=session['duration'])


def get_electrode_data(session):
    hdl = EDFreader(session['filename'])
    # Convert seconds to milliseconds
    offset = int(session['offset'])
    N = int(session['duration']) * 1000 + 1

    data = []

    if session['selected_count'] == '0':
        session['selected_id'] = list(map(str, range(0, hdl.getNumSignals())))
        session['selected_count'] = hdl.getNumSignals()

    channels = session['selected_id']
    channels.reverse()
    # for each signal in edf file
    for count, s_id in enumerate(channels):
        signal = int(s_id)
        # set off set for sample
        hdl.fseek(signal, offset, EDFreader.EDFSEEK_SET)
        # Get chart mping
        map_val = count * int(session['data_offset'])
        # read N samples for signal
        data_read = hdl.readSamples_IBRAIN(signal, N, map_val)
        # Add data to list
        data.append([hdl.getSignalLabel(signal), data_read])

    # Get time labels
    start_time = hdl.getStartDateTime()
    times = [str((start_time + timedelta(milliseconds=i)).time()) for i in range(offset, offset + N + 1)]
    times[0] = times[0][:-7] if len(times[0]) > 8 else times[0]
    times[-1] = times[-1][:-7] if len(times[-1]) > 8 else times[-1]

    # Increment offset by samples read
    new_offset = offset + N - 1
    amplitude = session['amplitude']
    map_val = int(session['data_offset'])
    return jsonify(time=times,
                   data=data,
                   sliderval=offset,
                   offset=new_offset,
                   dataOffset=map_val,
                   duration=session['duration'])


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

    def __init__(self):
        self.f_name = ""
        self.edf_reader = None
        self.records_loaded = 0
        self.num_channels = 0
        self.data = None
        self.record_start = None

    def start(self, session):
        self.f_name = session['filename']
        self.edf_reader = EDFreader(self.f_name)
        self.records_loaded = 0
        self.num_channels = self.edf_reader.getNumSignals()
        self.data = None
        self.record_start = self.edf_reader.getStartDateTime()
        self.regulate_buffering()

    def regulate_buffering(self):
        num_records = int(self.edf_reader.getFileDuration() / 10000)
        num_channels = self.num_channels
        self.data = np.zeros((num_channels, num_records))

        data_per_epoch = 10000

        for record_start in range(0, num_records, data_per_epoch):
            self.records_loaded += self.load_data(record_start, data_per_epoch)
            if self.records_loaded % (data_per_epoch * 100) == 0:
                print("Loaded %d records" % self.records_loaded, flush=True)
                print("==>", self.data[:, record_start], flush=True)
                sys.stdout.flush()

    def load_data(self, record_start, N):
        for signal in range(0, self.edf_reader.getNumSignals()):
            buf = self.data[signal, record_start: record_start + N]
            self.edf_reader.readSamples(signal, buf, N)
        return N
