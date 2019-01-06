fileIn = "EURUSD_15m_BID_01.01.2010-31.12.2016.csv"
fileOut = "OHLC15.csv"

f = open(fileIn, 'r')
allData = f.readlines()
f.close()

f = open(fileOut, 'w')

for line in allData:
    items = line.split(',')
    if items[-1] != '0\n':
        f.write(line)

f.close()