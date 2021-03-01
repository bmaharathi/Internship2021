from flask import Flask, render_template, redirect, url_for, request, jsonify, after_this_request, session
import edf_manager

filename = ''  # reusable filename variable
app = Flask(__name__)
app.config['SECRET_KEY'] = "CHANGE BEFORE DEPLOYMENT!!!!!"


# HOME PAGE: NO FILE TO DISPLAY
@app.route('/')
def index():
    return render_template('index.html')


# POST SELECTED DURATION
@app.route('/upload_duration', methods=['POST'])
def select_duration():
    # Set selected graph duration for session
    session['duration'] = request.form['duration']
    # Redirect user to current stage in flow: empty index; electrode select; or display graph
    if session.get('filename') is None:
        return redirect(url_for('index'))
    elif session.get('selected_id') is None:
        return redirect(url_for('index', electrodes=True))
    else:
        return redirect(url_for('index', display=True))


# POST EEG FILE
@app.route('/upload_eeg', methods=['POST'])
def upload_file():
    # Save file to server directory
    eeg_file = request.files['eeg_file']
    if eeg_file.filename != '':
        eeg_file.save(eeg_file.filename)
    else:
        return redirect(url_for('index'))
    # Save file path for session
    session['filename'] = eeg_file.filename
    # Redirect to electrode select
    return redirect(url_for('index', electrodes=True))


# GET ELECTRODES TO CHOOSE FROM
@app.route('/electrode_get', methods=['GET'])
def electrode_send():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # Return edf electrodes by name and index in JSON
    return edf_manager.get_electrodes(session)


# POST SELECTED ELECTRODES
@app.route('/electrode_select', methods=['POST'])
def selecting_electrodes():
    # Save selected ids for session
    session['selected_id'] = list(request.form.values())
    # Redirect user to index page, with url parameter to trigger graph displays
    return redirect(url_for('index', display=True))


# GET SELECTED DATA
@app.route('/data', methods=['GET'])
def get_relevant_data():
    # If duration not set -> set to 1 (second) by default
    if session.get('duration') is None:
        session['duration'] = '1'
    # If offset not set -> set to 0 by default
    if session.get('offset') is None:
        session['offset'] = '0'
    # Else calculate new offset utilizing url argument delta converted to milliseconds
    else:
        session['offset'] = int(session['offset']) + (int(request.args.get('delta')) * int(session['duration']) * 1000)
    data = edf_manager.get_electrode_date(session)
    return data


if __name__ == '__main__':
    app.run()
