"""
updates price and prediction data every 15 minutes in the background
"""

import datetime, threading, time
import json, requests
from flask import Blueprint, current_app

import jsonPredictions

import app
from app import db
from models import user, apiRequest, prediction

jsonPath = 'static/json/'
predictionsFile = 'predictions.json'

alphaVantageDataFile = 'data.json'
alphaVantageKey = "2XFPRGYPL0RM2GQ8"
alphaVantageURL = "https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=15min&outputsize=compact&apikey="

purgeDays = 30


update = Blueprint('update', __name__)


#if the api call doesn't return new data, keep the old values
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
        return returnPrevious()

    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))

        for key in data.keys():
            #if error message returned
            if key == 'Error Message' or key == "Note":
                return returnPrevious()

        print("Get successful.")
        with open(jsonPath + alphaVantageDataFile, 'w') as f:
            json.dump(data, f, indent=4)
        return data


#save predictions to database
def savePredictions(time, predictions):
    #write predictions to database
    print("Saving Predictions")

    with app.app.app_context():
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


#get string from a datetime object
def getDateString(dateTime):
    return datetime.datetime.strftime(dateTime, "%Y-%m-%d %H:%M:%S")


#get the correct prediction to compare with the actual value
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


#calculate the recent "percentage accuracies" and standard deviation of each prediction
def assessPredictions(priceData, time, timestep):
    timeNow = getDateTime(time)
    #set the cutoff lookback period to the size of the alphavantage compact period (100 timesteps)
    prevCutoff = timeNow - datetime.timedelta(minutes=15*(99+timestep))
    futureCutoff = timeNow - datetime.timedelta(minutes=15*(timestep))

    #retrieve all predictions that could potentially be evaluated
    with app.app.app_context():
        predictions = prediction.query.filter(
                prediction.dateTime > prevCutoff).filter(
                prediction.dateTime < futureCutoff).order_by(
                prediction.dateTime.desc()).all()

    noPredictions = len(predictions)
    
    #return 0 if would return a div 0 error 
    if noPredictions < 2:
        return 0, 0

    totalCorrect = 0
    totalError = 0
    totalSquaredError = 0
    for i in range(0, noPredictions):
        #get the label in the json data with the prediction + offset time
        predTime = getDateString(predictions[i].dateTime + datetime.timedelta(minutes=15*timestep))
        ohlc = priceData[predTime]
        predPrice = retrievePrediction(predictions[i], timestep)

        if predPrice < float(ohlc["2. high"]) and predPrice > float(ohlc["3. low"]):
            totalCorrect += 1
        
        totalError += abs(float(ohlc["4. close"])-predPrice)
        totalSquaredError += abs(float(ohlc["4. close"])-predPrice)**2

    #return percentage correct and unbiased estimate of stdev
    #unbiased estimate st. dev. ~ (n/n-1 * ((x^2/n)-(x/n)^2)^(1/2)
    return ((totalCorrect/noPredictions)*100,
            (noPredictions/(noPredictions-1))**0.5 * ((totalSquaredError/noPredictions)-(totalError/noPredictions)**2)**0.5)


#make predictions for a set of data
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
        for i in range(0, 6):
            percentage, stdev = assessPredictions(priceData, time, 2**i)
            percentages.append(percentage)
            stdevs.append(stdev)

        predictions = jsonPredictions.predict(time, percentages, stdevs)
        savePredictions(time, predictions)
        print('Done')
    else:
        print("Predictions already made.")


#remove inactive users and get stats
def atMidnight(current):
    #remove inactive users
    noRemoved = purge(current)
    #return stats
    getStats(current, noRemoved)


#remove inactive users
def purge(current):
    #TODO yeet inactive users 
    #look at api rejection of requests to get the right things  
    #for each
    
    #get list of all users
    print("\nRemoving inactive users...")
    count = 0 
    
    with app.app.app_context():
        #get all users
        allUsers = user.query.all()

        for i in range(0, len(allUsers)):
            User = allUsers[i]
            #query request table for last request made by the user
            lastRequest = apiRequest.query.filter_by(user_id=User.id).order_by(apiRequest.dateTime.desc()).first()

            #if user has made a request check how many days since the last request
            if lastRequest != None and (current-lastRequest.dateTime).days > purgeDays:
                db.session.delete(User)
                db.session.commit()
                count += 1

            #if user has never made a request use signup date
            else:
                if (current-User.dateJoined).days > purgeDays:
                    db.session.delete(User)
                    db.session.commit()
                    count += 1
    
    return count 


#get stats for the last day
def getStats(current, noRemoved):

    dayBefore = current - datetime.timedelta(days=1)

    with app.app.app_context():
        #query tables for stats
        #number users who have signed up in the last day
        newSignups = user.query.filter(db.between(user.dateJoined, dayBefore, current)).count()
        #total number of users remaining in the database
        remainingUsers = user.query.count()
        #number of users who have made a request in the last day
        activeUsers = apiRequest.query.distinct(apiRequest.user_id).filter(db.between(apiRequest.dateTime, dayBefore, current)).count()
        #total number of requests made in the past day
        totalRequests = apiRequest.query.filter(db.between(apiRequest.dateTime, dayBefore, current)).count()
        #number of requests that were rejected in the last day 
        rejectedRequests = apiRequest.query.filter(apiRequest.served==0).filter(db.between(apiRequest.dateTime, dayBefore, current)).count()
        

    print("\nDAILY SUMMARY: ")
    print("Users removed: {}".format(noRemoved))
    print("New signups: {}".format(newSignups))
    print("Remaining users: {}".format(remainingUsers))
    print("Active users: {}".format(activeUsers))
    print("Total requests: {}".format(totalRequests))
    print("Rejected requests: {}\n\n".format(rejectedRequests))


#get data when app first is run
@update.before_app_first_request
def activate_job():
    #get latest prices
    print('Getting Prices...')
    firstData = getPriceData()
    firstTime = firstData["Meta Data"]["4. Last Refreshed"]
    #predict based off these 

    time1 = datetime.datetime.utcnow()
    getPredictions(firstTime, firstData["Time Series FX (15min)"])
    time2 = datetime.datetime.utcnow()
    print("Predictions made and saved in: {} seconds\n".format((time2-time1).total_seconds()))

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
                atMidnight(current)

            if check:
                print("\nChecking for new prices...")
                newData = getPriceData()
                newTime = newData["Meta Data"]["4. Last Refreshed"]

                #if prices have updated, stop checking
                if dataTime != newTime:
                    print("Prices updated.")

                    #get predictions and time how long before they are retrei
                    time1 = datetime.datetime.utcnow()
                    getPredictions(newTime, newData["Time Series FX (15min)"])
                    time2 = datetime.datetime.utcnow()

                    print("Predictions made and saved in: {} seconds\n".format((time2-time1).total_seconds()))

                    check = False
                else:
                    print("Prices Not updated...\n")
                
                #another delay so the console doesn't get too congested
                time.sleep(30)
            
            #delay before checking the time again
            time.sleep(45)

    #create and start a new thread for the update function
    thread = threading.Thread(target=update)
    thread.start()

