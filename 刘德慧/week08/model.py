# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from torch.optim import Adam, SGD
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
"""
建立网络模型结构
"""


# 将输入的句子编码为固定长度的向量。
class SentenceEncoder(nn.Module):

    def __init__(self, config):
        super(SentenceEncoder, self).__init__()
        hidden_size = config["hidden_size"]
        vocab_size = config["vocab_size"] + 1
        max_length = config["max_length"]
        self.embedding = nn.Embedding(vocab_size, hidden_size, padding_idx=0)
        self.lstm = nn.LSTM(hidden_size,
                            hidden_size,
                            batch_first=True,
                            bidirectional=True)
        self.layer = nn.Linear(hidden_size * 2, hidden_size)
        self.dropout = nn.Dropout(0.5)

    #输入为问题字符编码
    def forward(self, x):
        x = self.embedding(x)  # shape = [batch_size, max_length, hidden_size]
        # 使用lstm
        x, _ = self.lstm(x)  # shape = [batch_size, max_length, hidden_size*2]
        #使用线性层
        x = self.layer(x)  # shape = [batch_size, max_length, hidden_size]
        x = nn.functional.max_pool1d(x.transpose(
            1, 2), x.shape[1]).squeeze()  # shape = [batch_size, hidden_size]
        return x


class SiameseNetwork(nn.Module):

    def __init__(self, config):
        super(SiameseNetwork, self).__init__()
        self.sentence_encoder = SentenceEncoder(config)

    # 计算余弦距离  1-cos(a,b)，0到2之间，值越小表示两个向量越相似
    # cos=1时两个向量相同，余弦距离为0；cos=0时，两个向量正交，余弦距离为1
    def cosine_distance(self, tensor1, tensor2):
        tensor1 = torch.nn.functional.normalize(
            tensor1, dim=-1)  # 对 tensor1 进行 L2 归一化，将向量的长度缩放为1
        tensor2 = torch.nn.functional.normalize(tensor2, dim=-1)
        cosine = torch.sum(torch.mul(tensor1, tensor2),
                           axis=-1)  # 计算归一化后的两个张量的点积（内积），并在最后一个维度上求和
        return 1 - cosine

    def cosine_triplet_loss(self, a, p, n, margin=None):
        ap = self.cosine_distance(a, p)
        an = self.cosine_distance(a, n)
        if margin is None:
            diff = ap - an + 0.1
        else:
            diff = ap - an + margin.squeeze()
        return torch.mean(diff[diff.gt(0)])  #greater than

    #sentence : (batch_size, max_length)
    def forward(self, sentence1, sentence2=None, sentence3=None):
        #同时传入三个句子
        if sentence2 is not None and sentence3 is not None:
            vector1 = self.sentence_encoder(
                sentence1)  #vec:(batch_size, hidden_size)
            vector2 = self.sentence_encoder(sentence2)
            vector3 = self.sentence_encoder(sentence3)
            return self.cosine_triplet_loss(vector1, vector2, vector3)
        else:
            #只传入一个句子
            vector1 = self.sentence_encoder(
                sentence1)  #vec:(batch_size, hidden_size)


def choose_optimizer(config, model):
    optimizer = config["optimizer"]
    learning_rate = config["learning_rate"]
    if optimizer == "adam":
        return Adam(model.parameters(), lr=learning_rate)
    elif optimizer == "sgd":
        return SGD(model.parameters(), lr=learning_rate)


if __name__ == "__main__":
    from config import Config
    Config["vocab_size"] = 10
    Config["max_length"] = 4
    model = SiameseNetwork(Config)
    s1 = torch.LongTensor([[1, 2, 3, 0], [2, 2, 0, 0]])
    s2 = torch.LongTensor([[1, 2, 3, 4], [3, 2, 3, 4]])
    l = torch.LongTensor([[1], [0]])
    y = model(s1, s2, l)
    print(y)
    # print(model.state_dict())
