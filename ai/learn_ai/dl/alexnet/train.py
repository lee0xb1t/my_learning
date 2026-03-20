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

from model import AlexNet


def get_train_data():
    train_dataset = FashionMNIST(
        root="./data",
        train=True,
        download=True,
        transform=transforms.Compose([transforms.Resize(224) ,transforms.ToTensor(), ])
    )

    train_data_ = DataLoader(train_dataset, batch_size=512, shuffle=True)

    return train_data_, train_dataset.classes

def get_validation_data():
    val_dataset_ = FashionMNIST(
        root="./data",
        train=False,
        download=True,
        transform=transforms.Compose([transforms.Resize(224) ,transforms.ToTensor(), ])
    )

    val_data_ = DataLoader(val_dataset_, batch_size=512, shuffle=False)

    return val_data_, val_dataset_.classes

class AlexNetTrainer:
    def __init__(self, num_classes: int, epochs: int, train: bool = False):
        self.train_mode = train
        self.num_classes = num_classes
        self.epochs = epochs

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if self.train_mode:
            self.model = AlexNet(num_classes)
            self.model.to(self.device)
            self.model.train()

            self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.criterion = nn.CrossEntropyLoss()

        self.train_accuracy_per_epoch = []
        self.train_loss_per_epoch = []

        self.val_accuracy_per_epoch = []
        self.val_loss_per_epoch = []

    def _train_batch(self, x_batch_: torch.Tensor, y_batch_: torch.Tensor):
        self.optimizer.zero_grad()
        logits = self.model(x_batch_)
        loss = self.criterion(logits, y_batch_)
        loss.backward()
        self.optimizer.step()

        _train_loss = loss.item()
        _train_prob = F.softmax(logits, dim=1)
        _train_pred = torch.argmax(_train_prob, dim=1)
        _train_accuracy = torch.mean((_train_pred == y_batch_).float()).item()

        return _train_loss, _train_accuracy


    def _val_batch(self, x_batch_: torch.Tensor, y_batch_: torch.Tensor):
        with torch.no_grad():
            logits = self.model(x_batch_)
            loss = self.criterion(logits, y_batch_)

        _train_loss = loss.item()
        _train_prob = F.softmax(logits, dim=1)
        _train_pred = torch.argmax(_train_prob, dim=1)
        _train_accuracy = torch.mean((_train_pred == y_batch_).float()).item()

        return _train_loss, _train_accuracy

    # def __mean_loss(self):
    #     return np.mean(self.train_loss_list)
    #
    # def __mean_accuracy(self):
    #     return np.mean(self.train_accuracy_list)
    #
    # def __mean_val_loss(self):
    #     return np.mean(self.val_loss_list)
    #
    # def __mean_val_accuracy(self):
    #     return np.mean(self.val_accuracy_list)

    def train(self, train_data_: DataLoader, val_data_: DataLoader):
        if not self.train_mode:
            raise Exception("Current is not training mode")

        total_start_time = datetime.now()

        for epoch in range(self.epochs):
            step_accuracy_list = []
            step_loss_list = []

            step_val_accuracy_list = []
            step_val_loss_list = []

            start_time = datetime.now()

            for step, (_imgs, _labels) in enumerate(train_data_):
                _imgs = _imgs.to(self.device)
                _labels = _labels.to(self.device)
                train_loss, train_accuracy = self._train_batch(_imgs, _labels)

                step_loss_list.append(train_loss)
                step_accuracy_list.append(train_accuracy)

                # print("Epoch:{}/{}, Step: {}, Loss: {}, Accuracy: {}".format(epoch+1, self.epochs, step, self.__mean_loss(), self.__mean_accuracy()))

            for step, (_imgs, _labels) in enumerate(val_data_):
                self.model.eval()
                _imgs = _imgs.to(self.device)
                _labels = _labels.to(self.device)
                val_loss, val_accuracy = self._val_batch(_imgs, _labels)
                step_val_accuracy_list.append(val_accuracy)
                step_val_loss_list.append(val_loss)
                self.model.train()

            mean_loss = np.array(step_loss_list).mean()
            mean_accuracy = np.array(step_accuracy_list).mean()
            self.train_loss_per_epoch.append(mean_loss)
            self.train_accuracy_per_epoch.append(mean_accuracy)

            val_mean_loss = np.array(step_val_loss_list).mean()
            val_mean_accuracy = np.array(step_val_accuracy_list).mean()
            self.val_loss_per_epoch.append(val_mean_loss)
            self.val_accuracy_per_epoch.append(val_mean_accuracy)

            time_diff = datetime.now() - start_time
            minutes, seconds = divmod(time_diff.seconds, 60)

            print("Epoch:{}/{}, Loss: {}, Accuracy: {}, Val Loss: {}, Val Accuracy: {}, {}分{}秒".format(epoch + 1, self.epochs, mean_loss,
                                                               mean_accuracy, val_mean_loss, val_mean_accuracy, minutes, seconds))

        total_time_diff = datetime.now() - total_start_time
        minutes, seconds = divmod(total_time_diff.seconds, 60)
        print("Total time: {}分{}秒".format(minutes, seconds))


    # def validation(self, val_data_: DataLoader):
    #     if self.train_mode:
    #         raise Exception("Current is training mode")
    #
    #     step_accuracy_list = []
    #     step_loss_list = []
    #
    #     for step, (_val_imgs, _val_labels) in enumerate(val_data_):
    #         _val_imgs = _val_imgs.to(self.device)
    #         _val_labels = _val_labels.to(self.device)
    #         val_loss, val_accuracy = self._val_batch(_val_imgs, _val_labels)
    #
    #         step_accuracy_list.append(val_accuracy)
    #         step_loss_list.append(val_loss)
    #
    #     mean_loss = np.array(step_loss_list).mean()
    #     mean_accuracy = np.array(step_accuracy_list).mean()
    #
    #     print("[Validate] Loss: {}, Accuracy: {}".format( mean_loss, mean_accuracy))
    #
    #     self.val_accuracy_per_epoch.append(mean_loss)
    #     self.val_loss_per_epoch.append(mean_accuracy)

    def eval(self, img):
        transform = transforms.Compose([transforms.Resize(224), transforms.ToTensor(), ])
        img = transform(img)
        img = img.unsqueeze(0)
        img = img.to(self.device)

        with torch.no_grad():
            logits = self.model(img)
            _eval_prob = F.softmax(logits, dim=1)
            _eval_pred = torch.argmax(_eval_prob, dim=1)

        _eval_probs = _eval_prob.squeeze().tolist()
        _eval_pred = _eval_pred.item()

        return _eval_probs, _eval_pred

    def save_model(self):
        loss_and_accuracy = {
            'train': {
                'loss': self.train_loss_per_epoch,
                'accuracy': self.train_accuracy_per_epoch,
            },
            'validation': {
                'loss': self.val_loss_per_epoch,
                'accuracy': self.val_accuracy_per_epoch,
            },
        }
        with open('./data/FashionMNIST/loss_and_accuracy.json', 'w+') as outfile:
            json.dump(loss_and_accuracy, outfile)

        torch.save(self.model, 'data/FashionMNIST/model.pt')

    def load_model(self):
        self.model = torch.load('data/FashionMNIST/model.pt', weights_only=False)
        self.model.to(self.device)

    def set_train_mode(self):
        self.train_mode = True
        self.model.train()

    def set_val_mode(self):
        self.train_mode = False
        self.model.eval()

    def show_loss_and_accuracy(self):
        with open('./data/FashionMNIST/loss_and_accuracy.json', 'r') as outfile:
            loss_and_accuracy = json.load(outfile)
            loss_list = loss_and_accuracy['train']['loss']
            accuracy_list = loss_and_accuracy['train']['accuracy']
            val_loss_list = loss_and_accuracy['validation']['loss']
            val_accuracy_list = loss_and_accuracy['validation']['accuracy']

            epochs = range(1, len(loss_list) + 1)

            plt.subplot(1, 2, 1)
            plt.plot(loss_list, label='Train Loss')
            plt.plot(val_loss_list, '--', label='Val Loss')
            plt.xlabel('Epoch')
            plt.ylabel('Loss')
            plt.legend()
            plt.grid(True)
            plt.xticks(epochs)

            plt.subplot(1, 2, 2)
            plt.plot(accuracy_list, label='Train Acc')
            plt.plot(val_accuracy_list, '--', label='Val Acc')
            plt.xlabel('Epoch')
            plt.ylabel('Accuracy')
            plt.legend()
            plt.grid(True)
            plt.xticks(epochs)

            plt.show()

if __name__ == '__main__':
    train_data, labels = get_train_data()
    val_data, val_labels = get_validation_data()

    trainer = AlexNetTrainer(num_classes=len(labels), epochs=20, train=True)
    # trainer.train(train_data, val_data)
    # trainer.save_model()
    trainer.show_loss_and_accuracy()
