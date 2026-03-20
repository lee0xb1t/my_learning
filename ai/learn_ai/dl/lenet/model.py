from typing import Self

import torch
import torch.nn as nn
from torchinfo import summary

class LeNet(nn.Module):
    def __init__(self, num_classes: int):
        super(LeNet, self).__init__()
        self.c1 = nn.Conv2d(1, 6, 5, padding=2)
        self.s2 = nn.AvgPool2d(2, 2)
        self.sig1 = nn.Sigmoid()
        self.c3 = nn.Conv2d(6, 16, 5)
        self.s4 = nn.AvgPool2d(2, 2)
        self.c5 = nn.Conv2d(16, 120, 5, 1, 0)

        self.flatten = nn.Flatten()
        self.nn1 = nn.Linear(120, 84)
        self.tanh = nn.Tanh()
        self.linear = nn.Linear(84, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.c1(x)
        x = self.s2(x)
        x = self.sig1(x)
        x = self.c3(x)
        x = self.s4(x)
        x = self.c5(x)
        x = self.flatten(x)
        x = self.nn1(x)
        x = self.tanh(x)
        return self.linear(x)

if __name__ == '__main__':
    net = LeNet(3)
    print(summary(net, (1, 1, 28, 28)))
