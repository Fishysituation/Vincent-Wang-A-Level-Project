"""
all routes and functionality for the API
"""


import random, string

from flask import render_template, request, flash, redirect, url_for, Response, send_from_directory, Blueprint

import datetime, time
import json, requests

from app import db
from models import user, apiRequest


jsonPath = 'static/json/'

sampleFile = 'sample.json'
predictionsFile = 'predictions.json'
usageErrorFile = 'invalidGet.json'
errorFile = 'error.json'

api = Blueprint('api', __name__, template_folder='templates')


#generate a random 
def createKey():
    toReturn = ''
    #keep generating keys until a unique one is made

    while True:
        toReturn = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        User = user.query.filter_by(apiKey=toReturn).first()
        if User is None:
            break

    return toReturn


#route for api page
@api.route("/api", methods=["GET", "POST"])
def apiHome():
   
    if request.method == "GET": 
        return render_template("api.html")
    
    elif request.method == "POST":
        #if email already in use, reject
        #if email valid, give key to user and add email/key to database

        #if email entered was invalid, return to api main page
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

                #try to add user entry to database
                try:
                    db.session.add(newUser)
                    db.session.commit()
                    return redirect(url_for('api.showKey', key=apiKey))

                except:
                    flash("There was an error, please try again...")
                    return render_template("api.html")


#route for showing api key when valid email is entered
@api.route("/show_api_key")
def showKey():
    key = request.args['key']
    return render_template("showKey.html", key=key)


#route for api requests
@api.route("/api/data")
def returnData():
    #if an api key is provided
    if 'apikey' in request.args:
        apiKey = request.args['apikey']
        
        #if the example get request
        if apiKey == 'testKey':
            return send_from_directory(jsonPath, sampleFile)

        try:
            #get the last most recent user/apiRequest datetime where the user's apikey is equal to the one entered
            User = db.session.query(user, apiRequest.dateTime).outerjoin(apiRequest, user.id == apiRequest.user_id).filter(user.apiKey == apiKey).order_by(apiRequest.dateTime.desc()).first()

            #if a valid get
            if User is not None:
                
                #setup flag
                serveRequest = False

                timeNow = datetime.datetime.utcnow()

                #if no datetime was returned
                if User[1] == None:
                    serveRequest = True

                elif (timeNow-User[1]).total_seconds() > 20:
                    serveRequest = True
                
                #create a new request entry 
                Request = apiRequest(
                    dateTime = timeNow,
                    served = serveRequest,
                    user_id = User[0].id
                )

                db.session.add(Request)
                db.session.commit()

                if serveRequest:
                    return send_from_directory(jsonPath, predictionsFile)

        except: 
            #if error in querying/writing to database send an error file back
            return send_from_directory(jsonPath, errorFile)
        

    #if api key not/provided or is invalid, send an invalid response back
    return send_from_directory(jsonPath, usageErrorFile)

