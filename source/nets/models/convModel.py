"""
feed forward model that convolves ohlc data from each time step

"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim


class model(nn.Module):

    def __init__(self, input_no, h1_no, out_no=3):
        super().__init__()
        self.c1 = nn.Conv1d(4, 2, 1)
        self.c2 = nn.Conv1d(2, 1, 1)
        self.h1 = nn.Linear(h1_no, 64)
        self.h2 = nn.Linear(64, 16)
        self.out = nn.Linear(16, out_no)
        
        self.optimizer = optim.Adam(self.parameters(), lr=0.002)
        self.lossFunc = nn.MSELoss()

    def forward(self, x):
        x = F.relu(self.c1(x))
        x = F.relu(self.c2(x))
        x = F.relu(self.h1(x))
        x = F.relu(self.h2(x))
        x = F.relu(self.out(x))
        x = F.softmax(x, dim=2)
        return x
