
from flask import Flask, render_template, redirect, url_for, request, jsonify, after_this_request
from edfreader import EDFreader

filename = '' #reusable filename variable
app = Flask(__name__)
@app.route('/')
def hello_world():
   return render_template("index.html")



@app.route('/', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        eeg_file = request.files['eeg_file']
        global filename
        filename = '%s'%eeg_file.filename
        if filename != '':
            eeg_file.save(eeg_file.filename)
        return redirect(url_for('hello_world'))
    return render_template("index.html")

@app.route('/electrode_send', methods=['GET'])
def electrode_send():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    hdl = EDFreader(filename)
    n_elec = hdl.getNumSignals()
    e_dict = {}
    for i in range(0,n_elec):
        e_dict[i] = hdl.getSignalLabel(i)
    return jsonify(e_dict)


if __name__ == '__main__':
    app.run()