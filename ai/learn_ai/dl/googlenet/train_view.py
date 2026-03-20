import torch
from PIL.Image import Image
from torchvision.datasets import FashionMNIST
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.functional import F
import torch.optim as optim
import torch.nn as nn
import numpy as np
import json
from datetime import datetime
from matplotlib import pyplot as plt

from train import GoogleNetTrainer


if __name__ == '__main__':
    GoogleNetTrainer.show_loss_and_accuracy()
