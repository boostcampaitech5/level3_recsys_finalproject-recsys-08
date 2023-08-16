import math
import random

import numpy as np
import pandas as pd

import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.utils.data import DataLoader
from .dataset import *
from .annoy import *

class Inference:
    def __init__(self,args, corp_seq,key, transformer, annoy_index, count_dict,key2idx):
        self.args = args
        self.corp_seq = corp_seq
        self.n_trees = self.args.n_trees
        self.n = self.args.n
        self.d_embed = self.args.d_embed
        self.key = key
        self.model = transformer
        self.annoy_index = annoy_index
        self.device = self.args.device
        self.key2idx = key2idx
        
    def inference(self):
        device = torch.device(self.device)
        idx = self.key2idx[self.key]
        inference_dataset = Dataset(self.args, self.corp_seq, data_type="inference")[idx]
        inference_dataloader = DataLoader(inference_dataset, batch_size= 1)
        with torch.no_grad():
            self.model.eval()
            corp_id, mask, input_seq, target_pos, _ = inference_dataloader
            mask = mask.to(device)
            input_seq, target_pos = input_seq.to(device), target_pos.to(device)
            output = self.model(input_seq, mask=mask)
            output = output[:, -1, :].cpu().data.numpy()
        output = output.reshape(-1,1)
        return output
    
    def scoring(self,df_biz):
        self.inference_vector = self.inference()
        annoy = Annoy(self.args, self.annoy_index)
        ann_idx,ann_score = annoy.find_annoy(self.inference_vector) # (768, 1)
        score_dict = {}
        for idx,score in zip(ann_idx,ann_score):
            key = df_biz.iloc[idx]['key']
            if key not in score_dict:
                score_dict[key] = [1,score]
            else:
                score_dict[key][0] += 1
                
        return score_dict
    
    def find_candidates(self,df_biz):
        score_dict = self.scoring(df_biz)
        k = len(score_dict)
        key_list = np.repeat(self.key, k)
        sorted_score = sorted(score_dict.items(), key=lambda x: (x[1][0],x[1][1]), reverse=True)
        target_key_list = []
        for target_corp_info in sorted_score:
            target_corp_key = target_corp_info[0]
            target_key_list.append(target_corp_key)
        df_candidate = pd.DataFrame({'의뢰기업_key':key_list,'대상기업_key':target_key_list})
        return df_candidate
    
    def filtering(self,inference):
        df_value = pd.read_csv('../../corp_valuation_v2.csv')
        value_dict = dict(zip(df_value['회사명'],df_value['기업가치']))
        inference['의뢰기업_기업가치'] = inference['의뢰기업_key'].map(value_dict)
        inference['추천회사_기업가치'] = inference['대상기업_key'].map(value_dict)
        df_inference = inference[inference['의뢰기업_기업가치'] > inference['추천회사_기업가치']].drop(['의뢰기업_기업가치','추천회사_기업가치'],axis=1)
        return df_inference