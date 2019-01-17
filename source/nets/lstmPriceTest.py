
import process
import train
import models.lstmPrice
import assess

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim


window = 20
timestepToPredict = 1

#split to testing/training data
trainMe, testMe, trainIn, testIn, trainTa, testTa = process.get(window, timestepToPredict, "data/OHLC15sample.csv", price=True)


trainTa = (trainTa-trainMe)*100
testTa = (testTa-testMe)*100

net = models.lstmPrice.model(window)
net = net.cuda()

#assess the network
assess.testNetwork(net, testIn, testTa, lstm=True, price=True)


train.iterate(net, trainIn, trainTa, 100, lstm=True)


#assess the network
assess.testNetwork(net, testIn, testTa, lstm=True, price=True)
