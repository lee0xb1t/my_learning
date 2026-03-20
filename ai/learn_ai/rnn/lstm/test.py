from train import *


if __name__ == '__main__':
    sequence_length = 96
    epochs = 20

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    transformer = StandardScaler()

    dataset = LoadDataset('./data/Load_Forcast.xlsx', '用电量', sequence_length, device, transformer)

    trainer = LoadTrainer('./data', epochs, device, False)

    trainer.load_model()


    dataset_ = pd.read_excel('./data/Load_Forcast_test.xlsx', '用电量', index_col=(0, 1, 2))
    dataset_ = dataset_.fillna(0)
    dataset_ = np.array(dataset_)
    data = dataset_.reshape(-1, 1)

    pred_list = []
    real_list = []

    X, y = [], []
    for i in range(len(data) - sequence_length):
        X = data[i: i+sequence_length]
        y = data[i+sequence_length].squeeze()
        y_pred = trainer.eval(X, transformer)

        real_list.append(y)
        pred_list.append(y_pred)


    plt.subplot(1, 1, 1)
    plt.plot(real_list, label='Real Values')
    plt.plot(pred_list, '--', label='Predicted Values')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)

    plt.show()

