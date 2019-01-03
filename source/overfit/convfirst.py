import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

"""
attempt 2 - feed network better inputs: 

take relative values of prices
 - open/close pricing values taken relative to most recent close price
 - high/low taken relative to the open price of each timestep

order of magnitude
 - changes in price are on the order of magnitude of pips (10^-4)
   - multiply relative values by 1000 so that inputs stay (mostly) within [-1, 1]
"""

batchSize = 20
timesteps = 24
typicalSpread = 0.00007

toPredict = [2]

class model(nn.Module):
    
    def __init__(self, input_no, h1_no, out_no=len(toPredict)*3):
        super().__init__()
        self.c1 = nn.Conv1d(4, 2, 1)
        self.c2 = nn.Conv1d(2, 1, 1)
        self.h1 = nn.Linear(h1_no, 64)
        self.h2 = nn.Linear(64, 16)
        self.out = nn.Linear(16, out_no)

    def forward(self, x):
        print("\n")
        x = F.relu(self.c1(x))
        #print(x)
        x = F.relu(self.c2(x))
        #print(x)
        x = F.relu(self.h1(x))
        #print(x)
        x = F.relu(self.h2(x))
        x = F.relu(self.out(x))
        x = F.softmax(x, dim=2)
        print(x)
        return x


def readIn():
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
    
    data = readIn()

    batch = []
    target = [] 

    #for each item in batch
    for i in range(0, batchSize):

        #most recent close price
        finalClose = data[i+noPrev-1][3]

        #"rotate" data so it can be convolved
        o, h, l, c = [], [], [], []
        for j in range(i, i+noPrev):
            localOpen = data[j][0]
            o.append(data[j][0] - finalClose)
            h.append(data[j][1] - localOpen)
            l.append(data[j][2] - localOpen)
            c.append(data[j][3] - finalClose)


        targets = []
        for j in range(0, len(listPred)):
            value = data[i+noPrev+listPred[j]][3] - finalClose
            if value >= typicalSpread:
                targets.append([1, 0, 0])
            elif value <= -(typicalSpread):
                targets.append([0, 0, 1])
            else:
                targets.append([0, 1, 0])

        batch.append([o,h,l,c])
        target.append(targets)

    return autograd.Variable(torch.tensor(batch)*1000), autograd.Variable(torch.tensor(target))




net = model(timesteps*4, timesteps)
optimizer = optim.Adam(net.parameters(), lr=0.002)


#get data from 4 timesteps + the target for the prediction
batch, target = getData(timesteps, toPredict)

print(batch)
print(target.max(2)[1].view(1, -1))

out = net(batch)
print(out.view(1, -1))


for i in range(0, 20000):
    out = net(batch)
    _, results = out.max(2)

    net.zero_grad()
    optimizer.zero_grad()

    lossFunc = nn.MSELoss()
    loss = lossFunc(out, target.float())
    
    loss.backward()
    
    if i%2000 == 0:
        #input()
        print()
        print("target\t", str(target.max(2)[1].view(1, -1)))
        print("pred.\t", str(results.view(1, -1)))
        print(loss)
        input()


    optimizer.step()
