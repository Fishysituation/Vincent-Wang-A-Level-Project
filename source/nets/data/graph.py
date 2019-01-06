import matplotlib.pyplot as plt

fileIn = "OHLC15sample.csv"

timeSeries = []
openSeries = []
highSeries = []
lowSeries = []
closeSeries = []

f = open(fileIn, 'r')
allData = f.readlines()
f.close()

for i in range (1, len(allData)):
    items = allData[i].split(',')
    timeSeries.append(items[0])
    openSeries.append(float(items[1]))
    highSeries.append(float(items[2]))
    lowSeries.append(float(items[3]))
    closeSeries.append(float(items[4]))

plt.plot(timeSeries, openSeries)
plt.show()