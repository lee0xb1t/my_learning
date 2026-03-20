import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image


class Fruit30Dataset(Dataset):
    def __init__(self, path, train=True):
        self.train = train
        if train:
            path = os.path.join(path, 'train')
        else:
            path = os.path.join(path, 'val')

        self.path = path

        self.data = []
        self.data_labels = []
        self.labels = []

        self.subdir = os.listdir(path)
        self.labels = self.subdir

        for subpath in self.subdir:
            images = os.listdir(os.path.join(path, subpath))
            for image in images:
                self.data.append(os.path.join(path, subpath, image))
                self.data_labels.append(subpath)

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        path = self.data[idx]
        label_ = self.labels.index(self.data_labels[idx])
        with open(path, 'rb') as f:
            image = Image.open(f).convert('RGB')
            trans = self.transform(image)
            return trans, label_


def get_train_data():
    dataset = Fruit30Dataset(
        path='./data/fruit30',
        train=True,
    )
    train_data_ = DataLoader(dataset, batch_size=256, shuffle=True)
    return train_data_, dataset.labels

def get_validation_data():
    dataset = Fruit30Dataset(
        path='./data/fruit30',
        train=False,
    )
    data_ = DataLoader(dataset, batch_size=256, shuffle=False)
    return data_, dataset.labels


if __name__ == '__main__':
    dataset = Fruit30Dataset('./data/fruit30', train=True)
    dataloader, labels = get_train_data()
    for step, (data, label) in enumerate(dataloader):
        print(data.shape)
        print(label.shape)
        break
    dataloader, labels = get_validation_data()
    for step, (data, label) in enumerate(dataloader):
        print(data.shape)
        print(label.shape)
        break
