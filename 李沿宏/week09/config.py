# -*- coding: utf-8 -*-

"""
配置参数信息
"""

Config = {
    "model_path": "model_output",
    "schema_path": "ner_data/schema.json",
    "train_data_path": "ner_data/train",
    "valid_data_path": "ner_data/test",
    "vocab_path": "chars.txt",
    "max_length": 100,
    "hidden_size": 768,  # BERT的隐藏层大小
    "num_layers": 2,
    "epoch": 20,
    "batch_size": 16,
    "optimizer": "adam",
    "learning_rate": 2e-5,  # BERT通常使用较小的学习率
    "use_crf": False,
    "class_num": 9,
    "bert_path": r"F:\Desktop\work_space\pretrain_models\bert-base-chinese"  # BERT模型路径
}