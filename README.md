# EEG Reviewer

## About the project
EEG Reviewer is a one-of-a-kind web-based EEG analysis tool which uses machine learning tools to mark significant and seizure events in a given subject. 

## Tools and libraries used

 1. [Flask](https://flask.palletsprojects.com/en/2.0.x/)
 2. [EDFlib - Python](https://gitlab.com/Teuniz/EDFlib-Python)
 3. [ChartJS](https://www.chartjs.org/)
 4. [Sci-Kit Learn](https://scikit-learn.org/stable/)
 5. [SciPy](https://www.scipy.org/)
 6. Pandas
 7. NumPy
## Getting Started
### Prerequisites
This app requires Flask to be set up on the user device. To set up Flask, follow this [installation guide](https://flask.palletsprojects.com/en/1.1.x/installation/#python-version).
Furthermore, the numpy, pandas, sklearn and scipy libraries should also be installed. Use the following commands to install thee libraries:-

    pip3 install -U scikit-learn
    pip3 install pandas numpy scipy tqdm

## Usage
To run the Flask app, go to the directory that stores the EEG Reviewer,

    cd ~/EEG
   and run this command to set the app file,
   

    export FLASK_APP=app.py
   and run this command to execute the Flask app,
   

    python -m flask run
   The output should look something like this:-
   

    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
   Open a web browser, copy and paste the host link (in this example, it is 127.0.0.1:5000) in the URL bar to run the server.

## Tools within the App
## Contributors
