import torch
from torchvision.datasets import FashionMNIST
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.functional import F
import torch.optim as optim
import torch.nn as nn
import numpy as np

from train import LeNetTrainer, get_train_data


def get_validation_data():
    val_dataset_ = FashionMNIST(
        root="./data",
        train=False,
        download=True,
        transform=transforms.Compose([transforms.ToTensor(), ])
    )

    val_data_ = DataLoader(val_dataset_, batch_size=64, shuffle=True)

    return val_data_, val_dataset_.classes

if __name__ == '__main__':
    train_data, labels = get_train_data()
    val_data, val_labels = get_validation_data()
    print(labels)

    trainer = LeNetTrainer(num_classes=len(labels), epochs=50)
    trainer.load_model()

    trainer.set_val_mode()
    trainer.validation(val_data)
