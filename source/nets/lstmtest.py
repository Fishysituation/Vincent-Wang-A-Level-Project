
import process
import train
import models.lstm
import assess

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

meanOverHistoric = 1.2684

window = 20
timestepToPredict = 1

#split to testing/training data
trainIn, trainTa, testIn, testTa = process.get(window, timestepToPredict, "data/OHLC15sample.csv")


net = models.lstm.model(window)
net = net.cuda()

#assess the network
#assess.testNetwork(net, testIn, testTa)


train.iterate(net, trainIn, trainTa, 5000, lstm=True)


#assess the network
assess.testNetwork(net, testIn, testTa, lstm=True)
