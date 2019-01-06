"""
put data into correct form for network input/target outputs
"""


import torch
from torch import autograd


typicalSpread = 0.00007
dataPath = "data/overfit.txt"


def readIn():
    toReturn = []

    with open(dataPath, 'r') as file:
        #skip header line
        next(file)
        for line in file:
            ohlc = line.split(',')[1:-1]
            toReturn.append([float(x) for x in ohlc])
    
    return toReturn


def getData(batchSize, noPrev, toPredict, conv=True):
    
    #read data in from 
    data = readIn()

    batch = []
    targets = [] 

    #for each item in batch
    for i in range(0, batchSize):

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
            batch.append([o, h, l, c])

        else:
            item = []
            for j in range(i, i+noPrev):
                localOpen = data[j][0]
                item.append(data[j][0] - finalClose)
                item.append(data[j][1] - localOpen)
                item.append(data[j][2] - localOpen)
                item.append(data[j][3] - finalClose)
            batch.append([o, h, l, c])


        target = []

        value = data[i+noPrev+toPredict][3] - finalClose
        if value >= typicalSpread:
            target.append([1, 0, 0])
        elif value <= -(typicalSpread):
            target.append([0, 0, 1])
        else:
            target.append([0, 1, 0])

        targets.append(target)

    #return batch and targets as autograd variables 
    return autograd.Variable(torch.tensor(batch)*1000), autograd.Variable(torch.tensor(targets).float())

