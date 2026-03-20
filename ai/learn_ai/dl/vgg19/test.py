import torch
from torchvision.datasets import FashionMNIST
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.functional import F
import torch.optim as optim
import torch.nn as nn
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

from model import VGG16Net
from train import VGG16NetTrainer


if __name__ == '__main__':
    img = Image.open("./data/test/8.png").convert("L")

    labels = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

    trainer = VGG16NetTrainer(num_classes=len(labels), epochs=0, train=True)
    trainer.load_model()
    trainer.set_val_mode()
    eval_probs, eval_pred = trainer.eval(img)

    for i, p in enumerate(eval_probs):
        # 使用 .15f 保留15位小数（足够显示微小值）
        print(f"Class {labels[i]:<15}: {p:>20.15f} {" <" if p > 0.5 else ""}")

    print(f"Pred Class: {labels[eval_pred]}")
