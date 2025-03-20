from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from io import StringIO
import csv

from record_linkage import match_records

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

    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
    except Exception as e:
        return f"Error reading CSV files: {e}", 400

    matches = match_records(df1, df2)
    
    # Also prepare data for visualization: distribution of Hamming distances
    hamming_values = [m[2] for m in matches]
    jaccard_values = [m[3] for m in matches]
    
    return render_template('results.html', matches=matches,
                           hamming_values=hamming_values, jaccard_values=jaccard_values)

@app.route('/api/matches', methods=['POST'])
def api_matches():
    # API endpoint for programmatic access
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Both files required'}), 400

    file1 = request.files['file1']
    file2 = request.files['file2']

    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
    except Exception as e:
        return jsonify({'error': f"CSV read error: {e}"}), 400

    matches = match_records(df1, df2)
    return jsonify({'matches': matches})

@app.route('/download', methods=['POST'])
def download():
    # Provide a CSV file download of matching results
    file1 = request.files['file1']
    file2 = request.files['file2']

    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
    except Exception as e:
        return f"Error reading CSV files: {e}", 400

    matches = match_records(df1, df2)
    
    # Create CSV content in memory
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Dataset1_ID', 'Dataset2_ID', 'Hamming_Distance', 'Jaccard_Similarity'])
    writer.writerows(matches)
    output = si.getvalue()
    
    return send_file(StringIO(output), mimetype='text/csv', as_attachment=True,
                     attachment_filename='matches.csv')

if __name__ == '__main__':
    app.run(debug=True)
