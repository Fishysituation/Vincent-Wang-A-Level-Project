
import process
import train
import models.lstmPrice
import assess

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim


windowSize = 20
lstmNo = 10
lstmLayerNo = 1
timestepToPredict = 1

loadOld = True

outPath = "trainedNets/{}-{}-{}-{}.pth".format(timestepToPredict*15, windowSize, lstmNo, lstmLayerNo)

#get all testing/training data
trainMe, testMe, trainIn, testIn, trainTa, testTa = process.get(windowSize, timestepToPredict, "data/OHLC15.csv")

net = models.lstmPrice.model(windowSize, hidden_no=lstmNo, lstm_layer_no=lstmLayerNo, learning_rate=0.01)
net = net.cuda()

if loadOld:
    net.load_state_dict(torch.load(outPath))

#assess the network
assess.testNetwork(net, testIn, testTa, testMe, windowSize, plot=True)

input()

train.iterate(net, trainMe, trainIn, trainTa, windowSize, 100)

#assess the network
assess.testNetwork(net, testIn, testTa, testMe, windowSize, plot=True)

if loadOld:
    a = input("save new? ")
    if a == 'y':
        #save the model's state
        torch.save(net.state_dict(), outPath)

else:
    #save the model's state
    torch.save(net.state_dict(), outPath)