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



def getPredictionTargets(noPrev, toPredict, data):

    targets = []

    #for each item in datafile
    for i in range(0, len(data) - noPrev - toPredict):
        #take the close price
        targets.append([data[i+noPrev+toPredict][-1]])

    return autograd.Variable(torch.tensor(targets).float())



def getLSTMProcessed(noPrev, toPredict, data):
    #separate into the inputs for one feedForward run
    inputs = []
    means = []

    for i in range(0, len(data) - noPrev - toPredict):
        total = 0
        temp = []

        for j in range(i, i+noPrev):
            temp.append(data[j])
            total += data[j][-1]

        #"normalise"
        mean = total/noPrev
        means.append(torch.tensor([mean]))
        normalised = []

        for x in range(0, len(temp)):
            ohlcNorm = []
            for y in range(0, len(temp[x])):
                ohlcNorm.append(temp[x][y]-mean)
            normalised.append(ohlcNorm)

        inputs.append(normalised)
    return torch.stack(means), autograd.Variable((torch.tensor(inputs))*100)



def getBatch(inputs, targets):
    #take a proportion of the training data
    batchProp = 0.2
    length = int(len(inputs)*batchProp)
    startIndex = r.randint(0, len(inputs) - length)
    return inputs[startIndex:startIndex+length], targets[startIndex:startIndex+length]



def splitData(tensor):
    #split data into training/testing
    splitProp = 0.8
    splitIndex = int(len(tensor)*splitProp)

    return tensor[:splitIndex], tensor[splitIndex:]



def get(noPrev, toPredict, dataPath):
    #get data from previous timesteps + the target for the prediction

    data = readIn(dataPath)

    means, inputs = getLSTMProcessed(noPrev, toPredict, data)
    targets = getPredictionTargets(noPrev, toPredict, data)    

    #move to GPU
    inputs = inputs.cuda()
    targets = targets.cuda()
    means = means.cuda()

    meansSep = splitData(means)
    insSep = splitData(inputs)
    targetSep = splitData(targets)

    return meansSep[0], meansSep[1], insSep[0], insSep[1], targetSep[0], targetSep[1]



def getRandom(inputs, targets, length):
    #return random sample 
    startIndex = r.randint(0, len(inputs) - length)
    return inputs[startIndex:startIndex+length], targets[startIndex:startIndex+length]

