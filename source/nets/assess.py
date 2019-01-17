"""
asses a trained network's ability on unseen data 
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

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



def testNetwork(net, inputs, targets, lstm=False, price=False):

    net.eval()

    #if the lstm network
    if lstm:
        #clear the hidden/cell states
        net.hidden = net.init_hidden()

    out = net(inputs)

    lossFunc = nn.MSELoss()
    loss = lossFunc(out, targets)

    #percentageError = calculatePercentage(prediction, expected)
    meanSquaredError = loss.item()


    if price:
        print("Correctly predicted within the spread: " + str(calculatePercentagePrice(out, targets)))
        print("Mean squared error: " + str(loss.item()) + "\n")
    else:
        _, prediction = out.max(1)
        _, expected = targets.max(1)
    
        print("Percentage correct: " + str(calculatePercentage(prediction, expected)))
        print("Mean squared error: " + str(loss.item()) + "\n")

    #return percentageError, meanSquaredError

