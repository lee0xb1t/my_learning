import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchinfo import summary


class LSTMLoad(nn.Module):
    def __init__(self):
        super(LSTMLoad, self).__init__()

        self.lstm = nn.LSTM(
            input_size=1,
            hidden_size=64,
            num_layers=2,
            batch_first=True,
            dropout=0.2,
        )

        self.fc = nn.Linear(64, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        out = self.fc(out)
        return out


if __name__ == '__main__':
    model = LSTMLoad()
    summary(model, (1, 96, 1))

