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
        print(len(buf))

    # Get time labels
    start_time = hdl.getStartDateTime() + timedelta(milliseconds=offset)
    times = []
    for i in range(offset, offset + N + 1):
        time = str((start_time + timedelta(milliseconds=i)).time())
        times.append(time[:-7] if len(time) > 8 else time)

    # Increment offset by samples read
    new_offset = offset + N - 1
    # Number of seconds for gridlines
    ticks = int(session['duration']) + 1
    print(len(times))

    return jsonify(time=times,
                   data=data,
                   offset=new_offset,
                   ticks=ticks)
