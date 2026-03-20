import os
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np


class LoadDataset(Dataset):
    def __init__(self, path, sheet_name, sequence_length, device, transform=None, train=True, test_ratio=0.2):
        self.device = device
        self.path = path
        self.sheet_name = sheet_name
        self.sequence_length = sequence_length
        self.train = train
        self.test_ratio = test_ratio
        self.transform = transform

        dataset_ = pd.read_excel(path, sheet_name, index_col=(0, 1, 2))
        dataset_ = dataset_.fillna(0)
        dataset_ = np.array(dataset_)
        data = dataset_.reshape(-1, 1)

        if train:
            data = self.transform.fit_transform(data)
        else:
            data = self.transform.transform(data)

        X, y = [], []
        for i in range(len(data) - sequence_length):
            X.append(data[i:i + sequence_length])
            y.append(data[i + sequence_length])
        X, y = np.array(X), np.array(y)

        split_idx = int(len(X) * (1 - test_ratio))
        self.X_train, self.X_test = X[:split_idx], X[split_idx:]
        self.y_train, self.y_test = y[:split_idx], y[split_idx:]

    def __len__(self):
        if self.train:
            return len(self.X_train)
        else:
            return len(self.X_test)

    def __getitem__(self, idx):
        if self.train:
            X_train, y_train = self.X_train[idx], self.y_train[idx]
            X_train = torch.FloatTensor(X_train).to(self.device)
            y_train = torch.FloatTensor(y_train).to(self.device)
            return X_train, y_train
        else:
            X_test, y_test = self.X_test[idx], self.y_test[idx]
            X_test = torch.FloatTensor(X_test).to(self.device)
            y_test = torch.FloatTensor(y_test).to(self.device)
            return X_test, y_test


if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    transformer = StandardScaler()

    dataset = LoadDataset('./data/Load_Forcast.xlsx', '用电量', 96, device, transformer)
    train_data_ = DataLoader(dataset, batch_size=1, shuffle=False)
    for step, (x, y) in enumerate(train_data_):
        print(x.shape)
        print(y.shape)
        break

    dataset = LoadDataset('./data/Load_Forcast.xlsx', '用电量', 96, device, transformer, False)
    test_data_ = DataLoader(dataset, batch_size=1, shuffle=False)
    for step, (x, y) in enumerate(test_data_):
        print(x.shape)
        print(y.shape)
        break