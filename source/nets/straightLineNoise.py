import numpy as np
import matplotlib.pyplot as plt
import random as r

origin = 1.4

outpath = "data/dscNoise.csv"

origin = 1.4
dataRange = 0.2

timesteps = 200

close = []
for i in range(0, timesteps+1):
    close.append(origin + dataRange - i*(dataRange*2)/timesteps + 0.001*r.randint(-5,5))

openP = close[:timesteps]
close = np.asarray(close)[1:]
high = (close + 0.01)
low = (close - 0.01)


f = open(outpath, 'w')
for i in range(0, timesteps):
    string = "-,{},{},{},{},-\n".format(openP[i], high[i], low[i], close[i])
    f.write(string)

f.close()


plt.plot(high)
plt.plot(low)
plt.plot(close)
plt.show()



