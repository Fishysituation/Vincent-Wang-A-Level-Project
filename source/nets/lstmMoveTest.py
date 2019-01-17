
import process
import train
import models.lstmMove
import assess

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim


window = 20
timestepToPredict = 1

#split to testing/training data
_, _, trainIn, testIn, trainTa, testTa  = process.get(window, timestepToPredict, "data/OHLC15sample.csv", price=False)

print(trainIn)
print(trainTa)

net = models.lstmMove.model(window)
net = net.cuda()

#assess the network
#assess.testNetwork(net, testIn, testTa)

"""
train.iterate(net, trainIn, trainTa, 5000, lstm=True)


#assess the network
assess.testNetwork(net, testIn, testTa, lstm=True)
"""