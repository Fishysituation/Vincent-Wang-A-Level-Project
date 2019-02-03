"""
asses a trained network's ability on unseen data 
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import matplotlib.pyplot as plt
import numpy as np

import process

typicalSpread = 0.00007


def calculatePercentage(prediction, raw):
    correct = 0
    startRaw = len(raw) - len(prediction)

    for i in range(0, len(prediction)-1):
        #if between the high and low
        if (prediction[i] < raw[startRaw + i + 1][1] and 
            prediction[i] > raw[startRaw + i + 1][2]):
            correct += 1
    
    return correct/len(prediction) * 100



def testNetwork(net, rawIns, targets, means, windowSize, plot=True):

    inputs = process.prepareInputs(means, rawIns, windowSize)

    net.eval()

    #clear the hidden/cell states
    net.hidden = net.init_hidden()

    out = net(inputs)
    outPrices = out/100 + means


    lossFunc = nn.MSELoss()
    loss = lossFunc(out, (targets-means)*100)

    #percentageError = calculatePercentage(prediction, expected)
    meanSquaredError = loss.item()

    

    print("Correctly predicted within high/low: " + str(calculatePercentage(outPrices, rawIns)))
    print("Mean squared error: " + str(meanSquaredError) + "\n")

    
    if plot:
        plotPredictions(outPrices, targets)


    #return percentageError, meanSquaredError



def plotPredictions(out, targets):
    toPlot = 50
    start = 100
    
    out = out[start:start+toPlot].view(toPlot).detach().cpu().numpy()
    targets = targets[start:start+toPlot].view(toPlot).detach().cpu().numpy()
    
    plt.plot(targets)
    plt.plot(out)
    plt.show()
