import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import random
import json

"""
    基于pytorch框架编写模型训练
    实现一个自行构造的找规律的任务
    规律：选择最大的
"""

class TorchModel(nn.Module):
    def __init__(self, input_size):
        super(TorchModel, self).__init__()
        self.linear = nn.Linear(input_size, 5)  # 线性层
        self.activation = torch.sigmoid  # sigmoid归一化函数
        self.loss_func = nn.CrossEntropyLoss()  # loss函数采用均方差损失

    def forward(self, x, y=None):
        y_pred = self.linear(x)
        y_pred = self.activation(y_pred)
        if y is not None:
            return self.loss_func(y_pred, y)
        else:
            return y_pred

def build_sample():
    x = np.random.random(5)
    y = [0, 0, 0, 0, 0]
    y[np.argmax(x)] = 1
    return x, y

def build_dataset(total_sample_num):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.FloatTensor(X), torch.FloatTensor(Y)

# 用来测试每轮模型的准确率
def evaluate(model):
    model.eval()
    test_sample_num = 100
    x, y = build_dataset(test_sample_num)
    correct, wrong = 0, 0
    with torch.no_grad():
        y_pred = model(x)  # 模型预测 model.forward(x)
        for y_p, y_t in zip(y_pred, y):  # 与真实标签进行对比
            if(np.argmax(y_p) == np.argmax(y_t)):
                correct += 1
            else:
                wrong += 1
    print("正确预测个数：%d, 正确率：%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)

def main():
    # 配置参数
    epoch_num = 20  # 训练轮数
    batch_size = 20  # 每次训练样本个数
    train_sample = 5000  # 每轮训练总共训练的样本总数
    input_size = 5  # 输入向量维度
    lr = 0.001  # 学习率

    # 构建模型
    model = TorchModel(input_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    log = []
    train_x, train_y = build_dataset(train_sample)
    # 训练
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index*batch_size:(batch_index+1)*batch_size]
            y = train_y[batch_index*batch_size:(batch_index+1)*batch_size]
            loss = model(x, y)
            loss.backward() # 计算梯度
            optimizer.step() # 更新权重
            optimizer.zero_grad()
            watch_loss.append(loss.item())
            print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model)  # 测试本轮模型结果
        log.append([acc, float(np.mean(watch_loss))])
    # 保存模型
    torch.save(model.state_dict(), "csmodel.bin")
    # 画图
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return

# 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    model = TorchModel(input_size)
    model.load_state_dict(torch.load(model_path))  # 加载训练好的权重
    print(model.state_dict())

    model.eval()  # 测试模式
    with torch.no_grad():  # 不计算梯度
        result = model.forward(torch.FloatTensor(input_vec))  # 模型预测
    for vec, res in zip(input_vec, result):
        print(vec,res)


if __name__ == "__main__":
    main()
    # test_vec = [[0.97889086,0.15229675,0.31082123,0.03504317,0.88920843],
    #         [0.74963533,0.5524256,0.95758807,0.95520434,0.84890681],
    #         [0.00797868,0.67482528,0.13625847,0.34675372,0.19871392],
    #         [0.09349776,0.59416669,0.92579291,0.41567412,0.1358894]]
    # predict("csmodel.bin", test_vec)
