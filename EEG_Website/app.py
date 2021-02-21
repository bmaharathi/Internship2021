from flask import Flask, render_template, redirect, url_for, request, jsonify, after_this_request, session
import edf_manager

filename = ''  # reusable filename variable
app = Flask(__name__)
app.config['SECRET_KEY'] = "CHANGE BEFORE DEPLOYMENT!!!!!"


# HOME PAGE: NO FILE TO DISPLAY
@app.route('/')
def index():
    return render_template('index.html')


# POST EEG FILE
@app.route('/upload_eeg', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        eeg_file = request.files['eeg_file']
        if eeg_file.filename != '':
            eeg_file.save(eeg_file.filename)
        else:
            return redirect(url_for('index'))

        session['filename'] = eeg_file.filename
        return redirect(url_for('index', electrodes=True))


# GET ELECTRODES TO CHOOSE FROM
@app.route('/electrode_get', methods=['GET'])
def electrode_send():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    return edf_manager.get_electrodes((session['filename']))


# POST SELECTED ELECTRODES
@app.route('/electrode_select', methods=['POST'])
def selecting_electrodes():
    selected = []
    for id in request.form.keys():
        selected.append(id)
    for id in request.args.items():
        selected.append(id)
    print( list(request.form.keys()),app.logger)
    return jsonify(selected)


if __name__ == '__main__':
    app.run()
