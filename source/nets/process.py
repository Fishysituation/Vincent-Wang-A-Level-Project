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



def getTargets(noPrev, toPredict, data):

    targets = []

    #for each item in datafile
    for i in range(0, len(data) - noPrev - toPredict):

        #most recent close price
        finalClose = data[i+noPrev-1][3]

        value = data[i+noPrev+toPredict][3] - finalClose
        if value >= typicalSpread:
            targets.append([1, 0, 0])
        elif value <= -(typicalSpread):
            targets.append([0, 0, 1])
        else:
            targets.append([0, 1, 0])

    return autograd.Variable(torch.tensor(targets).float())


def getLSTMProcessed(noPrev, toPredict, data):
    #separate into the inputs for one feedForward run
    inputs = []

    
    for i in range(0, len(data) - noPrev - toPredict):
        total = 0
        temp = []

        for j in range(i, i+noPrev):
            temp.append(data[j])
            total += data[j][-1]

        #"normalise"
        mean = total/noPrev
        normalised = []

        for x in range(0, len(temp)):
            ohlcNorm = []
            for y in range(0, len(temp[x])):
                ohlcNorm.append(temp[x][y]-mean)
            normalised.append(ohlcNorm)

        inputs.append(normalised)

    return autograd.Variable((torch.tensor(inputs))*100)


def getConvProcessed(noPrev, toPredict, data, takeRelative=False):
    
    inputs = []

    #for each item in datafile
    for i in range(0, len(data) - noPrev - toPredict):
        
        #most recent close price
        finalClose = 0 
        
        if takeRelative: 
            finalClose = data[i+noPrev-1][3]

        #"rotate" data so it can be convolved
        o, h, l, c = [], [], [], []
        for j in range(i, i+noPrev):
            
            localOpen = 0
            
            if takeRelative: 
                data[j][0]
                
            o.append(data[j][0] - finalClose)
            h.append(data[j][1] - localOpen)
            l.append(data[j][2] - localOpen)
            c.append(data[j][3] - finalClose)
        inputs.append([o, h, l, c])


    #return inputs and as autograd variable, scale the relative values used
    if takeRelative:
        return autograd.Variable(torch.tensor(inputs)*1000)
    else:
        return autograd.Variable(torch.tensor(inputs))


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


def get(noPrev, toPredict, dataPath, conv=False, raw=False):
    #get data from previous timesteps + the target for the prediction

    data = readIn(dataPath)
    inputs = None

    if conv:
        inputs = getConvProcessed(noPrev, toPredict, data)
    else:
        inputs = getLSTMProcessed(noPrev, toPredict, data)
    
    
    targets = getTargets(noPrev, toPredict, data)    

    #move to GPU
    inputs = inputs.cuda()
    targets = targets.cuda()

    return splitData(inputs, targets)


def getRandom(inputs, targets, length):
    #return random sample 
    startIndex = r.randint(0, len(inputs) - length)
    return inputs[startIndex:startIndex+length], targets[startIndex:startIndex+length]

"""    
trai, trat, testi, test = get(1, 1, "data/OHLC15sample.csv", conv=False, raw=True)
print(trai)
"""