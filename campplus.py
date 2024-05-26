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


if __name__ == "__main__":
  
    args = parser.parse_args()
    wav_path1, wav_path2 = args.wavs
    CAM_model = Campplus()
    
    #wav_path1 = './clips_wav/common_voice_ar_19058496.wav' #.wav 16k sample rate
    #wav_path2 = './clips_wav/common_voice_ar_24175176.wav'
    score = CAM_model.compute_similarty(wav_path1,wav_path2)
    print('similar' if score > CAM_model.threshold else 'not similar')