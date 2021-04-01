from edfreader import EDFreader
from flask import jsonify
import numpy as np
from datetime import datetime, timedelta


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
    if len(session['selected_id']) == 0:
        session['selected_id'] = list(map(str, range(1, hdl.getNumSignals())))
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

    data = {}

    if len(session['selected_id']) == 0:
        session['selected_id'] = list(map(str, range(1, hdl.getNumSignals())))

    # for each signal in edf file
    for s_id in session['selected_id']:
        signal = int(s_id)
        # buffer to hold samples for single signal
        buf = np.zeros(N)
        # set off set for sample
        hdl.fseek(signal, offset, EDFreader.EDFSEEK_SET)
        # read N samples for signal
        hdl.readSamples(signal, buf, N)
        # invert data
        buf = buf * (-1)
        # Add data to list
        data[hdl.getSignalLabel(signal)] = list(buf)

    # Get time labels
    start_time = hdl.getStartDateTime() + timedelta(milliseconds=offset)
    times = [str((start_time + timedelta(milliseconds=i)).time()) for i in range(offset, offset + N + 1)]
    times[0] = times[0][:-7] if len(times[0]) > 8 else times[0]
    times[-1] = times[-1][:-7] if len(times[-1]) > 8 else times[-1]

    # Increment offset by samples read
    new_offset = offset + N - 1
    amplitude = session['amplitude']

    return jsonify(time=times,
                   data=data,
                   offset=new_offset,
                   amplitude=amplitude)


def get_file_start(session):
    hdl = EDFreader(session['filename'])
    return hdl.getStartDateTime()


def get_time_data(session):
    hdl = EDFreader(session['filename'])
    end = hdl.getFileDuration() / 10000
    start_time = str(hdl.getStartDateTime().time()).split(':')
    return jsonify(min=0,
                   max=end,
                   start=start_time)
