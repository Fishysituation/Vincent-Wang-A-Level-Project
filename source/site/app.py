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

app.register_blueprint(api)
app.register_blueprint(update)

db.init_app(app)
migrate = Migrate(app, db)


import models


jsonPath = 'static/json/'
predictionsFile = 'predictions.json'
alphaVantageDataFile = 'data.json'


def getTime(datetime):
    time = str(datetime).split()[1]
    return time[:5]


@app.route("/")
def home():
    time = getTime(datetime.datetime.utcnow())
    

    #TODO account for weekend closing so times don't get v confusing
    with open(jsonPath + alphaVantageDataFile) as f:
        data = json.load(f)
        dataTime = getTime(data["Meta Data"]["4. Last Refreshed"])

        timeLabels = []
        highPrices = []
        closePrices = []
        lowPrices = []
        for key, value in data["Time Series FX (15min)"].items():
            timeLabels.append(key.split()[1][:-3])
            highPrices.append(float(value['2. high']))
            closePrices.append(float(value['4. close']))
            lowPrices.append(float(value['3. low']))

        timeLabels.reverse()
        
        for i in range(1, 33):
            timeLabels.append('+' + str(i))

        closePrices.reverse()
        highPrices.reverse()
        lowPrices.reverse()


    with open(jsonPath + predictionsFile) as f:
        data = json.load(f)

        predictions = [closePrices[-1]]
        for key, value in data["Predictions"].items():
            predictions.append(value)

    #load in predictions from the api json file 
    #print(predictions)

    return render_template("home.html",
                        timeNow=time, 
                        dataTime=dataTime, 
                        timeLabels=timeLabels,
                        highPrices=highPrices,
                        closePrices=closePrices,
                        lowPrices=lowPrices,
                        predictions=predictions)


if __name__ == "__main__":
    app.debug = False
    app.run()
