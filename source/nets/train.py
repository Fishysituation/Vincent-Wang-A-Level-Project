"""
train network for given number of epochs
"""


import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

import process


def iterate(net, means, inputs, targets, noPrev, noEpochs):

    net.train()

    for j in range(0, noEpochs):
        
        #get batch
        batchIn, batchTa = process.getBatch(means, inputs, targets, noPrev)

        #clear the hidden/cell states
        net.hidden = net.init_hidden()

        #clear the accumulated values in the network and optimiser
        net.zero_grad()
        net.optimizer.zero_grad()
       
        #pass inputs to network
        out = net(batchIn)

        #calculate the loss
        loss = net.lossFunc(out, batchTa)

        #back-propagate
        loss.backward(retain_graph=True)
        net.optimizer.step()


        #display the loss and a sample of the predictions
        if j % 1 == 0:

            print("iteration: " + str(j) +  " Loss: " + str(loss.item()))
            toView = 5
            
            print("target: " + str(batchTa[:toView].view(1, toView)))
            print("predi.: " + str(out[:toView].view(1, toView)))
            
            print()