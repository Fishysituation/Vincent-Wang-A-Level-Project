"""
put data into correct form for network input/target outputs
"""

import torch
from torch import autograd
import random as r



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

    #for each window in the data
    for i in range(0, len(data) - noPrev - toPredict + 1):
        #take the close price
        targets.append([data[i+noPrev+toPredict-1][-1]])

    return autograd.Variable(torch.tensor(targets).float())



def getMeans(noPrev, toPredict, data):

    means = []

    localTotal = 0
    
    #get the total of the first window
    for i in range(0, noPrev - 1):
        localTotal += data[i][-1]

    #for each window in the data
    for i in range(0, len(data) - noPrev - toPredict + 1):
        #move the current window across 1
        if i > 0:
            localTotal -= data[i-1][-1]
        localTotal += data[i+noPrev-1][-1]

        means.append([localTotal/noPrev])

    return autograd.Variable(torch.tensor(means).float())



def getInputs(noPrev, toPredict, data):
    return autograd.Variable(torch.tensor(data[:len(data)-toPredict]))



def prepareInputs(means, inputs, noPrev):
    
    batchIn = []

    #for each window
    for i in range(0, len(inputs) - noPrev + 1):
        window = []
        for j in range(i, i+noPrev):
            window.append(inputs[j] - means[i])

        batchIn.append(torch.stack(window))
    
    return torch.stack(batchIn) * 100



def getBatch(means, inputs, targets, noPrev):
    #take a proportion of the training data
    batchProp = 0.05
    length = int(len(means)*batchProp)
    startIndex = r.randint(0, len(means) - length)

    splitStart = split(startIndex, means, inputs, targets, noPrev)
    
    #pass the latter halves of the split into another split
    splitEnd = split(length, splitStart[1], splitStart[3], splitStart[5], noPrev)

    batchMeans = splitEnd[0]
    batchIns =  prepareInputs(batchMeans, splitEnd[2], noPrev)
    batchTargets = (splitEnd[4]-batchMeans)*100

    #batchIns, batchTargets are "normalised"
    return batchIns, batchTargets



def splitData(means, inputs, targets, noPrev):
    #split data into training/testing
    splitProp = 0.8
    splitIndex = int(len(means)*splitProp)

    return split(splitIndex, means, inputs, targets, noPrev)



def get(noPrev, toPredict, dataPath):
    #get all data

    data = readIn(dataPath)

    inputs = getInputs(noPrev, toPredict, data)
    targets = getTargets(noPrev, toPredict, data)    
    means = getMeans(noPrev, toPredict, data) 

    #move to GPU
    inputs = inputs.cuda()
    targets = targets.cuda()
    means = means.cuda()
    
    return splitData(means, inputs, targets, noPrev)



def split(windowNo, means, inputs, targets, noPrev):
    return means[:windowNo], means[windowNo:], inputs[:windowNo+noPrev-1], inputs[windowNo:], targets[:windowNo], targets[windowNo:]


"""
noPrev = 10
toPredict = 1
dataPath = "data/overfit.csv"

means, _, inputs, _, targets, _ = get(noPrev, toPredict, dataPath)

print(inputs)
print(means.view(1, len(means)))
print(targets.view(1, len(targets)))

m1, m2, i1, i2, t1, t2 = split(4, means, inputs, targets, noPrev)

print(m1)
print(m2)
print(i1)
print(i2)
print(t1)
print(t2)

returnI = prepareInputs(means, inputs, noPrev)
print(inputs)
print(returnI)

batchMe, batchIn, batchTa = getBatch(means, inputs, targets, noPrev)

print(batchMe)
print(batchIn)
print(batchTa)
"""
