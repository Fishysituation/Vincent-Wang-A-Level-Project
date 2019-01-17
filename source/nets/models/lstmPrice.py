"""
lstm network that takes in the 4 data points for the current time step 
"""

import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim


class model(nn.Module):

    def __init__(self, itemSize, input_no=4, hidden_no=10, lstm_layer_no=1, out_no=1):
        super(model, self).__init__()

        self.itemSize = itemSize

        self.hidden_no = hidden_no

        #number of lstm layers
        self.layer_no = lstm_layer_no

        #lstm layer with input_no in features and hidden_no out features
        self.lstm = nn.LSTM(input_no, hidden_no, self.layer_no)
        
        #output layer
        self.linear = nn.Linear(hidden_no, out_no)

        #lstm hidden states
        self.hidden = self.init_hidden()

        self.optimizer = optim.Adam(self.parameters(), lr=0.1)
        self.lossFunc = nn.MSELoss()

    
    def init_hidden(self):
        #init a blank hidden/cell state
        return (torch.zeros(self.layer_no, self.itemSize, self.hidden_no).cuda(),
                torch.zeros(self.layer_no, self.itemSize, self.hidden_no).cuda())
    

    #pass forword one batch
    def forward(self, x):
        outs = []

        lstm_out, self.hidden = self.lstm(x, self.hidden)
        net_out = self.linear(lstm_out) 

        for i in range(0, len(net_out)):
            predictions = net_out[i]
            outs.append(predictions[-1])

        return torch.stack(outs)
