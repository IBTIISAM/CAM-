import os
import random
import logging
import time
from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
from campplus import create_embedding_db, rank,pred_similarity
import pandas as pd
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import numpy as np
app = Flask(__name__)

# Configure Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('flask_app')

# Path to the data directory
DATA_DIR = './data'
DB_FILE = 'data_base.csv'

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def convert_webm_to_wav(input_file, output_file):
    try:
        logger.info(f"Converting {input_file} to {output_file} using pydub")
        audio = AudioSegment.from_file(input_file, format="webm")
        audio.export(output_file, format="wav")
        logger.info(f"Conversion successful: {input_file} to {output_file}")
    except CouldntDecodeError as e:
        logger.error(f"Error decoding file with pydub: {e}")
        raise e
    except Exception as e:
        logger.error(f"General error during conversion: {e}")
        raise e

def process_file(file, filename):
    temp_file_path = os.path.join(DATA_DIR, filename)
    logger.info(f"Saving file {filename} to {temp_file_path}")
    file.save(temp_file_path)
    
    # Log the file size to check for empty files
    file_size = os.path.getsize(temp_file_path)
    logger.info(f"File size: {file_size} bytes")

    if file_size == 0:
        logger.error(f"File is empty: {temp_file_path}")
        raise ValueError(f"File is empty: {temp_file_path}")

    # Determine file type and convert if necessary
    if filename.endswith('.webm'):
        temp_wav_path = temp_file_path.replace('.webm', '.wav')
        convert_webm_to_wav(temp_file_path, temp_wav_path)
        os.remove(temp_file_path)  # Clean up the original .webm file
        return temp_wav_path
    elif filename.endswith('.wav'):
        return temp_file_path
    else:
        raise ValueError("Unsupported file type")

@app.route('/')
@cache.cached(timeout=60)  # Cache this view for 60 seconds
def index():
    start_time = time.time()
    response = render_template('fe.html')
    end_time = time.time()
    logger.info(f"Main page loaded in {end_time - start_time:.2f} seconds")
    return response

@app.route('/audio_record_and_upload')
@cache.cached(timeout=60)  # Cache this view for 60 seconds
def audio_record_and_upload():
    return render_template('audio_record_and_upload.html')

@app.route('/compare_with_database')
@cache.cached(timeout=60)  # Cache this view for 60 seconds
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

        # Process the uploaded files
        temp_voice1_path = process_file(voice1, voice1.filename)
        temp_voice2_path = process_file(voice2, voice2.filename)
        
        files = os.listdir('./data')
        
        # Log the list of files
        logging.info(f'Files in directory : {files}')
        
        # Process the .wav files (you can add your specific processing logic here)
        score = np.round(100*pred_similarity(temp_voice1_path,temp_voice2_path),2)

        # Clean up the temporary files
        os.remove(temp_voice1_path)
        os.remove(temp_voice2_path)
        
        return jsonify(result="Comparison result here", confidence=score)
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
        start_time = time.time()
        
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

        # Process the uploaded file
        temp_file_path = process_file(voice, voice.filename)

        # Update the embedding database only if new files are present
        create_embedding_db_if_needed()

        matches = rank(temp_file_path)
        logger.info(f'Matched files: {matches}')

        db_results = [match for match in matches if match['score'] >= threshold]
        sorted_db_results = sorted(db_results, key=lambda x: x['score'], reverse=True)

        # Clean up the temporary file
        os.remove(temp_file_path)

        end_time = time.time()
        logger.info(f"Processing time: {end_time - start_time:.2f} seconds")

        return jsonify(matches=sorted_db_results)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify(error="An error occurred during processing"), 500

def create_embedding_db_if_needed():
    '''
    This function checks if the database needs to be updated and only updates
    it if new files are present.
    '''
    try:
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
    except Exception as e:
        logger.error(f"Error in create_embedding_db_if_needed: {str(e)}")

if __name__ == '__main__':
    logger.info("Starting Flask app...")
    start_time = time.time()
    app.run(host="0.0.0.0", port=5000)
    end_time = time.time()
    logger.info(f"Flask app started in {end_time - start_time:.2f} seconds")