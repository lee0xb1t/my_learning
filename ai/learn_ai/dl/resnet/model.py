import torch
import torch.nn as nn
from torch.functional import F
from torchinfo import summary


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, with_conv1=False, strides=1):
        super(ResidualBlock, self).__init__()

        self.features = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=strides, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
        )

        if with_conv1:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=strides),
            )
        else:
            self.shortcut = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1 = self.features(x)
        if self.shortcut:
            x = self.shortcut(x)
        return F.relu(x1 + x)


class ResNet(nn.Module):
    def __init__(self, num_classes=10):
        super(ResNet, self).__init__()

        b1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(num_features=64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
        )

        b2 = nn.Sequential(
            ResidualBlock(64, 64),
            ResidualBlock(64, 64),
        )

        b3 = nn.Sequential(
            ResidualBlock(64, 128, True, 2),
            ResidualBlock(128, 128),
        )

        b4 = nn.Sequential(
            ResidualBlock(128, 256, True, 2),
            ResidualBlock(256, 256),
        )

        b5 = nn.Sequential(
            ResidualBlock(256, 512, True, 2),
            ResidualBlock(512, 512),
        )

        self.net = nn.Sequential(
            b1, b2, b3, b4, b5,
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(in_features=512, out_features=num_classes),
        )

    def forward(self, x):
        return self.net(x)

if __name__ == '__main__':
    net = ResNet(num_classes=10)
    summary(net, (1, 3, 224, 224))
