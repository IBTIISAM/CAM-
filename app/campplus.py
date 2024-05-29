# Copyright 3D-Speaker (https://github.com/alibaba-damo-academy/3D-Speaker). All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""
Created on Mon May 20 13:59:58 2024

@author: ibtesam
"""
import torch
import torchaudio
import argparse
from utils import dynamic_import, FBank
import ast 
import os
import pandas as pd
import numpy as np
parser = argparse.ArgumentParser(description='Extract speaker embeddings.')
parser.add_argument('--wavs', nargs='+', type=str, help='Wavs')

class Campplus:#CAM++
    
    def __init__(self):        
        self.model_path        = 'campplus_voxceleb.bin'
        self.campplus_vox      = {'obj': 'speakerlab.models.campplus.DTDNN.CAMPPlus',
                                  'args': {'feat_dim': 80,'embedding_size': 512}}
        self.device            = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.feature_extractor = FBank(80, sample_rate=16000, mean_nor=True)
        self.threshold         = 0.38 #cosine similarty score between (-1,1) , similar if score > 0.38
        self.embedding_model   = self.load_model()  # Load the model during initialization
        
    def load_model(self):
        pretrained_state = torch.load(self.model_path, map_location='cpu')
        embedding_model = dynamic_import(self.campplus_vox['obj'])(**self.campplus_vox['args'])
        embedding_model.load_state_dict(pretrained_state)
        embedding_model.to(self.device)
        embedding_model.eval()
        return embedding_model
    
    def load_wav(self, wav_file, obj_fs=16000):
       wav, fs = torchaudio.load(wav_file)
       if fs != obj_fs:
           #print(f'[WARNING]: The sample rate of {wav_file} is not {obj_fs}, resample it.')
           wav, fs = torchaudio.sox_effects.apply_effects_tensor(
               wav, fs, effects=[['rate', str(obj_fs)]]
           )
       if wav.shape[0] > 1:
           wav = wav[0, :].unsqueeze(0)   
       return wav
   
    def compute_embedding(self, wav_file):
            wav = self.load_wav(wav_file)
            feat = self.feature_extractor(wav).unsqueeze(0).to(self.device)
            with torch.no_grad():
                embedding = self.embedding_model(feat).detach().cpu().numpy()  
            return embedding

    def compute_similarty(self, wav_file1, wav_file2):
        """calculate cosin similarity between two audio files."""        
        # Get embeddings
        embedding1 = self.compute_embedding(wav_file1)
        embedding2 = self.compute_embedding(wav_file2)
       
        similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
        score = similarity(torch.from_numpy(embedding1), torch.from_numpy(embedding2)).item()
        return score


def pred_similarity(wav_path1, wav_path2):
  
    CAM_model = Campplus()
    
    #wav_path1 = './clips_wav/common_voice_ar_19058496.wav' #.wav 16k sample rate
    #wav_path2 = './clips_wav/common_voice_ar_24175176.wav'
    score = CAM_model.compute_similarty(wav_path1,wav_path2)
    print('similar' if score > CAM_model.threshold else 'not similar')
    return(score)

def embed_audio(wav_path1):
    CAM_model = Campplus()
    file_embedding=CAM_model.compute_embedding(wav_path1)
    return file_embedding

def create_embedding_db():
    db_file = 'data_base.csv'
    directory = os.path.join('.', 'data')

    # Check if the database file exists
    if os.path.exists(db_file):
        # Load the existing database
        data_base = pd.read_csv(db_file)
    else:
        # Create a new DataFrame if the database does not exist
        data_base = pd.DataFrame(columns=['audio_file', 'embedding'])

    # Get the list of audio files already in the database
    existing_files = set(data_base['audio_file']) if not data_base.empty else set()

    for audio_file in os.listdir(directory):
        if audio_file.endswith('.wav') and audio_file not in existing_files:  # Ensure you only process new audio files
            audio_path = os.path.join(directory, audio_file)
            audio_embedding = embed_audio(audio_path)
            # Create a DataFrame for the new row
            new_row = pd.DataFrame({'audio_file': [audio_file], 'embedding': [audio_embedding.tolist()]})
            # Concatenate the new row to the existing DataFrame
            data_base = pd.concat([data_base, new_row], ignore_index=True)

    # Save the updated DataFrame to a CSV file
    data_base.to_csv(db_file, index=False)


def rank(audio_file):
    audio_embedding = embed_audio(audio_file)
    similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
    db = pd.read_csv('data_base.csv')
    
    results = []
    for i in range(len(db)):
        file_name = db.iloc[i]['audio_file']
        # Convert the string representation of the list back to a tensor
        embedding_db = torch.tensor(ast.literal_eval(db.iloc[i]['embedding']))
        score = np.round(100*similarity(embedding_db, torch.tensor(audio_embedding)).item(),2)
        results.append({"file": file_name, "score": score})
    
    return results

