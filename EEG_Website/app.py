from flask import Flask, render_template, redirect, url_for, request, jsonify, after_this_request, session
import edf_manager
import annreader

filename = ''  # reusable filename variable
app = Flask(__name__)
app.config['SECRET_KEY'] = "CHANGE BEFORE DEPLOYMENT!!!!!"
duration_default = '1'
offset_default = '0'
amplitude_default = '200'


# HOME PAGE: NO FILE TO DISPLAY
@app.route('/')
def index():
    if session.get('filename') is None:
        return render_template('index.html')
    else:
        return render_template('index.html', filename=session['filename'])


# DELETE ALL SESSION ITEMS
@app.route('/delete', methods=['POST'])
def delete_session():
    while len(session):
        session.popitem()
    return redirect(url_for('index'))


# POST SELECTED DURATION
@app.route('/upload_duration', methods=['POST'])
def select_duration():
    # Set selected graph duration for session
    session['duration'] = request.form['duration']
    # Redirect user to current stage in flow: empty index; electrode select; or display graph
    if session.get('filename') is None:
        return redirect(url_for('index'))
    elif session.get('selected_id') is None:
        return redirect(url_for('index', electrodes=True, filename=session['filename']))
    else:
        return redirect(url_for('index', display=True, filename=session['filename']))


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
    # Set up session defaults for file
    session['duration'] = duration_default
    session['offset'] = offset_default
    session['amplitude'] = amplitude_default
    session['selected_id'] = []
    # Redirect to electrode select
    return redirect(url_for('index', electrodes=True, filename=session['filename']))


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
@app.route('/electrode_select', methods=['POST', 'GET'])
def selecting_electrodes():
    if request.method == 'POST':
        # Save selected ids for session
        session['selected_id'] = list(request.form.values())
        # Redirect user to index page, with url parameter to trigger graph displays
        return redirect(url_for('index', display=True, filename=session['filename']))
    elif request.method == 'GET':
        return edf_manager.get_selected_electrodes(session)


# GET SELECTED DATA
@app.route('/data', methods=['GET'])
def get_relevant_data():
    print(session['offset'])
    # Calculate offset according to delta argumet, offset and current offset
    new_offset = int(session['offset']) + (int(request.args.get('delta')) * int(session['duration']) * 1000)
    if new_offset > 0:
        session['offset'] = new_offset
    else:
        session['offset'] = offset_default
    return edf_manager.get_electrode_date(session)


# CHANGE AMPLITUDE
@app.route('/amplitude', methods=['GET'])
def change_amplitude():
    new_amplitude = int(session['amplitude']) + int(request.args.get('delta'))
    session['amplitude'] = new_amplitude if new_amplitude > 0 else amplitude_default
    return jsonify(amplitude=session['amplitude'])


# UPLOAD ANNOTATION FILE
@app.route('/upload_ann', methods=['POST'])
def upload_ann():
    ann_file = request.files['ann_file']  # update view in static
    if ann_file.filename != '':
        ann_file.save(ann_file.filename)
    else:
        return redirect(url_for('index'))
    # save annotation filename to session
    session['annotation_file'] = ann_file.filename

    # fix to add if else statements for display, electrodes, filename
    return redirect(url_for('index', annotations=True))


@app.route('/ann_data', methods=["GET"])
def ann_data():
    return annreader.get_annotations(session)


@app.route('/slider', methods=['GET'])
def get_time():
    return edf_manager.get_time_data(session)


@app.route('/select-offset', methods=['POST'])
def set_time_data():
    session['offset'] = request.form['new_value']
    print(request.form['new_value'])
    print(session['offset'])
    return session['offset']


if __name__ == '__main__':
    app.run()
