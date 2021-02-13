# from flask import Flask, render_template
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def hello_world():
#     return render_template("index.html")

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/')
def upload_file():
    return render_template('index.html')


@app.route('/uploader', methods=['GET', 'POST'])
def openEEGFILE():
    if request.method == 'POST':
        f = request.files['eeg_file_form']
        f.save(secure_filename(f.filename))
        return 'file uploaded successfully'

if __name__ == '__main__':
    app.run()