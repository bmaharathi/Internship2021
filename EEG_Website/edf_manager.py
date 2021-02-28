from edfreader import EDFreader
from flask import jsonify, session
import numpy as np


# PARSE AVAILABLE ELECTRODES AND RETURN DICTIONARY => INDEX : ELECTRODE NAME
def get_electrodes(session):
    hdl = EDFreader(session['filename'])
    n_elec = hdl.getNumSignals()
    e_dict = {}
    for i in range(0, n_elec):
        e_dict[i] = hdl.getSignalLabel(i)
    return jsonify(amount=len(e_dict.keys()),
                   values=e_dict)


def get_electrode_date(session):
    hdl = EDFreader(session['filename'])
    # Convert seconds to milliseconds

    if not session.get('duration') is None:
        N = int(session['duration']) * 1000
    else:
        N = 10 * 1000
    print(N)

    data = {}
    # for each signal in edf file
    for s_id in session['selected_id']:
        signal = int(s_id)
        # buffer to hold samples for single signal
        buf = np.zeros(N)
        # read N samples for signal
        hdl.readSamples(signal, buf, N)
        # invert data
        buf = buf * (-1)
        # Add data to list
        data[hdl.getSignalLabel(signal)] = list(buf)

    return jsonify(time=list(range(0, N)),
                   data=data)
