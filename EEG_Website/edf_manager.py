from edfreader import EDFreader
from flask import jsonify
import numpy as np
from datetime import datetime, timedelta


# session dict keys :-
# filename
# selected_count
# selected_id
# offset
# duration
# data_offset
# amplitude


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
    start_time = hdl.getStartDateTime() + timedelta(milliseconds=offset)
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


