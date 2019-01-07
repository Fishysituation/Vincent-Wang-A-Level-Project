"""
train multiple of the same network
save the one which achieves the smallest loss 
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import process
import assess
import train

import models.convModel


noPrev = 24
noEpochs = 2000
toPredict = 1

dataPath = "data/OHLC15.csv"
#proportion of the training data to give the network eac=
batchProp = 0.1

noModels = 15
largestPercent = 0
smallestLoss = 1
bestModelPercent = None
bestModelLoss = None
outPathPercent = "trainedNets/testLoss.pth"
outPathLoss = "trainedNets/testPercent.pth"


#split to testing/training data
trainIn, trainTa, testIn, testTa = process.get(noPrev, toPredict, dataPath)


#run multiple models
for i in range(0, noModels):

    #init network
    net = models.convModel.model(noPrev*4, noPrev)

    #move net to gpu
    net = net.cuda()


    print("Training model: " + str(i))

    #train the network
    net = train.iterate(net, trainIn, trainTa, noEpochs)


    print("Finished training.\nTesting Network...")    

    #assess the network
    percentage, meanSquared = assess.testNetwork(net, testIn, testTa)

    #choose best model based off percentage correct
    if percentage > largestPercent:
        largestPercent = percentage
        bestModelPercent = net.state_dict()

    #choose best model based off smallest loss
    if meanSquared < smallestLoss:
        smallestLoss = meanSquared
        bestModelLoss = net.state_dict()


print("Best network off percentage had success of: " + str(largestPercent) + " on unseen data")
print("Best network off loss had success of: " + str(smallestLoss) + " on unseen data")


torch.save(bestModelLoss, outPathLoss)
torch.save(bestModelPercent, outPathPercent)
