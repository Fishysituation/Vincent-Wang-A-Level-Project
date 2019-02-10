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


#update data.json, return the time of the data sent
def getPriceData(): 
    api_url = alphaVantageURL + alphaVantageKey
    response = requests.get(api_url)

    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))

        for key in data.keys():
            #if error message returned
            if key == 'Error Message' or key == "Note:":
                print('API Call invalid...')
                print('Serving the last valid data file')

                with open(jsonPath + alphaVantageDataFile, 'r') as f:
                    data = json.load(f)
                    return data["Meta Data"]["4. Last Refreshed"]


        print("Get successful.")
        with open(jsonPath + alphaVantageDataFile, 'w') as f:
            json.dump(data, f, indent=4)
        return data["Meta Data"]["4. Last Refreshed"]



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



def getPredictions(time):
    #check if predictions have already been made for this time
    with open(jsonPath + predictionsFile, 'r') as f:
        data = json.load(f)
        predictionsTime = data["Meta Data"]["Time"]
    
    #if not, get new predictions and add a db entry
    if predictionsTime != time:
        print('Getting Predictions...')
        predictions = jsonPredictions.predict(time)
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
    firstTime = getPriceData()
    #predict based off these 
    getPredictions(firstTime)

    #run updates in the background
    def update():
        dataTime = getPriceData()
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
                newTime = getPriceData()

                #if prices have updated, stop checking
                if dataTime != newTime:
                    print("Prices updated.")
                    getPredictions(newTime)
                    check = False
                else:
                    print("Prices Not updated...")

            time.sleep(45)

    thread = threading.Thread(target=update)
    thread.start()
