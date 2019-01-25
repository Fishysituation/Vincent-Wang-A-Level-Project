from flask import Flask
from datetime import datetime
import re

import sqlite3 as sql
databasePath = "database.db"

from flask import render_template, request, flash, redirect, url_for, Response

import random, string


app = Flask(__name__)
app.secret_key = "secret key"



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


@app.route("/")
def home():
    return render_template("home.html")


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
        pattern = re.compile("^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$")
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
            return app.send_static_file("sample.json")

        query = []
        with sql.connect(databasePath) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE apiKey = '%s'" % apiKey)
            query = cur.fetchall()
        

        if len(query) == 1:
            #send the sample file as a placeholder for now
            return app.send_static_file("sample.json")

    #if api key not provided/invalid, return "unauthorized" response code
    return Response("An api key is required", 401)


@app.route("/test")
def test():
    return render_template("test.html")
