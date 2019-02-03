from flask import Flask
from datetime import datetime
import re

import sqlite3 as sql
databasePath = "database.db"

from flask import render_template, request, flash, redirect, url_for, Response, send_from_directory

import random, string
import datetime, threading, time
import json, requests

import jsonPredictions

jsonPath = 'static/json/'

sampleFile = 'sample.json'
predictionsFile = 'predictions.json'
errorFile = 'invalidGet.json'

alphaVantageDataFile = 'data.json'
alphaVantageKey = "2XFPRGYPL0RM2GQ8"
alphaVantageURL = "https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=15min&outputsize=compact&apikey="

emailRegex = "^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$"

app = Flask(__name__)
app.secret_key = "secret key"


#update data.json, return the time of the data sent
def getPriceData(): 
    api_url = alphaVantageURL + alphaVantageKey
    response = requests.get(api_url)

    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))

        valid = True 
        for key in data.keys():
            #if error message returned
            if key == 'Error Message':
                print('API Call invalid...')
                print('Serving the last valid data file')
                valid = False

        if valid:
            print("Get successful.")
            with open(jsonPath + alphaVantageDataFile, 'w') as f:
                json.dump(data, f, indent=4)
            return data["Meta Data"]["4. Last Refreshed"]

        else: 
            return None


@app.before_first_request
def activate_job():

    #get latest prices
    print('Getting Prices...')
    firstTime = getPriceData()
    #predict based off these 
    print('Getting Predictions...')
    jsonPredictions.predict(firstTime)
    print('Done.')

    #run update in the background
    def update():
        dataTime = getPriceData()
        check = False
        
        while True:
            
            current = datetime.datetime.utcnow()
            
            if current.minute % 15 == 0: 
                check = True 
            
            if check:
                print("Checking for new prices...")
                newTime = getPriceData()
                #if prices have updated, stop checking
                if dataTime != newTime:
                    print("Prices updated.")
                    print("Getting Predictions")
                    jsonPredictions.predict(newTime)
                    print("Predictions done")
                    check = False
                else:
                    print("Prices Not updated...")

            time.sleep(45)

    thread = threading.Thread(target=update)
    thread.start()


def createKey():
    toReturn = ''
    #keep generating keys until a unique one is made
    with sql.connect(databasePath) as con:
        cur = con.cursor()
        while True:
            toReturn = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            cur.execute("SELECT * FROM user WHERE apiKey='%s'" %toReturn)
            if len(cur.fetchall()) == 0:
                break
    return toReturn


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
        
        for i in range(1, 17):
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
    print(predictions)

    return render_template("home.html",
                        timeNow=time, 
                        dataTime=dataTime, 
                        timeLabels=timeLabels,
                        highPrices=highPrices,
                        closePrices=closePrices,
                        lowPrices=lowPrices,
                        predictions=predictions)


@app.route("/api", methods=["GET", "POST"])
def api():
   
    if request.method == "GET":
        return render_template("api.html")
    
    elif request.method == "POST":
        #if email invalid, reject
        #if email already in use, reject
        #if email valid, give key to user and add email/key to database

        email = request.form.get("email")
        
        #check if email pattern is valid
        pattern = re.compile(emailRegex)
        result = pattern.match(email)

        #re.match objects are always None if no match
        if result == None:
            flash("Email is invalid, please try again...")
            return render_template("api.html")

        else:
            query = []
            #see if email is already in use
            with sql.connect(databasePath) as con:
                cur = con.cursor()
                cur.execute("SELECT apiKey FROM user WHERE email = '%s'" % email)
                query = cur.fetchall()

            #if email was found
            if len(query) > 0:
                flash("This email is already in use")
                flash("Your API key is: %s" % query[0][0])
                return render_template("api.html")

            else:
                apiKey = createKey()

                try:
                    with sql.connect(databasePath) as con:
                        cur = con.cursor()
                        cur.execute("INSERT INTO user (email, apiKey) VALUES (?,?)",(email, apiKey))
                        
                        con.commit()
                        #msg = "Record successfully added"
                        return redirect(url_for('showKey', key=apiKey))

                except:
                    con.rollback()
                    #msg = "error in insert operation"

                flash("There was an error, please try again...")
                return render_template("api.html")


@app.route("/show_api_key")
def showKey():
    key = request.args['key']
    return render_template("showKey.html", key=key)


@app.route("/api/data")
def returnData():
    #if an api key is provided
    if 'apikey' in request.args:
        apiKey = request.args['apikey']
        
        #if the example get request
        if apiKey == 'testKey':
            return send_from_directory(jsonPath, sampleFile)

        query = []
        with sql.connect(databasePath) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE apiKey = '%s'" % apiKey)
            query = cur.fetchall()
        
        #if a valid get
        if len(query) == 1:
            #send the sample file as a placeholder for now
            return send_from_directory(jsonPath, predictionsFile)

        else: 
            return send_from_directory(jsonPath, errorFile)

    #if api key not provided/invalid, return "unauthorized" response code
    return send_from_directory(jsonPath, errorFile)


@app.route("/test")
def test():
    return render_template("test.html")



if __name__ == "__main__":
    app.debug = False
    app.run()
