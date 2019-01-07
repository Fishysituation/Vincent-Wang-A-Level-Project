"""
train network for given number of epochs
"""


import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import process


def iterate(net, inputs, targets, noEpochs):

    net.train()

    for j in range(0, noEpochs):
        
        #get batch
        batchIn, batchTa = process.getBatch(inputs, targets)
    
        out = net(batchIn)

        net.zero_grad()
        net.optimizer.zero_grad()

        loss = net.lossFunc(out, batchTa)
        loss.backward()

        net.optimizer.step()

        if j > 0 and j % 100 == 0:
            print("iteration: " + str(j) +  " Loss: " + str(loss.item()))
            
            if j == 500 and loss > 0.2:
                print("stopped training model\n")
                break

            elif j == 1000 and loss > 0.18:
                print("stopped training model\n")
                break

    return net