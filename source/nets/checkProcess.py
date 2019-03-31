import process

windowSize = 3
timestepToPredict = 2

#get all data from twentyLines.csv
trainMe, testMe, trainIn, testIn, trainTa, testTa = process.get(windowSize, timestepToPredict, "data/twentyLines.csv")

#output each tensor returned
print("Training means: {}".format(len(trainMe)))
print("Testing means: {}\n".format(len(testMe)))

print("Training inputs: {}, {}".format(len(trainIn), trainIn))
print("Testing inputs: {}, {}\n".format(len(testIn), testIn))

print("Training targets: {}, {}".format(len(trainTa), trainTa))
print("Testing targets: {}, {}\n\n".format(len(testTa), testTa))

#use the returned data to retrieve a batch
batchIn, batchTa = process.getBatch(testMe, testIn, testTa, windowSize)

#output the batch
print("Batch Inputs: {}".format(batchIn))
print("Batch Targets: {}".format(batchTa))
