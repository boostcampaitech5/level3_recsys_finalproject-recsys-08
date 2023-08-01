import math
from math import sqrt
import torch
import torch.nn as nn
import torch.nn.functional as F

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len):
        super(PositionalEncoding, self).__init__()
        self.encoding = torch.zeros(max_len, d_model)
        self.encoding.requires_grad = False
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        self.encoding[:, 0::2] = torch.sin(position * div_term)
        self.encoding[:, 1::2] = torch.cos(position * div_term)
        self.encoding = self.encoding.unsqueeze(0)

    def forward(self, x):
        device = x.device
        return x + self.encoding[:, :x.size(1)].detach().to(device)

class MultiHeadAttention(nn.Module):
    def __init__(self, hidden_dim, num_heads, dropout):
        super(MultiHeadAttention, self).__init__()
        self.h = num_heads # 병렬 attention head 개수
        self.head_dim = hidden_dim // num_heads
        # self.d_model = hidden_dim * num_heads ##
        self.d_model = hidden_dim ##
        
        self.Q_fc = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.K_fc = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.V_fc = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.O_fc = nn.Linear(hidden_dim, hidden_dim, bias=False)
        
        self.dropout = nn.Dropout(dropout)
        self.layerNorm = nn.LayerNorm(hidden_dim, 1e-6)
        
    def forward(self, Q, K, V, mask=None):
        n_batch = Q.size(0)
        residual = Q
        
        def transform(x, fc):
            out = fc(x)
            out = out.view(n_batch, -1, self.h, self.head_dim)
            out = out.transpose(1, 2)
            return out
        
        Q = transform(Q, self.Q_fc)
        K = transform(K, self.K_fc)
        V = transform(V, self.V_fc)
        d_k = K.shape[-1]
        device = torch.device('cuda')
        attention_score = torch.matmul(Q, K.transpose(-2, -1))
        attention_score = attention_score / torch.sqrt(torch.tensor(d_k, dtype=torch.double, device=device))
            
        if mask is not None:
            attention_score = attention_score.masked_fill(mask == 0, -1e12)
        
        attention_score = F.softmax(attention_score, dim=-1)
        out = torch.matmul(attention_score, V)
        out = out.transpose(1, 2).contiguous().view(n_batch, -1, self.d_model)
        out = self.O_fc(out)
        out = self.dropout(out) + residual
        return self.layerNorm(out)
    
class PointWiseFeedForward(nn.Module):
    def __init__(self, hidden_dim, dropout):
        super(PointWiseFeedForward, self).__init__()
        self.hidden_size = hidden_dim
        self.fc1 = nn.Linear(self.hidden_size, self.hidden_size * 4)
        self.activation = lambda x: x * 0.5 * (1.0 + torch.erf(x / sqrt(2.0)))
        self.fc2 = nn.Linear(self.hidden_size * 4, self.hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.layerNorm = nn.LayerNorm(self.hidden_size, 1e-6)
        
    def forward(self, x):
        residual = x
        out = self.fc1(x)
        out = self.activation(out)
        out = self.fc2(out)
        out = self.dropout(out) + residual
        return out

class SASRecBlock(nn.Module):
    def __init__(self, hidden_dim, num_heads, dropout):
        super(SASRecBlock, self).__init__()
        self.self_attention = MultiHeadAttention(hidden_dim, num_heads, dropout)
        self.pointwise_feed_forward = PointWiseFeedForward(hidden_dim, dropout)

    def forward(self, x, mask):
        out = self.self_attention(x, x, x, mask)
        out = self.pointwise_feed_forward(out)
        return out
    
class SASRec(nn.Module):
    def __init__(self, max_seq_length, hidden_dim, num_heads, num_blocks, dropout):
        super(SASRec, self).__init__()
        self.positional_encoding = PositionalEncoding(hidden_dim, max_seq_length)
        self.sas_blocks = nn.ModuleList([SASRecBlock(hidden_dim, num_heads, dropout) for _ in range(num_blocks)])
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_dim, eps=1e-6)

        self.initializer_range = args.initializer_range
        self.apply(self.init_weights)
        
    def make_pad_mask(self, x, pad_idx=0): ##
        max_seq_length = x.size(-1)

        row_wise = x.ne(pad_idx).unsqueeze(1).unsqueeze(3)
        row_wise = row_wise.repeat(1, 1, 1, max_seq_length)

        column_wise = x.ne(pad_idx).unsqueeze(1).unsqueeze(2)
        column_wise = column_wise.repeat(1, 1, max_seq_length, 1)

        pad_mask = row_wise & column_wise
        pad_mask.requires_grad = False

        return pad_mask
    
    def make_subsequent_mask(self, x, pad_idx=0): ##
        max_seq_length = x.size(-1)

        attention_shape = (1, max_seq_length, max_seq_length)
        subsequent_mask = torch.triu(torch.ones(attention_shape), diagonal=1)
        subsequent_mask = (subsequent_mask == pad_idx).unsqueeze(1)
        subsequent_mask.requires_grad = False

        return subsequent_mask
    
    def init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Embedding)):
            module.weight.data.normal_(mean=0.0, std=self.initializer_range)
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        if isinstance(module, nn.Linear) and module.bias is not None:
            module.bias.data.zero_()
    
    def forward(self, input_seq, mask=None):
        # Embedding and positional encoding
        seqs = input_seq
        seqs += self.positional_encoding(seqs)

        mask_pad = self.make_pad_mask(mask).to(seqs.device) ## 
        mask_time = self.make_subsequent_mask(mask).to(seqs.device) ##
        mask = mask_pad & mask_time

        # print(mask.shape)

        # Transformer blocks
        for sas_block in self.sas_blocks: 
            seqs = sas_block(seqs, mask)
        output = seqs
        return output
    
    # setting
def setting_model(args):
    device = args.device
    model = SASRec(args.max_len, args.d_embed, args.num_heads, args.num_layers, args.dropout_rate)
    model.to(device)
    # 모델의 가중치 파라미터를 Double 형식으로 설정
    model.apply(lambda module: setattr(module, 'dtype', torch.double))
    return model
