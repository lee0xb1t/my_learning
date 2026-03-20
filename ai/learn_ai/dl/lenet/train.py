import torch
from torchvision.datasets import FashionMNIST
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.functional import F
import torch.optim as optim
import torch.nn as nn
import numpy as np

from model import LeNet


def get_train_data():
    train_dataset = FashionMNIST(
        root="./data",
        train=True,
        download=True,
        transform=transforms.Compose([transforms.ToTensor(), ])
    )

    train_data_ = DataLoader(train_dataset, batch_size=64, shuffle=True)

    return train_data_, train_dataset.classes

class LeNetTrainer:
    def __init__(self, num_classes: int, epochs: int, train: bool = False):
        self.train_mode = train
        self.num_classes = num_classes
        self.epochs = epochs

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if self.train_mode:
            self.model = LeNet(num_classes)
            self.model.to(self.device)
            self.model.train()

            self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.criterion = nn.CrossEntropyLoss()

        self.base_accuracy = 0.0

        self.train_accuracy_list = []
        self.train_loss_list = []

        self.val_accuracy_list = []
        self.val_loss_list = []

        pass

    def _train_batch(self, x_batch_: torch.Tensor, y_batch_: torch.Tensor):
        if self.train_mode:
            self.optimizer.zero_grad()
            logits = self.model(x_batch_)
            loss = self.criterion(logits, y_batch_)
            loss.backward()
            self.optimizer.step()
        else:
            with torch.no_grad():
                logits = self.model(x_batch_)
                loss = self.criterion(logits, y_batch_)

        _train_loss = loss.item()
        _train_prob = F.softmax(logits, dim=1)
        _train_pred = torch.argmax(_train_prob, dim=1)
        _train_accuracy = torch.mean((_train_pred == y_batch_).float()).item()

        return _train_loss, _train_accuracy

    def __mean_loss(self):
        return np.mean(self.train_loss_list)

    def __mean_accuracy(self):
        return np.mean(self.train_accuracy_list)

    def __mean_val_loss(self):
        return np.mean(self.val_loss_list)

    def __mean_val_accuracy(self):
        return np.mean(self.val_accuracy_list)

    def train(self, train_data_: DataLoader):
        if not self.train_mode:
            raise Exception("Current is not training mode")

        for epoch in range(self.epochs):
            for step, (_imgs, _labels) in enumerate(train_data):
                _imgs = _imgs.to(self.device)
                _labels = _labels.to(self.device)
                train_loss, train_accuracy = self._train_batch(_imgs, _labels)

                self.train_accuracy_list.append(train_accuracy)
                self.train_loss_list.append(train_loss)

                if train_accuracy > self.base_accuracy:
                    self.base_accuracy = train_accuracy
                # print("Epoch:{}/{}, Step: {}, Loss: {}, Accuracy: {}".format(epoch+1, self.epochs, step, self.__mean_loss(), self.__mean_accuracy()))

            print("Epoch:{}/{}, Loss: {}, Accuracy: {}, Base Accuracy: {}".format(epoch + 1, self.epochs, self.__mean_loss(),
                                                               self.__mean_accuracy(), self.base_accuracy))
            self.train_accuracy_list = []
            self.train_loss_list = []

    def validation(self, val_data_: DataLoader):
        if self.train_mode:
            raise Exception("Current is training mode")

        self.base_accuracy = 0.0

        for step, (_val_imgs, _val_labels) in enumerate(val_data_):
            _val_imgs = _val_imgs.to(self.device)
            print(_val_imgs.shape)
            _val_labels = _val_labels.to(self.device)
            val_loss, val_accuracy = self._train_batch(_val_imgs, _val_labels)

            self.val_accuracy_list.append(val_accuracy)
            self.val_loss_list.append(val_loss)

            if val_accuracy > self.base_accuracy:
                self.base_accuracy = val_accuracy

        print("[Validate] Loss: {}, Accuracy: {}, Base Accuracy: {}".format( self.__mean_val_loss(), self.__mean_val_accuracy(), self.base_accuracy))

    def eval(self, img):
        img = np.array(img)

        transform = transforms.Compose([transforms.ToTensor(), ])
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


if __name__ == '__main__':
    train_data, labels = get_train_data()

    trainer = LeNetTrainer(num_classes=len(labels), epochs=50, train=True)
    trainer.train(train_data)
    trainer.save_model()
