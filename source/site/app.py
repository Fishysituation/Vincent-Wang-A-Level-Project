from flask import Flask
import datetime
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

purgeDays = 1


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



def savePredictions(time, predictions):
    #write predictions to database
    print("Saving Predictions")
    with sql.connect(databasePath) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO predictions (dateTime, pred15, pred30, pred60, pred120, pred240, pred480) VALUES ('{}','{}','{}', {}, {}, {}, {})".format(
            time, 
            predictions[0], 
            predictions[1], 
            predictions[2], 
            predictions[3], 
            predictions[4], 
            predictions[5])) 
        con.commit()


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


@app.before_first_request
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


def purge():
    #TODO yeet inactive users 
    #sqlite3 has own datetime functions on strings in correct format x 
    return


def createKey():
    toReturn = ''
    #keep generating keys until a unique one is made
    with sql.connect(databasePath) as con:
        cur = con.cursor()
        while True:
            toReturn = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            cur.execute("SELECT * FROM user WHERE apiKey = '{}'".format(toReturn))
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
                cur.execute("SELECT apiKey FROM user WHERE email = '{}'".format(email))
                query = cur.fetchall()

            #if email was found
            if len(query) > 0:
                flash("This email is already in use")
                flash("Your API key is: %s" % query[0][0])
                return render_template("api.html")

            else:
                #generate random alphanumeric string
                apiKey = createKey()
                #get date in string yyyy-mm-dd format
                date = datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
                try:
                    with sql.connect(databasePath) as con:
                        cur = con.cursor()
                        cur.execute("INSERT INTO user (email, apiKey, dateCreated) VALUES ('{}','{}','{}')".format(email, apiKey, date))
                        
                        con.commit()
                        return redirect(url_for('showKey', key=apiKey))

                except:
                    con.rollback()

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

        try:
            with sql.connect(databasePath) as con:

                cur = con.cursor()
                cur.execute("SELECT timeOfLastRequest FROM user WHERE apiKey = '{}'".format(apiKey))
                query = cur.fetchall()

                #if a valid get
                if len(query) == 1:
                    
                    print("valid apikey")

                    serveRequest = False
                    
                    #get datetime in string yyyy-mm-dd hh:mm:ss format
                    timeNow = datetime.datetime.utcnow()

                    requestString = query[0][0]

                    #if first request
                    if requestString == None:
                        print("first request")
                        serveRequest = True

                    else:
                        lastRequestTime = datetime.datetime.strptime(requestString, "%Y-%m-%d %H:%M:%S")
                        timeDelta = timeNow - lastRequestTime
                        
                        #if requests not too frequent
                        if timeDelta.total_seconds() > 20:
                            print("request valid")
                            serveRequest = True


                    #update the last attempted request
                    time = datetime.datetime.strftime(timeNow, "%Y-%m-%d %H:%M:%S")
                    cur.execute("UPDATE user SET timeOfLastRequest = '{}' WHERE apiKey = '{}'".format(time, apiKey))
                    con.commit()

                    if serveRequest:
                        return send_from_directory(jsonPath, predictionsFile)


        except:
            con.rollback()


    #if api key not/provided or is invalid, or error requests too frequent, send an invalid response back
    return send_from_directory(jsonPath, errorFile)


@app.route("/test")
def test():
    return render_template("test.html")



if __name__ == "__main__":
    app.debug = False
    app.run()
