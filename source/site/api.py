import random, string

from flask import render_template, request, flash, redirect, url_for, Response, send_from_directory, Blueprint

import datetime, time
import json, requests

import re

import sqlite3 as sql
databasePath = "database.db"

jsonPath = 'static/json/'

sampleFile = 'sample.json'
predictionsFile = 'predictions.json'
errorFile = 'invalidGet.json'

emailRegex = "^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)"


api = Blueprint('api', __name__, template_folder='templates')


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


@api.route("/api", methods=["GET", "POST"])
def apiHome():
   
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


@api.route("/show_api_key")
def showKey():
    key = request.args['key']
    return render_template("showKey.html", key=key)


@api.route("/api/data")
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

