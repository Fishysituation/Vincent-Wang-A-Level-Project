"""
Load in best network produced by train.py
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import process
import models.convModel


batchSize = 20
timesteps = 24

toPredict = 1

modelPath = "trainedNets/testModel15.pth"


def calculatePercentage(prediction, expected):
    correct = 0
    for i in range(0, len(prediction)):
        if prediction[i] == expected[i]:
            correct += 1
    return correct/len(prediction) * 100


net = models.convModel.model(timesteps*4, timesteps)
net.load_state_dict(torch.load(modelPath))
net.cuda()
net.eval()

#get data from previous timesteps + the target for the prediction
batch, targets = process.getData(batchSize, timesteps, toPredict)

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
