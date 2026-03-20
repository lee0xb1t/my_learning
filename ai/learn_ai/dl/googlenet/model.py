import torch
import torch.nn as nn
import torch.nn.functional as F
from torchinfo import summary


class Inception(nn.Module):
    def __init__(self, in_channels, c1, c2, c3, c4):
        super(Inception, self).__init__()

        self.p1 = nn.Sequential(
            nn.Conv2d(in_channels, c1, 1),
            nn.BatchNorm2d(c1),
            nn.ReLU(),
        )

        self.p2 = nn.Sequential(
            nn.Conv2d(in_channels, c2[0], 1),
            nn.BatchNorm2d(c2[0]),
            nn.ReLU(inplace=True),
            nn.Conv2d(c2[0], c2[1], 3, padding=1),
            nn.BatchNorm2d(c2[1]),
            nn.ReLU(inplace=True),
        )

        self.p3 = nn.Sequential(
            nn.Conv2d(in_channels, c3[0], 1),
            nn.BatchNorm2d(c3[0]),
            nn.ReLU(inplace=True),
            nn.Conv2d(c3[0], c3[1], 5, padding=2),
            nn.BatchNorm2d(c3[1]),
            nn.ReLU(inplace=True),
        )

        self.p4 = nn.Sequential(
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            nn.Conv2d(in_channels, c4, 1),
            nn.BatchNorm2d(c4),
            nn.ReLU(inplace=True),
        )

    def forward(self, x) -> torch.Tensor:
        p1 = self.p1(x)
        p2 = self.p2(x)
        p3 = self.p3(x)
        p4 = self.p4(x)
        return torch.cat([p1, p2, p3, p4], 1)


class GoogleNet(nn.Module):
    def __init__(self, num_classes=1000):
        super(GoogleNet, self).__init__()
        self.b1 = nn.Sequential(
            nn.Conv2d(1, 64, 7, stride=2, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(3, stride=2, padding=1),
        )
        self.b2 = nn.Sequential(
            nn.Conv2d(64, 64, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 192, 3, padding=1),
            nn.BatchNorm2d(192),
            nn.ReLU(),
            nn.MaxPool2d(3, stride=2, padding=1),
        )
        self.b3 = nn.Sequential(
            Inception(192, 64, (96, 128), (16, 32), 32),
            Inception(256, 128, (128, 192), (32, 96), 64),
            nn.MaxPool2d(3, stride=2, padding=1),
        )
        self.b4 = nn.Sequential(
            Inception(480, 192, (96, 208), (16, 48), 64),
            Inception(512, 160, (112, 224), (24, 64), 64),
            Inception(512, 128, (128, 256), (24, 64), 64),
            Inception(512, 112, (144, 288), (32, 64), 64),
            Inception(528, 256, (160, 320), (32, 128), 128),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )
        self.b5 = nn.Sequential(
            Inception(832, 256, (160, 320), (32, 128), 128),
            Inception(832, 384, (192, 384), (48, 128), 128),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )

        self.model = nn.Sequential(
            self.b1, self.b2, self.b3, self.b4, self.b5,
            nn.Linear(1024, num_classes),
            nn.ReLU(),
        )

        self._init_weights()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None: nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None: nn.init.constant_(m.bias, 0)


if __name__ == '__main__':
    inc = Inception(1, 256, (256, 256), (256, 256), 256)
    summary(inc, (1, 1, 96, 96))

    model = GoogleNet(10)
    summary(model, (1, 1, 96, 96))
