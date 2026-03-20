import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

if __name__ == '__main__':
    device = torch.device('cuda:0')
    print(torch.cuda.is_available())

    raw = pd.read_csv('../dataset/心脏病数据集/heart_2020_raw.csv')
    raw.drop(['GenHealth'], axis=1, inplace=True)
    print(raw.isnull().sum())
    print(raw.info())

    inputs = raw.iloc[:, 1:]
    labels = raw['HeartDisease']


    print(inputs.iloc[:1, 1:])
    print(labels.iloc[:1])
    print('---')

    print("\n=== 标签分布 ===")
    print("HeartDisease 分布:")
    print(raw['HeartDisease'].value_counts())
    print("\n比例:")
    print(raw['HeartDisease'].value_counts(normalize=True) * 100)


    # 特征工程
    binary_features = ['Smoking', 'Stroke', 'DiffWalking',
                       'Sex', 'PhysicalActivity', 'Asthma',
                       'KidneyDisease', 'SkinCancer']

    label_features = ['AgeCategory', 'Race', 'Diabetic']

    numeric_features = ['BMI', 'PhysicalHealth', 'MentalHealth', 'SleepTime']

    transformer = ColumnTransformer(
        transformers=[
            ('binary', OneHotEncoder(drop='first', sparse_output=False), binary_features),
            ('onehot', OneHotEncoder(drop='first', sparse_output=False), label_features),
            ('scaler', StandardScaler(), numeric_features),
        ],
        remainder='drop'
    )

    label_encoder = LabelEncoder()

    # 将数据划分为测试机和训练集
    X_train, X_test, y_train, y_test = train_test_split(inputs, labels, test_size=0.3, random_state=78, stratify=labels)

    X_train = transformer.fit_transform(X_train)
    X_test = transformer.transform(X_test)

    y_train = label_encoder.fit_transform(y_train)
    y_test = label_encoder.transform(y_test)

    X_train = torch.tensor(X_train, dtype=torch.float32).to(device)
    X_test = torch.tensor(X_test, dtype=torch.float32).to(device)

    y_train = torch.tensor(y_train, dtype=torch.long).to(device)
    y_test = torch.tensor(y_test, dtype=torch.long).to(device)

    print(X_train.shape)

    # model
    batch_size = 32
    learning_rate = 0.001
    epochs = 200
    num_classes = 1

    model = nn.Sequential()
    model.add_module('dense1', nn.Linear(32, 64))
    model.add_module('relu1', nn.ReLU())

    model.add_module('dense2', nn.Linear(64, 32))
    model.add_module('relu2', nn.ReLU())

    model.add_module('dense3', nn.Linear(32, 16))
    model.add_module('relu3', nn.ReLU())

    model.add_module('output', nn.Linear(16, num_classes))

    model = model.to(device)

    # optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)
    loss_func = nn.BCEWithLogitsLoss()

    model.train()
    for epoch in range(epochs):
        # 清0梯度
        optimizer.zero_grad()
        # 前向传播
        logits = model(X_train)
        # 计算损失
        y_train_reshaped = y_train.view(-1, 1).float()
        loss = loss_func(logits, y_train_reshaped)
        # 反向传播
        loss.backward()
        # 更新参数
        optimizer.step()

        if epoch % 10 == 0:
            print("Epoch:", epoch, "Loss:", loss.item())

    model.eval()
    with torch.no_grad():
        val_logits = model(X_test)
        y_test_reshaped = y_test.view(-1, 1).float()
        val_loss = loss_func(val_logits, y_test_reshaped)
        val_prob = torch.sigmoid(val_logits)
        val_pred = (val_prob > 0.5).float()
        accuracy = (val_pred == y_test_reshaped).float().mean()
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {accuracy:.4f}")

    torch.save(model, '../dataset/心脏病数据集/heart_2020.pt')

    joblib.dump(transformer, '../dataset/心脏病数据集/transformer.pkl')
    joblib.dump(label_encoder, '../dataset/心脏病数据集/label_encoder.pkl')