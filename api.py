#!/usr/bin/python
# -*- coding: utf-8 -*-

import mysql.connector
import datetime
import jwt
import time
from flask import abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask import Flask, request, jsonify

# API

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address,
                  default_limits=['20000 per day', '5000 per hour',
                  '50 per minute'])

# GLOBAL VARIABLES

now = datetime.datetime.now()
mydb = mysql.connector.connect(host='localhost', user='root', passwd=''
                               , database='mybase')
mycursor = mydb.cursor()


# USER ROUTES  ----------------------------

# SEE ONE USER

@app.route('/seeuser/<id>', methods=['GET'])
def seeuser(id):
    try:
        try:
            val = int(id)
        except:
            return (jsonify('Invalid id'), 401)
        sql = 'SELECT * FROM users WHERE id = ' + id
        try:
            mycursor.execute(sql)
        except:
            return (jsonify('Failed'), 500)
        myresult = mycursor.fetchall()
        return jsonify(myresult[0])
    except:
        return (jsonify('Sory, Failed'), 500)


# DOWN USER

@app.route('/downuser/<id>', methods=['GET'])
def downuser(id):
    try:
        val = int(id)
    except:
        return (jsonify('Invalid id'), 401)
    sql = 'UPDATE users set enabled = 0, updated_at="' \
        + now.isoformat() + '" WHERE id = ' + id
    try:
        mycursor.execute(sql)
    except:
        return (jsonify('Failed'), 500)
    return (jsonify('User down'), 200)


# UP USER

@app.route('/upuser/<id>', methods=['GET'])
def upuser(id):
    try:
        val = int(id)
    except:
        return (jsonify('Invalid id'), 401)
    sql = 'UPDATE users set enabled = 1, updated_at="' \
        + now.isoformat() + '" WHERE id = ' + id
    try:
        mycursor.execute(sql)
    except:
        return (jsonify('Failed'), 500)
    return (jsonify('User up'), 200)


# LOGIN USER

@app.route('/login', methods=['POST'])
def login():
    try:
        sql = 'SELECT * FROM users WHERE mail="' + request.json['mail'] \
            + '" AND pwd="' + request.json['pwd'] + '"'
        try:
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
        except:
            return (jsonify('Sorry, failed.'), 500)
        if myresult == []:
            return (jsonify('Login failed. Please check data.'), 400)
        ttl = int(time.time()) + 25000
        token = generateToken(request.json['mail'], request.json['pwd'],
                          ttl)
        sql = 'UPDATE users SET token = "' \
            + token + '" WHERE mail = "' \
            + request.json['mail'] + '"'
        try:
            mycursor.execute(sql)
            mydb.commit()
        except:
            return (jsonify('Sorry, failed.'), 500)
        json = {'mail': request.json['mail'], 'token': token}
        return (jsonify(json), 200)
    except:
        return (jsonify('Sorry, failed.'), 500)


# REGISTER USER

@app.route('/register', methods=['POST'])
def register():
    try:
        ttl = time.time() + 250000
        token = generateToken(request.json['mail'], request.json['pwd'],
                          ttl)
        sql = \
            'INSERT INTO users (mail,pwd,name,surname,tel,token,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        val = (
        request.json['mail'],
        request.json['pwd'],
        request.json['name'],
        request.json['surname'],
        request.json['tel'],
        token,
        now.isoformat(),
        )
        try:
            mycursor.execute(sql, val)
            mydb.commit()
        except:
            return (jsonify('Failed'), 500)
        json = {'mail': request.json['mail'], 'token': token}
        return (jsonify(json), 200)
    except:
        return (jsonify('Sory, error.'), 500)


# UPDATE USER

@app.route('/update', methods=['PUT'])
def update():
    try:
        sql = 'UPDATE users SET pwd ="' + request.json['pwd'] \
            + '", updated_at="' + now.isoformat() + '", name="' \
            + request.json['name'] + '", surname="' + request.json['surname'
                ] + '", tel="' + request.json['tel'] + '" WHERE id = "' \
            + request.json['id'] + '"'
        try:
            mycursor.execute(sql)
            mydb.commit()
        except:
            return (jsonify('Failed'), 500)
        return (jsonify('Updated'), 200)
    except:
        return (jsonify('Failed'), 500)


# GET ALL USERS

@app.route('/getusers', methods=['GET'])
def getusers():
    mycursor.execute('SELECT * FROM users')
    myresult = mycursor.fetchall()
    return jsonify(myresult)


# -------------------------------------

# TEST MIDDLEWARE

@app.route('/testtoken', methods=['POST'])
def untoken():
    res = middleware(request.headers.get('token'))
    if res == '0':
        return (jsonify('Forbidden'), 400)
    return (jsonify('OK'), 200)


# GENERATE TOKEN

def generateToken(mail, pwd, time):
    encoded = jwt.encode({'mail': mail, 'pwd': pwd, 'time': time},
                         '011WER432ETTI7887YT655ET688EUUY78',
                         algorithm='HS256')
    return encoded


# MIDDLEWARE

def middleware(token):
    try:
        decoded = jwt.decode(token, '011WER432ETTI7887YT655ET688EUUY78'
                             , algorithm='HS256')
    except:
        return '0'
    if decoded['time'] < int(time.time()):
        return '0'
    return '1'


# -------------------------------------

if __name__ == '__main__':
    app.run(debug=True)


			
			