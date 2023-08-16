import numpy as np
import torch
from torch.utils.data import Dataset

class Dataset(Dataset):
    def __init__(self, args, corp_seq, data_type="train"):
        self.args = args
        self.corp_seq = corp_seq
        self.data_type = data_type
        self.max_len = args.max_len
        self.d_embed = args.d_embed
        
    def __len__(self):
        return len(self.corp_seq)
    
    def __getitem__(self, index):

        corp_id = index
        patents = self.corp_seq[index] # index번째 기업의 sequence 

        # 각 patent는 embedding vector로 구성
        
        # [patent0, patent1, patent2, patent3, patent4, patent5, patent6]
        # train [patent0, patent1, patent2, patent3]
        # target [patent1, patent2, patent3, patent4]

        # valid [patent0, patent1, patent2, patent3, patent4]
        # answer [patent5]

        # test [patent0, patent1, patent2, patent3, patent4, patent5] 
        # answer [patent6]

        if self.data_type == "train":
            input_ids = patents[:-2]
            target_pos = patents[1:-1]
            answer = [0] # no use

        elif self.data_type == "valid":
            input_ids = patents[:-1]
            target_pos = patents[1:]
            # answer = [patents[-1]]
            answer = np.array([patents[-1]])
        else:
            input_ids = patents[:]
            target_pos = patents[:]  # will not be used
            answer = []
        
        mask = np.ones(self.max_len)
        pad_len = self.max_len - len(input_ids)
        if pad_len > 0 :
            pad = np.zeros((pad_len,self.d_embed))
            input_ids = np.concatenate((pad,input_ids),axis=0)
            target_pos = np.concatenate((pad,target_pos),axis=0)

            mask[:pad_len] = 0
            
        input_ids = input_ids[-self.max_len :]
        target_pos = target_pos[-self.max_len :]


        assert len(input_ids) == self.max_len
        assert len(target_pos) == self.max_len
        device = torch.device("cuda")

        cur_tensors = (
            torch.tensor(corp_id, device=device),  # user_id for testing
            torch.tensor(mask, device=device),  # user_id for testing
            torch.tensor(input_ids,dtype = torch.float, device=self.args.device),
            torch.tensor(target_pos,dtype = torch.float, device=self.args.device),
            torch.tensor(answer,dtype = torch.float, device=self.args.device),
        )

        return cur_tensors


    