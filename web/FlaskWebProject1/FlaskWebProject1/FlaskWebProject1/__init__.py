"""
The flask application package.
"""

from flask import Flask,request
from flask_cors import CORS, cross_origin

def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

app = Flask(__name__)
CORS(app)

app.after_request(after_request)

import FlaskWebProject1.views

