#!/usr/bin/env python

import flask
from flask import Response
import json
import sqlite3


# Create the application.
app = flask.Flask(__name__)


@app.route('/')
def index():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('index.html')
 

@app.route('/speakers')
def speakers():
    connection = sqlite3.connect("mydatabase.sqlite") 
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT(surname) FROM speaker;")
    speakers = cursor.fetchall()
    return flask.render_template('speaker.html', speakers=speakers)



if __name__ == '__main__':
    app.debug=True
    app.run()
