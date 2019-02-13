import datetime, threading, time
import json, requests
from flask import Blueprint

import jsonPredictions

from app import db
from models import prediction

jsonPath = 'static/json/'
predictionsFile = 'predictions.json'

alphaVantageDataFile = 'data.json'
alphaVantageKey = "2XFPRGYPL0RM2GQ8"
alphaVantageURL = "https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=15min&outputsize=compact&apikey="

purgeDays = 1


update = Blueprint('update', __name__)


def returnPrevious():
    print('API Call failed...')
    print('Serving the last valid data file')

    with open(jsonPath + alphaVantageDataFile, 'r') as f:
        data = json.load(f)
        return data


#update data.json, return the time of the data sent
def getPriceData(): 
    api_url = alphaVantageURL + alphaVantageKey

    try:
        response = requests.get(api_url)
    except: 
        return returnPrevious

    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))

        for key in data.keys():
            #if error message returned
            if key == 'Error Message' or key == "Note:":
                return returnPrevious()

        print("Get successful.")
        with open(jsonPath + alphaVantageDataFile, 'w') as f:
            json.dump(data, f, indent=4)
        return data



def savePredictions(time, predictions):
    #write predictions to database
    print("Saving Predictions")

    #create instance of prediction class
    pred = prediction(
        dateTime = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S"),
        pred15 = predictions[0],
        pred30 = predictions[1],
        pred60 = predictions[2],
        pred120 = predictions[3],
        pred240 = predictions[4],
        pred480 = predictions[5],
    )
    
    #write to database
    db.session.add(pred)
    db.session.commit()


#return datetime.datetime object
def getDateTime(timeString):
    return datetime.datetime.strptime(timeString, "%Y-%m-%d %H:%M:%S")


def getDateString(dateTime):
    return datetime.datetime.strftime(dateTime, "%Y-%m-%d %H:%M:%S")


def retrievePrediction(entry, timestep):
    if timestep == 1:
        return entry.pred15
    elif timestep == 2:
        return entry.pred30 
    elif timestep == 4:
        return entry.pred60
    elif timestep == 8: 
        return entry.pred120
    elif timestep == 16:
        return entry.pred240
    elif timestep == 32: 
        return entry.pred480


def assessPredictions(priceData, time, timestep):
    timeNow = getDateTime(time)
    #set the cutoff lookback period to the size of the alphavantage compact period (100 timesteps)
    prevCutoff = timeNow - datetime.timedelta(minutes=15*(99+timestep))
    futureCutoff = timeNow - datetime.timedelta(minutes=15*(timestep))

    #retrieve up to first fifty of those that pass the cutoff
    predictions = prediction.query.filter(
            prediction.dateTime > prevCutoff).filter(
            prediction.dateTime < futureCutoff).order_by(
            prediction.dateTime.desc()).limit(50).all()

    noPredictions = len(predictions)
    
    #return 0 if would return a div 0 error 
    if noPredictions < 2:
        return 0, 0

    totalCorrect = 0
    totalError = 0
    for i in range(0, noPredictions):
        #get the label in the json data with the prediction + offset time
        predTime = getDateString(predictions[i].dateTime + datetime.timedelta(minutes=15*timestep))
        ohlc = priceData[predTime]
        predPrice = retrievePrediction(predictions[i], timestep)

        if predPrice < float(ohlc["2. high"]) and predPrice > float(ohlc["3. low"]):
            totalCorrect += 1
        
        totalError += abs(float(ohlc["2. high"])-predPrice)

    #return percentage correct and unbiased estimate of stdev
    return ((totalCorrect/noPredictions)*100,
            (noPredictions/(noPredictions-1))**0.5 * (totalError/noPredictions))


def getPredictions(time, priceData):
    #check if predictions have already been made for this time
    with open(jsonPath + predictionsFile, 'r') as f:
        data = json.load(f)
        predictionsTime = data["Meta Data"]["Time"]

    #if not, get new predictions and add a db entry
    if predictionsTime != time:
        print('Getting Predictions...')

        percentages = []
        stdevs = []
        for i in range(0, 7):
            percentage, stdev = assessPredictions(priceData, time, 2**i)
            percentages.append(percentage)
            stdevs.append(stdev)

        predictions = jsonPredictions.predict(time, percentages, stdevs)
        savePredictions(time, predictions)
        print('Done')
    else:
        print("Predictions already made.")


def purge():
    #TODO yeet inactive users 
    #sqlite3 has own datetime functions on strings in correct format x 
    return


@update.before_app_first_request
def activate_job():
    #get latest prices
    print('Getting Prices...')
    firstData = getPriceData()
    firstTime = firstData["Meta Data"]["4. Last Refreshed"]
    #predict based off these 
    getPredictions(firstTime, firstData["Time Series FX (15min)"])

    #run updates in the background
    def update():
        data = getPriceData()
        dataTime = data["Meta Data"]["4. Last Refreshed"]

        check = False
        
        while True:
            #get current time
            current = datetime.datetime.utcnow()
            
            #if new alphaVantage data expected
            if current.minute % 15 == 0: 
                #check for new data
                check = True 
            #if midnight
            if current.hour == 0 and current.minute == 0:
                #remove inactive users
                purge()

            if check:
                print("Checking for new prices...")
                newData = getPriceData()
                newTime = newData["Meta Data"]["4. Last Refreshed"]

                #if prices have updated, stop checking
                if dataTime != newTime:
                    print("Prices updated.")
                    getPredictions(newTime, newData["Time Series FX (15min)"])
                    check = False
                else:
                    print("Prices Not updated...")

            time.sleep(45)

    thread = threading.Thread(target=update)
    thread.start()
