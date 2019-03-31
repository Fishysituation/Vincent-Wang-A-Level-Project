"""
train and assess a network for a number of timesteps
"""


import process
import train
import models.lstmPrice
import assess

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim


windowSize = 90
lstmNo = 30
lstmLayerNo = 1
timestepToPredict = 32

loadOld = True


outPath = "trainedNets/{}-{}-{}-{}.pth".format(timestepToPredict*15, windowSize, lstmNo, lstmLayerNo)

#get all testing/training data
trainMe, testMe, trainIn, testIn, trainTa, testTa = process.get(windowSize, timestepToPredict, "data/OHLC15.csv")

net = models.lstmPrice.model(windowSize, hidden_no=lstmNo, lstm_layer_no=lstmLayerNo, learning_rate=0.002)
net = net.cuda()

#load an old network in
if loadOld:
    net.load_state_dict(torch.load(outPath))

#assess the network
assess.testNetwork(net, testIn, testTa, testMe, windowSize, plot=loadOld)

#run the training
train.iterate(net, trainMe, trainIn, trainTa, windowSize, 50)

#assess the network
assess.testNetwork(net, testIn, testTa, testMe, windowSize, plot=True)


#choose whether to save an old network
if loadOld:
    a = input("save new? ")
    if a == 'y':
        #save the model's state
        torch.save(net.state_dict(), outPath)

else:
    #save the model's state
    torch.save(net.state_dict(), outPath)

#assess the network
assess.testNetwork(net, testIn, testTa, testMe, windowSize, plot=True)
    