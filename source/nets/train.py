"""
train multiple of the same network
save the one which achieves the smallest loss 
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim
import process

import models.convModel


batchSize = 20
timesteps = 24
noEpochs = 100

toPredict = 1

smallestLoss = 1 
bestModel = None
outPath = "trainedNets/test.pth"

#get data from previous timesteps + the target for the prediction
batch, targets = process.getData(batchSize, timesteps, toPredict)

#move to gpu
batch = batch.cuda()
targets = targets.cuda()


#run multiple models
for i in range(0, 50):

    print("Training model: " + str(i))

    #init network
    net = models.convModel.model(timesteps*4, timesteps)

    #move net to gpu
    net = net.cuda()
    #set to training mode
    net.train()

    for j in range(0, noEpochs):
        out = net(batch)

        net.zero_grad()
        net.optimizer.zero_grad()

        loss = net.lossFunc(out, targets)
        loss.backward()

        net.optimizer.step()

        #if on the final iteration of optimisation
        if j == noEpochs - 1:

            print("Final loss of: " + str(loss.item()) + "\n")
            if loss < smallestLoss:
                smallestLoss = loss
                bestModel = net.state_dict()
    

print("Best model had loss of: " + str(smallestLoss.item()))
torch.save(bestModel, outPath)
