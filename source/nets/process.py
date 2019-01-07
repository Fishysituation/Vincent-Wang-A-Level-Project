"""
put data into correct form for network input/target outputs
"""

import torch
from torch import autograd
import random as r

typicalSpread = 0.00007


def readIn(dataPath):
    toReturn = []

    with open(dataPath, 'r') as file:
        #skip header line
        next(file)
        for line in file:
            ohlc = line.split(',')[1:-1]
            toReturn.append([float(x) for x in ohlc])
    
    return toReturn


def getAll(noPrev, toPredict, dataPath, conv=True):
    
    #take ohlc data in from file
    data = readIn(dataPath)

    inputs = []
    targets = [] 

    #for each item in datafile
    for i in range(0, len(data) - noPrev - toPredict):

        #most recent close price
        finalClose = data[i+noPrev-1][3]

        #if network convolves ohlc data
        if conv:
            #"rotate" data so it can be convolved
            o, h, l, c = [], [], [], []
            for j in range(i, i+noPrev):
                localOpen = data[j][0]
                o.append(data[j][0] - finalClose)
                h.append(data[j][1] - localOpen)
                l.append(data[j][2] - localOpen)
                c.append(data[j][3] - finalClose)
            inputs.append([o, h, l, c])

        else:
            item = []
            for j in range(i, i+noPrev):
                localOpen = data[j][0]
                item.append(data[j][0] - finalClose)
                item.append(data[j][1] - localOpen)
                item.append(data[j][2] - localOpen)
                item.append(data[j][3] - finalClose)
            inputs.append([item])


        target = []

        value = data[i+noPrev+toPredict][3] - finalClose
        if value >= typicalSpread:
            target.append([1, 0, 0])
        elif value <= -(typicalSpread):
            target.append([0, 0, 1])
        else:
            target.append([0, 1, 0])

        targets.append(target)

    #return inputs and targets as autograd variables 
    return autograd.Variable(torch.tensor(inputs)*1000), autograd.Variable(torch.tensor(targets).float())



def getBatch(inputs, targets):
    #take a proportion of the training data
    batchProp = 0.1
    length = int(len(inputs)*batchProp)
    startIndex = r.randint(0, len(inputs) - length)
    return inputs[startIndex:startIndex+length], targets[startIndex:startIndex+length]


def splitData(inputs, targets):
    #split data into training/testing
    splitProp = 0.8
    splitIndex = int(len(inputs)*splitProp)

    return (
        inputs[:splitIndex], targets[:splitIndex],
        inputs[splitIndex:], targets[splitIndex:]
    )


def get(noPrev, toPredict, dataPath):
    #get data from previous timesteps + the target for the prediction
    inputs, targets = getAll(noPrev, toPredict, dataPath)

    #move to GPU
    inputs = inputs.cuda()
    targets = targets.cuda()

    return splitData(inputs, targets)
