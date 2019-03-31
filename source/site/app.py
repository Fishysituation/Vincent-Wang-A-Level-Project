"""
entry point for flask run
contains about and main page routes
"""


from flask import Flask, render_template, request, flash, redirect, url_for, Response, send_from_directory
from flask_migrate import Migrate

import datetime, time
import json, requests

from database import db
from config import Config

from api import api
from update import update


app = Flask(__name__)
app.config.from_object(Config)

#init the database
with app.app_context():
    db.init_app(app)

app.register_blueprint(api)
app.register_blueprint(update)

migrate = Migrate(app, db)


import models


jsonPath = 'static/json/'
predictionsFile = 'predictions.json'
alphaVantageDataFile = 'data.json'


#returns hh:mm time from datetime object
def getTime(datetime):
    time = str(datetime).split()[1]
    return time[:5]


#route for about page
@app.route("/about")
def about():
    return render_template("about.html")


#route for home page
@app.route("/")
def home():
    time = datetime.datetime.utcnow()
    timeString = getTime(time)

    weekendMessage = ""

    #check if market is closed because of the weekend
    if time.weekday() == 4 and time.hour > 21 or time.weekday() == 5 or time.weekday() == 6 and time.hour < 22:
        weekendMessage = "Market is currently closed for the weekend <br> - please check back at 10pm UTC on Sunday"


    #get the prices
    with open(jsonPath + alphaVantageDataFile) as f:
        data = json.load(f)
        dataTime = getTime(data["Meta Data"]["4. Last Refreshed"])

        timeLabels = []
        highPrices = []
        closePrices = []
        lowPrices = []

        #load in all prices to memory 
        for key, value in data["Time Series FX (15min)"].items():
            timeLabels.append(key.split()[1][:-3])
            highPrices.append(float(value['2. high']))
            closePrices.append(float(value['4. close']))
            lowPrices.append(float(value['3. low']))

        timeLabels.reverse()
        
        for i in range(1, 33):
            timeLabels.append('+' + str(i))

        #arrange data in chronological form 
        closePrices.reverse()
        highPrices.reverse()
        lowPrices.reverse()


    #load in predictions from the api json file 
    with open(jsonPath + predictionsFile) as f:
        data = json.load(f)

        predictions = [closePrices[-1]]
        for key, value in data["Predictions"].items():
            predictions.append(value)

        percentages = []
        for key, value in data["Meta Data"]["Recent Percentage Correct"].items():
            percentages.append(value)

        stDevs = [0]
        for key, value in data["Meta Data"]["Recent Standard Deviation Error"].items():
            stDevs.append(value)
    

    return render_template("home.html",
                        weekendMessage=weekendMessage,
                        timeNow=timeString, 
                        dataTime=dataTime, 
                        timeLabels=timeLabels,
                        highPrices=highPrices,
                        closePrices=closePrices,
                        lowPrices=lowPrices,
                        percentages=percentages,
                        stDevs=stDevs,
                        predictions=predictions)


if __name__ == "__main__":
    app.debug = False
    app.run()
