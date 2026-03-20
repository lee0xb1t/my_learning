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

from train import ResNetTrainer


if __name__ == '__main__':
    img = Image.open("./data/test/hongpingguo.webp").convert("RGB")

    # labels = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
    labels = ['哈密瓜', '圣女果', '山竹', '杨梅', '柚子', '柠檬', '桂圆', '梨', '椰子', '榴莲', '火龙果', '猕猴桃', '石榴', '砂糖橘', '胡萝卜', '脐橙', '芒果', '苦瓜', '苹果-红', '苹果-青', '草莓', '荔枝', '菠萝', '葡萄-白', '葡萄-红', '西瓜', '西红柿', '车厘子', '香蕉', '黄瓜']

    trainer = ResNetTrainer('./data/fruit30', num_classes=len(labels), epochs=0, train=True)
    trainer.load_model()
    trainer.set_val_mode()
    eval_probs, eval_pred = trainer.eval(img)

    for i, p in enumerate(eval_probs):
        # 使用 .15f 保留15位小数（足够显示微小值）
        print(f"Class {labels[i]:<15}: {p:>20.15f} {" <" if p > 0.5 else ""}")

    print(f"Pred Class: {labels[eval_pred]}")
