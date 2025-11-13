import flask
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from lib import database


app = Flask(__name__)
CORS(app)
database.INIT()



if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
