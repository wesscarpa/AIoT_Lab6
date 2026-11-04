import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

HAR_LABELS = {1: "WALKING", 2: "WALKING_UPSTAIRS", 3: "WALKING_DOWNSTAIRS",
    4: "SITTING", 5: "STANDING", 6: "LAYING"}
    
CHANNEL_SETS = [
    "total_acc_x_{split}.txt",
    "total_acc_y_{split}.txt",
    "total_acc_z_{split}.txt",
    "body_gyro_x_{split}.txt",
    "body_gyro_y_{split}.txt",
    "body_gyro_z_{split}.txt",
]

class UCIHARSignals(Dataset):
    """
    Returns for __getitem__(i):
    x: torch.FloatTensor with shape [C, L] (channels-first for Conv1d)
    y: int in [0..5]
    y_name: str (human-readable)
    """
    def __init__(self, root, split="train"):
        base = Path(root) / split / "Inertial Signals"
        #tODO: load and stack all channels -> [N, C, L]
        channels = []
        for file in CHANNEL_SETS:
            path = base / file.format(split=split)
            data = np.loadtxt(path)
            channels.append(data)
            # print(data)
        x = np.stack(channels, axis=1)
#             N = data.shape[0]
#             C = len(CHANNEL_SETS)
#             L = data.shape[1]
#             x = [N, C, L]
        N, C, L = x.shape
       # print("N: ", N, " C: ", C, " L: ", L)


#         # tODO (optional): normalize per channel; keep raw g for Tasks 2-5
#         ...
        self.x = torch.tensor(x, dtype=torch.float32)
        # load and remap labels to [0...5]
        labels = np.loadtxt(Path(root) / split / f"y_{split}.txt", dtype=int)
        #print(labels)
        #print(len(labels))
        self.y = torch.tensor(labels - 1, dtype=torch.long)
        # y is the normalized version of x
    def __len__(self):
    # return number of samples in dataset
        return len(self.x)
    def __getitem__(self, i):
        # return x tensor, y label, y label name
        x = self.x[i] # -> [C, 128]
        y = int(self.y[i]) # -> scalar in [0..5]
        y_name = HAR_LABELS[y + 1]
        return x, y, y_name

if __name__ == "__main__":
    data_dir = r"human+activity+recognition+using+smartphones\UCI HAR Dataset\UCI HAR Dataset"
    train_loader = DataLoader(UCIHARSignals(data_dir, "train"), batch_size=32, shuffle=True)
    xb, yb, yname = next(iter(train_loader))
    print("x:", xb.shape) # [B, C, L], e.g. [32, 6, 128]
    print("y:", yb.shape) # [B]
    print("names:", yname[:-1])