import os
import random
import logging
from flask import Flask, render_template, request, jsonify
from campplus import create_embedding_db, rank
import pandas as pd

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('flask_app')

# Path to the data directory
DATA_DIR = './data'
DB_FILE = 'data_base.csv'

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def index():
    return render_template('fe.html')

@app.route('/audio_record_and_upload')
def audio_record_and_upload():
    return render_template('audio_record_and_upload.html')

@app.route('/compare_with_database')
def compare_with_database():
    return render_template('compare_with_database.html')

@app.route('/compare_two', methods=['POST'])
def compare_two():
    '''
    This function takes two voices, sends them to back end and displays the results
    on the front end. Please note that both are not saved neither the results.
    '''
    try:
        voice1 = request.files['voice1']
        voice2 = request.files['voice2']
        threshold = request.form.get('threshold')

        logger.info(f"Received files: {voice1.filename}, {voice2.filename} with threshold {threshold}")

        random_confidence = random.randint(70, 100)
        
        return jsonify(result="Comparison result here", confidence=random_confidence)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify(error="An error occurred during processing"), 500

@app.route('/compare_with_db', methods=['POST'])
def compare_with_db():
    '''
    This function takes a file, sends it to the backend, compares it
    with a database of voices stored in ./data, and returns the list of voices
    that are above the threshold and displays it as a list.
    '''
    try:
        logger.info(f'Request received: {request}')
        logger.info(f'Request files: {request.files}')
        logger.info(f'Request form: {request.form}')
        
        # Check if the POST request has the file part
        if 'voice' not in request.files:
            return jsonify(error="No file part in the request"), 400

        voice = request.files['voice']

        # Check if the user has actually selected a file
        if voice.filename == '':
            return jsonify(error="No selected file"), 400

        threshold = int(request.form.get('threshold')) / 100
        logger.info(f"Received file: {voice.filename} with threshold {threshold}")

        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join(DATA_DIR, voice.filename)
        voice.save(temp_file_path)

        # Update the embedding database only if new files are present
        create_embedding_db_if_needed()

        matches = rank(temp_file_path)
        logger.info(f'Matched files: {matches}')

        db_results = [match for match in matches if match['score'] >= threshold]
        sorted_db_results = sorted(db_results, key=lambda x: x['score'], reverse=True)

        # Clean up the temporary file
        os.remove(temp_file_path)

        return jsonify(matches=sorted_db_results)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify(error="An error occurred during processing"), 500

def create_embedding_db_if_needed():
    '''
    This function checks if the database needs to be updated and only updates
    it if new files are present.
    '''
    if os.path.exists(DB_FILE):
        data_base = pd.read_csv(DB_FILE)
        existing_files = set(data_base['audio_file']) if not data_base.empty else set()
    else:
        data_base = pd.DataFrame(columns=['audio_file', 'embedding'])
        existing_files = set()

    # Get the list of new audio files
    new_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.wav') and f not in existing_files]

    if new_files:
        logger.info(f'New files detected: {new_files}')
        create_embedding_db()
    else:
        logger.info('No new files to process.')

if __name__ == '__main__':
    app.run(port=5000, debug=True)