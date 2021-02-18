
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
@app.route('/')
def hello_world():
   return render_template("index.html")



@app.route('/', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        eeg_file = request.files['eeg_file']
        if eeg_file.filename != '':
            eeg_file.save(eeg_file.filename)
        return redirect(url_for('hello_world'))
    return render_template("index.html")

if __name__ == '__main__':
    app.run()
