"""
Asses a trained network's ability on unseen data 
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import process
import models.convModel


timesteps = 24
toPredict = 1


def calculatePercentage(prediction, expected):
    correct = 0
    for i in range(0, len(prediction)):
        if prediction[i] == expected[i]:
            correct += 1
    return correct/len(prediction) * 100


def testNetwork(net, inputs, targets):

    net.eval()

    out = net(inputs)

    _, prediction = out.max(2)
    _, expected = targets.max(2)

    lossFunc = nn.MSELoss()
    loss = lossFunc(out, targets)

    percentageError = calculatePercentage(prediction, expected)
    meanSquaredError = loss.item()

    print("Percentage correct: " + str(calculatePercentage(prediction, expected)))
    print("Mean squared error: " + str(loss.item()) + "\n")

    return percentageError, meanSquaredError

