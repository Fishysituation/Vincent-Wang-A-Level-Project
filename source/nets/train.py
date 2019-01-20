"""
train network for given number of epochs
"""


import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import process


def iterate(net, inputs, targets, noEpochs, lstm=False):

    net.train()

    for j in range(0, noEpochs):
        
        #get batch
        batchIn, batchTa = process.getBatch(inputs, targets)
        
        #clear the hidden/cell states
        net.hidden = net.init_hidden()

        net.zero_grad()
        net.optimizer.zero_grad()
       
        out = net(batchIn)

        loss = net.lossFunc(out, batchTa)

        net.train()
        loss.backward(retain_graph=True)

        net.optimizer.step()


        if j % 10 == 0:

            print("iteration: " + str(j) +  " Loss: " + str(loss.item()))
            toView = 10
            
            print("target: " + str(batchTa[:toView].view(1, toView)))
            print("predi.: " + str(out[:toView].view(1, toView)))
            
            print()
