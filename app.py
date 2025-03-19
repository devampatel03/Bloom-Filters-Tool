from flask import Flask, render_template, request
import pandas as pd
from record_linkage import match_records_parallel

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file1' not in request.files or 'file2' not in request.files:
        return "Please upload both files!", 400

    file1 = request.files['file1']
    file2 = request.files['file2']

    df1 = pd.read_csv(file1)  # Read uploaded file as DataFrame
    df2 = pd.read_csv(file2)

    matches = match_records_parallel(df1, df2)  # Perform record linkage

    return render_template('results.html', matches=matches)

if __name__ == '__main__':
    app.run(debug=True)
