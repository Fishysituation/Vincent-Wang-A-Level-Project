import numpy as np
import matplotlib.pyplot as plt

origin = 1.4

outpath = "data/dsc.csv"

origin = 1.4
dataRange = 0.2

timesteps = 200

close = []
for i in range(0, timesteps+1):
    close.append(origin + dataRange - i*(dataRange*2)/timesteps)

openP = close[:timesteps]
close = np.asarray(close)[1:]
high = (close + 0.005)
low = (close - 0.005)


f = open(outpath, 'w')
for i in range(0, timesteps):
    string = "-,{},{},{},{},-\n".format(openP[i], high[i], low[i], close[i])
    f.write(string)

f.close()


plt.plot(high)
plt.plot(low)
plt.plot(close)
plt.show()


