from flask import Flask
import datetime

from flask import render_template, request, flash, redirect, url_for, Response, send_from_directory

import datetime, time
import json, requests

from api import api
from update import update

jsonPath = 'static/json/'
predictionsFile = 'predictions.json'
alphaVantageDataFile = 'data.json'

emailRegex = "^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$"

app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(update)

app.secret_key = "secret key"


#get predictions/price data before first request
#run all checks in the background
"""
app.before_first_request(update.activate_job())

app.route("/api", methods=["GET", "POST"])(api.api())
app.route("/show_api_key")(api.showKey())
app.route("/api/data")(api.returnData())
"""

@app.route("/test")
def test():
    return render_template("test.html")


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
