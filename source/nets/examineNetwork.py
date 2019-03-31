"""
further train a network
look at a network's behaviour 
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import process
import train
import assess
import models.convModel


noPrev = 24
toPredict = 1


dataPath = "data/OHLC15.csv"

networkPath1 = "trainedNets/testLoss.pth"
networkPath2 = "trainedNets/testPercent.pth"

outPath = "trainedNets/testPercent-v2.pth"


#init network
net = models.convModel.model(noPrev*4, noPrev)
#load in saved
net.load_state_dict(torch.load(networkPath2))
net.cuda()


#get all inputs and targets
trainIn, trainTa, testIn, testTa = process.get(noPrev, toPredict, dataPath)


#train more and checkup 
for i in range(0, 5):
    train.iterate(net, trainIn, trainTa, 1000)
    assess.testNetwork(net, testIn, testTa)


torch.save(net, outPath)


#look at a random sample of outputs
for i in range(0, 10):
    sampleIn, sampleTa = process.getRandom(testIn, testTa, 10)

    out = net(sampleIn)
    print(out)
    print(sampleTa)

