import process
import train
import models.lstmPrice
import assess

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import matplotlib.pyplot as plt
import matplotlib as mpl 
import numpy as np
from matplotlib.collections import LineCollection


#paths to all the trained networks to be used 
netPaths = ["trainedNets/15-5-20-1.pth", #checked
            "trainedNets/30-10-20-1.pth", #checked
            "trainedNets/60-20-30-1.pth", #checked
            "trainedNets/120-40-30-1.pth", #checked
            "trainedNets/240-65-30-1.pth", #checked
            "trainedNets/480-90-30-1.pth"] #checked


#take in csv data and return pytorch tensor
def getData(path):
    
    with open(path) as f:
        data = f.readlines()

    toReturn = []
    for i in range(0, len(data)):
        ohlc = data[i].split(',')[1:-1]
        toReturn.append([float(x) for x in ohlc])

    #get all past data points in reverse chron. order
    toReturn.reverse()
    return torch.tensor(toReturn)


#just get the close price of each timestep in a list for graphing
def getClose(path):
    with open(path) as f:
        data = f.readlines()

    toReturn = []
    for i in range(0, len(data)):
        ohlc = data[i].split(',')[1:-1]
        toReturn.append(float(ohlc[-1]))

    return toReturn


#get a window for a network
def getSlice(data, steps):
    #calculate mean close price of region
    total = 0
    for i in range(0, steps):
        total += data[100-steps+i][-1].item()
    mean = total/steps

    print(torch.stack([data[-steps]]))

    return (torch.stack([data[-steps:]])-mean)*100, mean


#init a network and load the saved parameters 
def loadNet(path):
    data = path[:-4].split('-')
    net = models.lstmPrice.model(int(data[1]),
                                 hidden_no=int(data[2]), 
                                 lstm_layer_no=int(data[3]), 
                                 useCuda=False)

    net.load_state_dict(torch.load(path))
    return net, int(data[1])


#make the predictions for each network
def predict():

    allData = getData(dataPath)
    toReturn = []

    #get the prediction for each timestep
    for i in range(0, len(netPaths)):
        net, noSteps = loadNet(netPaths[i])
        data, mean = getSlice(allData, noSteps)

        net.init_hidden()
        out = net(data).item()
        prediction = (net(data).item()/100)+mean

        toReturn.append(prediction)

    return toReturn


#graph a sample of predictions vs the actual prices
def plotPredictions(out, targets):
    prev = 100
    
    mpl.style.use('default')

    fig, ax = plt.subplots()

    prediction = [[(prev, targets[-100+(100-prev)])]]
    for i in range(0, len(out)):
        prediction[0].append((prev + 2**i, out[i]))

    print(prediction)
    close = np.asarray(targets[100-prev:100])
    predLine = LineCollection(prediction, colors=['C1'])
    
    ax.plot(close, "C0")
    ax.add_collection(predLine)
    
    plt.xlim((-5, prev+40))
    plt.ylim((1.3, 1.6))

    plt.show()


dataPath = "data/dscNoise.csv"
results = predict()
close = getClose(dataPath)
plotPredictions(results, close)
