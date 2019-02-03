import torch

import static.nets.lstmPrice
import json 

netPaths = ["static/nets/15-20-10-1.pth",
            "static/nets/30-30-15-2.pth",
            "static/nets/30-30-15-2.pth",
            "static/nets/30-30-15-2.pth",
            "static/nets/30-30-15-2.pth"]

dataPath = "static/json/data.json"
outPath = "static/json/predictions.json"


def getData(path):
    #get all past data points in reverse chron. order
    with open(path) as f:
        data = json.load(f)["Time Series FX (15min)"]

    toReturn = []
    for _, timestep in data.items():
        ohlc = []
        for _, price in timestep.items():
            ohlc.append(float(price))
        toReturn.append(ohlc)

    toReturn.reverse()
    return torch.tensor(toReturn)


def getSlice(data, steps):
    #calculate mean close price of region
    total = 0
    for i in range(0, steps):
        total += data[100-steps+i][-1].item()
    mean = total/steps

    return (torch.stack([data[-steps:]])-mean)*100, mean


def loadNet(path):
    data = path[:-4].split('-')
    net = static.nets.lstmPrice.model(int(data[1]),
                                 hidden_no=int(data[2]), 
                                 lstm_layer_no=int(data[3]), 
                                 cuda=False)

    net.load_state_dict(torch.load(path))
    return net, int(data[1])


def predict(time):
    #TODO do actually do this properly 
    recentAccuracy = [100, 100, 100, 100, 100]

    allData = getData(dataPath)

    jsonData = {}
    jsonData['Meta Data'] = {}
    jsonData['Meta Data']['Time'] = time
    #to add to 

    jsonData['Meta Data']['Recent Accuracy'] = {}

    jsonData['Predictions'] = {}

    #get the prediction for each timestep
    for i in range(0, len(netPaths)):
        net, noSteps = loadNet(netPaths[i])
        data, mean = getSlice(allData, noSteps)
        
        net.init_hidden()
        out = net(data).item()
        prediction = (net(data).item()/100)+mean

        print(mean)
        print(out)
        print(prediction)
        print()

        key = '+{}mins'.format(15*(2**i))
        jsonData['Meta Data']['Recent Accuracy'][key] = recentAccuracy[i]
        jsonData['Predictions'][key] = prediction

    with open(outPath, 'w') as outfile:
        json.dump(jsonData, outfile, indent=4)

