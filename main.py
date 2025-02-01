from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Import CORS
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
df = None  # Global dataframe to hold uploaded data

@app.route('/upload', methods=['POST'])
def upload_file():
    global df
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    df = pd.read_csv(file_path)
    
    return jsonify({"message": "File uploaded successfully", "filename": file.filename})

@app.route('/data', methods=['GET'])
def get_data():
    global df
    if df is None:
        return jsonify({"error": "No data available. Upload a CSV first."}), 400
    return jsonify(df.to_dict(orient='records'))

@app.route('/visualization', methods=['GET'])
def get_visualization():
    global df
    if df is None:
        return jsonify({"error": "No data available. Upload a CSV first."}), 400

    factor = request.args.get('factor')
    if factor not in ['air_quality', 'water_quality', 'pollution']:
        return jsonify({"error": "Invalid factor. Choose from air_quality, water_quality, pollution."}), 400

    # Generate visualization
    plt.figure(figsize=(8, 5))
    plt.hist(df[factor], bins=20, color='skyblue', edgecolor='black')
    plt.xlabel(factor.replace('_', ' ').title())
    plt.ylabel("Frequency")
    plt.title(f"Distribution of {factor.replace('_', ' ').title()}")

    image_path = os.path.join(UPLOAD_FOLDER, f"{factor}_plot.png")
    plt.savefig(image_path)
    plt.close()

    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
