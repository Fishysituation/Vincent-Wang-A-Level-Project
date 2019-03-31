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


#calculate the precentage of predictions within the actual high/low price
def calculatePercentage(prediction, raw):
    correct = 0
    startRaw = len(raw) - len(prediction)

    for i in range(0, len(prediction)-1):
        #if between the high and low
        if (prediction[i] < raw[startRaw + i + 1][1] and 
            prediction[i] > raw[startRaw + i + 1][2]):
            correct += 1
    
    return correct/len(prediction) * 100


#return the close price of each timestep
def getClosePrices(inputs):
    toReturn = []
    for i in range(0, len(inputs)):
        toReturn.append(torch.tensor([inputs[i][-1][3]]))
    return torch.stack(toReturn).cuda()


#main function, assess and graph the predictions
def testNetwork(net, rawIns, targets, means, windowSize, plot=True):

    inputs = process.prepareInputs(means, rawIns, windowSize)

    net.eval()

    #clear the hidden/cell states
    net.hidden = net.init_hidden()

    #get the network outputs and the last close price of each batch
    out = net(inputs)
    mostRecentClosePrices = getClosePrices(inputs)


    print("Predictions:")
    lossFunc = nn.MSELoss()
    loss1 = lossFunc(out, (targets-means)*100)

    #percentageError = calculatePercentage(prediction, expected)
    meanSquaredError = loss1.item()

    print("Correctly predicted within high/low: " + str(calculatePercentage(out/100 + means, rawIns)))
    print("Mean squared error: " + str(meanSquaredError) + "\n")

        
    print("Most recent close price")
    loss2 = lossFunc(mostRecentClosePrices, (targets-means)*100)
    meanSquaredError = loss2.item()

    print("Correctly predicted within high/low: " + str(calculatePercentage(mostRecentClosePrices/100 + means, rawIns)))
    print("Mean squared error: " + str(meanSquaredError) + "\n")


    if plot:
        plotPredictions(out/100 + means, targets)


    #return percentageError, meanSquaredError


#graph a sample of predictions vs the actual prices
def plotPredictions(out, targets):
    toPlot = 200
    start = 100
    
    #change the pytorch tensors to numpy arrays for matplotlib
    out = out[start:start+toPlot].view(toPlot).detach().cpu().numpy()
    targets = targets[start:start+toPlot].view(toPlot).detach().cpu().numpy()
    
    plt.plot(targets)
    plt.plot(out)
    plt.show()
