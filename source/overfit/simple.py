import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

"""
network with one hidden layer
looks at previous 4 timesteps
"""

batchSize = 5
timesteps = 4
typicalSpread = 0.00007

toPredict = [1]

class model(nn.Module):
    
    def __init__(self, input_no, h1_no, h2_no=4, out_no=len(toPredict)*3):
        super().__init__()
        self.h1 = nn.Conv1d(4, 1, 1)
        self.h2 = nn.Linear(int(input_no/4), h2_no)
        self.out = nn.Linear(h2_no, out_no)

    def forward(self, x):
        x = F.relu(self.h1(x))
        x = F.relu(self.h2(x))
        x = F.relu(self.out(x))
        x = F.softmax(x, dim=2)
        return x


def process():
    dataPath = "overfit.txt"
    toReturn = []

    with open(dataPath, 'r') as file:
        #skip header line
        next(file)
        for line in file:
            ohlc = line.split(',')[1:-1]
            toReturn.append([float(x) for x in ohlc])
    
    return toReturn


def getData(noPrev, listPred):
    
    data = process()

    batch = []
    target = [] 

    #for each item in batch
    for i in range(0, batchSize):

        #"rotate" data so it can be convolved
        o, h, l, c = [], [], [], []
        for j in range(i, i+noPrev):
            o.append(data[j][0])
            h.append(data[j][1])
            l.append(data[j][2])
            c.append(data[j][3])

        current = data[i+noPrev-1][3]
        targets = []
        for j in range(0, len(listPred)):
            value = data[i+noPrev+listPred[j]][3] - current
            if value >= typicalSpread:
                targets.append(0)
            elif value <= -(typicalSpread):
                targets.append(2)
            else:
                targets.append(1)

        batch.append([o,h,l,c])
        target.append(targets)

    return autograd.Variable(torch.tensor(batch)), autograd.Variable(torch.tensor(target))




net = model(timesteps*4, timesteps)
optimizer = optim.SGD(net.parameters(), lr=0.01)


#get data from 4 timesteps + the target for the prediction
batch, target = getData(timesteps, toPredict)


for i in range(0, 10000):
    out = net(batch)
    _, results = out.max(2)

    net.zero_grad()
    optimizer.zero_grad()

    lossFunc = nn.MSELoss()
    loss = lossFunc(out, target.float())
    
    loss.backward()
    
    if i%500 == 0:
        print("target\t", str(target.view(1, -1)))
        print("pred.\t", str(results.view(1, -1)))
        print(loss)

    optimizer.step()
