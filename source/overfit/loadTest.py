import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

"""
Test for loading in a trained network and assessing performance
Load in best network from the produced 
"""

batchSize = 20
timesteps = 24
noEpochs = 2000

typicalSpread = 0.00007

toPredict = 1

modelPath = "testModel.pth"

class model(nn.Module):
    
    def __init__(self, input_no, h1_no, out_no=3):
        super().__init__()
        self.c1 = nn.Conv1d(4, 2, 1)
        self.c2 = nn.Conv1d(2, 1, 1)
        self.h1 = nn.Linear(h1_no, 64)
        self.h2 = nn.Linear(64, 16)
        self.out = nn.Linear(16, out_no)

    def forward(self, x):
        x = F.relu(self.c1(x))
        x = F.relu(self.c2(x))
        x = F.relu(self.h1(x))
        x = F.relu(self.h2(x))
        x = F.relu(self.out(x))
        x = F.softmax(x, dim=2)
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


def getData(noPrev, toPredict):
    
    data = readIn()

    batch = []
    targets = [] 

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


        target = []

        value = data[i+noPrev+toPredict][3] - finalClose
        if value >= typicalSpread:
            target.append([1, 0, 0])
        elif value <= -(typicalSpread):
            target.append([0, 0, 1])
        else:
            target.append([0, 1, 0])

        batch.append([o,h,l,c])
        targets.append(target)

    return autograd.Variable(torch.tensor(batch)*1000), autograd.Variable(torch.tensor(targets).float())


def calculatePercentage(prediction, expected):
    correct = 0
    for i in range(0, len(prediction)):
        if prediction[i] == expected[i]:
            correct += 1
    return correct/len(prediction) * 100



net = model(timesteps*4, timesteps)
net.load_state_dict(torch.load(modelPath))
net.cuda()
net.eval()

#get data from previous timesteps + the target for the prediction
batch, targets = getData(timesteps, toPredict)

#move to gpu
batch = batch.cuda()
targets = targets.cuda()


out = net(batch)

_, prediction = out.max(2)
_, expected = targets.max(2)

lossFunc = nn.MSELoss()
loss = lossFunc(out, targets)
loss.backward()


print("Percentage correct: " + str(calculatePercentage(prediction, expected)))
print("Mean squared error: " + str(loss.item()))
