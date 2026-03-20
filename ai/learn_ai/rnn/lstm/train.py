import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sympy import sequence
from torch.utils.data import DataLoader
from torchinfo import summary
from sklearn.preprocessing import StandardScaler
import json
from matplotlib import pyplot as plt

from model import LSTMLoad


class LoadTrainer:
    def __init__(self, model_path, epochs: int, device, train=True):
        self.model_path = model_path
        self.device = device
        if train:
            self.model = LSTMLoad()
            self.model.to(self.device)
            self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.loss_fn = nn.MSELoss()
        self.epochs = epochs

        self.train_loss_history = []
        self.val_loss_history = []

    def train(self, train_data_: DataLoader, test_data_: DataLoader):
        self.model.train()

        for epoch in range(self.epochs):
            train_loss_list = []
            test_loss_list = []
            for step, (X_train, y_train) in enumerate(train_data_):
                loss = self._train_model(X_train, y_train)
                train_loss_list.append(loss)

            for step, (X_test, y_test) in enumerate(test_data_):
                self.model.eval()
                test_loss = self._eval_model(X_test, y_test)
                self.model.train()
                test_loss_list.append(test_loss)

            self.train_loss_history.append(np.mean(train_loss_list))
            self.val_loss_history.append(np.mean(test_loss_list))

            print(f'Epoch {epoch + 1}, Train Loss {np.mean(train_loss_list):.4f}, Test Loss {np.mean(test_loss_list):.4f}')


    def _train_model(self, X_train_, y_train_):
        self.optimizer.zero_grad()
        y_pred = self.model(X_train_)
        single_loss = self.loss_fn(y_pred, y_train_)
        single_loss.backward()
        self.optimizer.step()
        return single_loss.item()

    def _eval_model(self, X_test, y_test):
        with torch.no_grad():
            y_pred_test = self.model(X_test)
            single_loss = self.loss_fn(y_pred_test, y_test)
        return single_loss.item()

    def save_model(self):
        loss_and_accuracy = {
            'train': {
                'loss': self.train_loss_history,
            },
            'validation': {
                'loss': self.val_loss_history,
            },
        }
        with open(os.path.join(self.model_path, 'loss.json'), 'w+') as outfile:
            json.dump(loss_and_accuracy, outfile)

        torch.save(self.model, os.path.join(self.model_path, 'model.pt'))

    def load_model(self):
        self.model = torch.load(os.path.join(self.model_path, 'model.pt'), weights_only=False)
        self.model.to(self.device)

    def show_loss(self):
        with open(os.path.join(self.model_path, 'loss.json'), 'r') as outfile:
            loss_and_accuracy = json.load(outfile)
            loss_list = loss_and_accuracy['train']['loss']
            val_loss_list = loss_and_accuracy['validation']['loss']

            epochs = range(1, len(loss_list) + 1)

            plt.subplot(1, 1, 1)
            plt.plot(loss_list, label='Train Loss')
            plt.plot(val_loss_list, '--', label='Val Loss')
            plt.xlabel('Epoch')
            plt.ylabel('Loss')
            plt.legend()
            plt.grid(True)
            plt.xticks(epochs)

            plt.show()

    def eval(self, X_test, transformer):
        self.model.eval()

        X_test = np.array(X_test)
        X_test = transformer.transform(X_test)
        X_test = torch.from_numpy(X_test).float().to(self.device)
        X_test = X_test.unsqueeze(0)

        with torch.no_grad():
            y_pred = self.model(X_test)
        y_pred = y_pred.cpu().numpy()
        y_pred = transformer.inverse_transform(y_pred)
        return y_pred.squeeze()



from load_data import *

if __name__ == '__main__':
    sequence_length = 96
    epochs = 20

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    transformer = StandardScaler()

    trainer = LoadTrainer('./data', epochs, device)

    # data
    dataset = LoadDataset('./data/Load_Forcast.xlsx', '用电量', sequence_length, device, transformer)
    train_data_ = DataLoader(dataset, batch_size=128, shuffle=False)

    dataset = LoadDataset('./data/Load_Forcast.xlsx', '用电量', sequence_length, device, transformer, False)
    test_data_ = DataLoader(dataset, batch_size=128, shuffle=False)

    # train
    trainer.train(train_data_, test_data_)
    trainer.save_model()
    trainer.show_loss()

