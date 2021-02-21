from edfreader import EDFreader
from flask import jsonify


# PARSE AVAILABLE ELECTRODES AND RETURN DICTIONARY => INDEX : ELECTRODE NAME
def get_electrodes(file):
    hdl = EDFreader(file)
    n_elec = hdl.getNumSignals()
    e_dict = {}
    for i in range(0, n_elec):
        e_dict[i] = hdl.getSignalLabel(i)
    return jsonify(amount=len(e_dict.keys()),
                   values=e_dict)


