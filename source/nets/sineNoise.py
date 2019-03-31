import numpy as np
import matplotlib.pyplot as plt
import math
import random as r

outpath = "data/sineNoise.csv"

origin = 1.4

timesteps = 200

#use a sine function to get the closeprices for a number of timesteps
close = []
for i in range(0, timesteps+1):
    close.append(origin + 0.15*(math.sin(0.04*i))+ 0.001*r.randint(-5,5))

#get the open, high, low prices from the close price
openP = close[:timesteps]
close = np.asarray(close)[1:]
high = (close + 0.005)
low = (close - 0.005)

#write data to csv
f = open(outpath, 'w')
for i in range(0, timesteps):
    string = "-,{},{},{},{},-\n".format(openP[i], high[i], low[i], close[i])
    f.write(string)

f.close()

#plot the data
plt.plot(high)
plt.plot(low)
plt.plot(close)
plt.show()

