"""
asses a trained network's ability on unseen data 
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import matplotlib.pyplot as plt
import numpy as np

typicalSpread = 0.00007



def calculatePercentage(prediction, expected):
    correct = 0
    for i in range(0, len(prediction)):
        if prediction[i] == expected[i]:
            correct += 1
    return correct/len(prediction) * 100


def calculatePercentagePrice(prediction, expected):
    correct = 0
    for i in range(0, len(prediction)):
        if prediction[i] - expected[i] < typicalSpread*100:
            correct += 1
    return correct/len(prediction) * 100



def testNetwork(net, inputs, targets, means=None, plot=True):

    net.eval()

    #clear the hidden/cell states
    net.hidden = net.init_hidden()

    out = net(inputs)

    lossFunc = nn.MSELoss()
    loss = lossFunc(out, targets)

    #percentageError = calculatePercentage(prediction, expected)
    meanSquaredError = loss.item()


    print("Correctly predicted within the spread: " + str(calculatePercentagePrice(out, targets)))
    print("Mean squared error: " + str(loss.item()) + "\n")

    
    if plot:
        plotPredictions(out/100 + means, targets/100 + means)


    #return percentageError, meanSquaredError



def plotPredictions(out, targets):
    toPlot = 200
    start = 450
    
    out = out[start:start+toPlot].view(toPlot).detach().cpu().numpy()
    targets = targets[start:start+toPlot].view(toPlot).detach().cpu().numpy()
    
    plt.plot(targets)
    plt.plot(out)
    plt.show()
