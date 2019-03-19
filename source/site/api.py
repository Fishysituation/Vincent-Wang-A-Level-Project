import random, string

from flask import render_template, request, flash, redirect, url_for, Response, send_from_directory, Blueprint

import datetime, time
import json, requests
import re
import hashlib

from app import db
from models import user, apiRequest


jsonPath = 'static/json/'

sampleFile = 'sample.json'
predictionsFile = 'predictions.json'
usageErrorFile = 'invalidGet.json'
errorFile = 'error.json'

emailRegex = "^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)"

api = Blueprint('api', __name__, template_folder='templates')

salt = 'OkRLWyqj'


def createKey():
    toReturn = ''
    #keep generating keys until a unique one is made

    while True:
        toReturn = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        User = user.query.filter_by(apiKey=toReturn).first()
        if User is None:
            break

    return toReturn


@api.route("/api", methods=["GET", "POST"])
def apiHome():
   
    if request.method == "GET": 
        return render_template("api.html")
    
    elif request.method == "POST":
        #if email already in use, reject
        #if email valid, give key to user and add email/key to database

        if request.form.get("isValid") != '1':
            return render_template("api.html")

        else:
            emailHash = request.form.get("email")
            User = user.query.filter_by(emailHash=emailHash).first()

            #if email was found
            if User is not None:
                flash("This email is already in use")
                flash("Your API key is: %s" % User.apiKey)
                return render_template("api.html")

            else:
                #generate random alphanumeric string
                apiKey = createKey()
                #get date in string yyyy-mm-dd format
                date = datetime.date.today()

                newUser = user(
                    emailHash = emailHash,
                    apiKey = apiKey,
                    dateJoined = date
                )

                try:
                    db.session.add(newUser)
                    db.session.commit()
                    return redirect(url_for('api.showKey', key=apiKey))

                except:
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

        try:
            User = user.query.filter_by(apiKey=apiKey).first()

            #if a valid get
            if User is not None:
                
                print("valid apikey")
                #setup flag
                serveRequest = False

                timeNow = datetime.datetime.utcnow()
                
                #get the last request from this user
                lastRequest = apiRequest.query.filter_by(user_id=User.id).order_by(apiRequest.dateTime.desc()).first()

                #if first request
                if lastRequest == None:
                    print("first request")
                    serveRequest = True

                elif (timeNow-lastRequest.dateTime).total_seconds() > 20:
                    print("request valid")
                    serveRequest = True
                
                #create a new request entry 
                Request = apiRequest(
                    dateTime = timeNow,
                    served = serveRequest,
                    user_id = User.id
                )

                db.session.add(Request)
                db.session.commit()

                if serveRequest:
                    return send_from_directory(jsonPath, predictionsFile)
            
        except: 
            #if requests too frequent, send an invalid response back
            return send_from_directory(jsonPath, errorFile)
        

    #if api key not/provided or is invalid, send an invalid response back
    return send_from_directory(jsonPath, usageErrorFile)

